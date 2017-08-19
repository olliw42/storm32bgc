import os
import time
import logging
import collections

import uavcan
import uavcan.node


class NodeStatusMonitor(uavcan.node.Monitor):
    NODE_INFO = {}
    NODE_STATUS = {}
    NODE_TIMESTAMP = collections.defaultdict(float)
    TIMEOUT = 30.0

    def __init__(self, *args, **kwargs):
        super(NodeStatusMonitor, self).__init__(*args, **kwargs)
        self.new_node_callback = kwargs.get("new_node_callback", None)

    def on_message(self, message):
        node_id = self.transfer.source_node_id
        last_timestamp = NodeStatusMonitor.NODE_TIMESTAMP[node_id]
        last_node_uptime = NodeStatusMonitor.NODE_STATUS[node_id].uptime_sec \
                           if node_id in NodeStatusMonitor.NODE_STATUS else 0

        # Update the node status registry
        NodeStatusMonitor.NODE_STATUS[node_id] = message
        NodeStatusMonitor.NODE_TIMESTAMP[node_id] = time.time()

        if time.time() - last_timestamp > NodeStatusMonitor.TIMEOUT or \
                message.uptime_sec < last_node_uptime:
            # The node has timed out, hasn't been seen before, or has
            # restarted, so get the node's hardware and software info
            request = uavcan.protocol.GetNodeInfo(mode="request")
            self.node.send_request(request, node_id,
                                   callback=self.on_nodeinfo_response)

    def on_nodeinfo_response(self, response, transfer):
        if not response or not transfer:
            return

        NodeStatusMonitor.NODE_INFO[transfer.source_node_id] = response

        hw_unique_id = "".join(format(c, "02X") for c in
                               response.hardware_version.unique_id)
        msg = (
            "[#{0:03d}:uavcan.protocol.GetNodeInfo] " +
            "software_version.major={1:d} " +
            "software_version.minor={2:d} " +
            "software_version.vcs_commit={3:08x} " +
            "software_version.image_crc={4:016X} " +
            "hardware_version.major={5:d} " +
            "hardware_version.minor={6:d} " +
            "hardware_version.unique_id={7!s} " +
            "name={8!r}"
        ).format(
            transfer.source_node_id,
            response.software_version.major,
            response.software_version.minor,
            response.software_version.vcs_commit,
            response.software_version.image_crc,
            response.hardware_version.major,
            response.hardware_version.minor,
            hw_unique_id,
            response.name.decode()
        )
        logging.info(msg)

        # If a new-node callback is defined, call it now
        if self.new_node_callback:
            self.new_node_callback(self.node, transfer.source_node_id,
                                   response)


class DynamicNodeIDServer(uavcan.node.Monitor):
    ALLOCATION = {}
    QUERY = ""

    def __init__(self, *args, **kwargs):
        super(DynamicNodeIDServer, self).__init__(*args, **kwargs)
        self.dynamic_id_range = kwargs.get("dynamic_id_range", (1, 127))

    def on_message(self, message):
        if message.first_part_of_unique_id:
            # First-phase messages trigger a second-phase query
            DynamicNodeIDServer.QUERY = message.unique_id.to_bytes()

            response = uavcan.protocol.dynamic_node_id.Allocation()
            response.first_part_of_unique_id = 0
            response.node_id = 0
            response.unique_id.from_bytes(DynamicNodeIDServer.QUERY)
            self.node.send_message(response)

            logging.debug(("[MASTER] Got first-stage dynamic ID request " +
                           "for {0!r}").format(DynamicNodeIDServer.QUERY))
        elif len(message.unique_id) == 6 and \
                len(DynamicNodeIDServer.QUERY) == 6:
            # Second-phase messages trigger a third-phase query
            DynamicNodeIDServer.QUERY += message.unique_id.to_bytes()

            response = uavcan.protocol.dynamic_node_id.Allocation()
            response.first_part_of_unique_id = 0
            response.node_id = 0
            response.unique_id.from_bytes(DynamicNodeIDServer.QUERY)
            self.node.send_message(response)
            logging.debug(("[MASTER] Got second-stage dynamic ID request " +
                           "for {0!r}").format(DynamicNodeIDServer.QUERY))
        elif len(message.unique_id) == 4 and \
                len(DynamicNodeIDServer.QUERY) == 12:
            # Third-phase messages trigger an allocation
            DynamicNodeIDServer.QUERY += message.unique_id.to_bytes()

            logging.debug(("[MASTER] Got third-stage dynamic ID request " +
                           "for {0!r}").format(DynamicNodeIDServer.QUERY))

            node_requested_id = message.node_id
            node_allocated_id = None

            allocated_node_ids = \
                set(DynamicNodeIDServer.ALLOCATION.itervalues()) | \
                set(NodeStatusMonitor.NODE_STATUS.iterkeys())
            allocated_node_ids.add(self.node.node_id)

            # If we've already allocated a node ID to this device, return the
            # same one
            if DynamicNodeIDServer.QUERY in DynamicNodeIDServer.ALLOCATION:
                node_allocated_id = DynamicNodeIDServer.ALLOCATION[
                    DynamicNodeIDServer.QUERY]

            # If an ID was requested but not allocated yet, allocate the first
            # ID equal to or higher than the one that was requested
            if node_requested_id and not node_allocated_id:
                for node_id in xrange(node_requested_id,
                                      self.dynamic_id_range[1]):
                    if node_id not in allocated_node_ids:
                        node_allocated_id = node_id
                        break

            # If no ID was allocated in the above step (also if the requested
            # ID was zero), allocate the highest unallocated node ID
            if not node_allocated_id:
                for node_id in xrange(self.dynamic_id_range[1],
                                      self.dynamic_id_range[0], -1):
                    if node_id not in allocated_node_ids:
                        node_allocated_id = node_id
                        break

            DynamicNodeIDServer.ALLOCATION[DynamicNodeIDServer.QUERY] = \
                node_allocated_id

            if node_allocated_id:
                response = uavcan.protocol.dynamic_node_id.Allocation()
                response.first_part_of_unique_id = 0
                response.node_id = node_allocated_id
                response.unique_id.from_bytes(
                    DynamicNodeIDServer.QUERY)
                self.node.send_message(response)
                logging.info(("[MASTER] Allocated node ID #{0:03d} to node " +
                              "with unique ID {1!r}").format(
                              node_allocated_id, DynamicNodeIDServer.QUERY))
            else:
                logging.error("[MASTER] Couldn't allocate dynamic node ID")
        else:
            # Received mis-sequenced reply, clear out the state
            DynamicNodeIDServer.QUERY = ""
            logging.error("[MASTER] Got mis-sequenced reply, resetting query")


class DebugLogMessageMonitor(uavcan.node.Monitor):
    def on_message(self, message):
        logmsg = "DebugLogMessageMonitor [#{0:03d}:{1}] {2}".format(
            self.transfer.source_node_id, message.source.decode(),
            message.text.decode())
        (logging.debug, logging.info,
            logging.warning, logging.error)[message.level.value](logmsg)
