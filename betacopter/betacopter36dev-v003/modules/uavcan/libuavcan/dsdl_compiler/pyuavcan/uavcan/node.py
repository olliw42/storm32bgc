#encoding=utf-8

import time
import math
import ctypes
import struct
import logging
import binascii
import functools
import collections

import uavcan
import uavcan.dsdl as dsdl
import uavcan.driver as driver
import uavcan.transport as transport


NODE_STATUS_INVERVAL = 0.5


class Node(object):
    def __init__(self, handlers, node_id=127):
        self.can = None
        self.transfer_manager = transport.TransferManager()
        self.handlers = handlers
        self.node_id = node_id
        self.outstanding_requests = {}
        self.outstanding_request_callbacks = {}
        self.outstanding_request_timestamps = {}
        self.outstanding_request_retries = {}
        self.next_transfer_ids = collections.defaultdict(int)
        self.node_info = {}

    def _recv_frame(self, dev, message):
        frame_id, frame_data, ext_id = message
        if not ext_id:
            return

        frame = transport.Frame(frame_id, frame_data)
        # logging.debug("Node._recv_frame(): got {0!s}".format(frame))

        transfer_frames = self.transfer_manager.receive_frame(frame)
        if not transfer_frames:
            return

        transfer = transport.Transfer()
        transfer.from_frames(transfer_frames)

        logging.debug("Node._recv_frame(): received {0!r}".format(transfer))

        # If it's a node info request, keep track of the status of each node
        if transfer.payload.type == uavcan.protocol.NodeStatus:
            self.node_info[transfer.source_node_id] = {
                "uptime": transfer.payload.uptime_sec,
                "health": transfer.payload.health,
                "mode": transfer.payload.mode,
                "sub_mode": transfer.payload.sub_mode,
                "vendor_specific_status_code":
                    transfer.payload.vendor_specific_status_code,
                "timestamp": time.time()
            }

        if (transfer.service_not_message and not
                transfer.request_not_response) and \
                transfer.dest_node_id == self.node_id:
            # This is a reply to a request we sent. Look up the original
            # request and call the appropriate callback
            requests = self.outstanding_requests.keys()
            for key in requests:
                if transfer.is_response_to(self.outstanding_requests[key]):
                    # Call the request's callback and remove it from the
                    # active list
                    self.outstanding_request_callbacks[key](transfer.payload,
                                                            transfer)
                    del self.outstanding_requests[key]
                    del self.outstanding_request_callbacks[key]
                    del self.outstanding_request_timestamps[key]
                    del self.outstanding_request_retries[key]
                    break
        elif not transfer.service_not_message or \
                transfer.dest_node_id == self.node_id:
            # This is a request, a unicast or a broadcast; look up the
            # appropriate handler by data type ID
            for handler in self.handlers:
                if handler[0] == transfer.payload.type:
                    kwargs = handler[2] if len(handler) == 3 else {}
                    h = handler[1](transfer.payload, transfer, self, **kwargs)
                    h._execute()

    def _next_transfer_id(self, key):
        transfer_id = self.next_transfer_ids[key]
        self.next_transfer_ids[key] = (transfer_id + 1) & 0x1F
        return transfer_id

    def listen(self, device, baudrate=1000000, io_loop=None):
        if device.startswith("/dev"):
            self.can = driver.SLCAN(device, baudrate=baudrate)
        else:
            self.can = driver.SocketCAN(device)

        self.can.open()

        # Send node status every 0.5 sec
        self.start_time = time.time()
        # TODO: make it easier to get constant values from UAVCAN types
        self.health = uavcan.protocol.NodeStatus().HEALTH_OK
        self.mode = uavcan.protocol.NodeStatus().MODE_OPERATIONAL

        if io_loop:
            # Run asynchronously on a Tornado ioloop
            import tornado.ioloop

            self.can.add_to_ioloop(io_loop, callback=self._recv_frame)
            self.nodestatus_timer = tornado.ioloop.PeriodicCallback(
                self.send_node_status,
                NODE_STATUS_INVERVAL * 1000.0, io_loop=io_loop)
            self.nodestatus_timer.start()
        else:
            # Run synchronously
            last_status_t = time.time()
            while True:
                messages = can._recv()

                if messages:
                    for message in messages:
                        self._recv_frame(self.can, message)

                if time.time() - last_status_t > NODE_STATUS_INVERVAL:
                    self.send_node_status()
                    last_status_t = time.time()

    def send_node_status(self):
        # Expire any requests more than one second old
        requests = self.outstanding_requests.keys()
        for key in requests:
            if time.time() - self.outstanding_request_timestamps[key] > 1.0:
                # Retry the request, or time it out if there are no retries
                # remaining
                if self.outstanding_request_retries[key]:
                    self.outstanding_request_retries[key] -= 1
                    self.outstanding_request_timestamps[key] = time.time()

                    for frame in self.outstanding_requests[key].to_frames():
                        self.can.send(frame.message_id, frame.bytes,
                                      extended=True)
                else:
                    self.outstanding_request_callbacks[key](None, None)

                    del self.outstanding_requests[key]
                    del self.outstanding_request_callbacks[key]
                    del self.outstanding_request_timestamps[key]
                    del self.outstanding_request_retries[key]

        # Send the node status message
        status = uavcan.protocol.NodeStatus()
        status.uptime_sec = int(time.time() - self.start_time)
        status.health = self.health
        status.mode = self.mode
        status.sub_mode = 0
        status.vendor_specific_status_code = 0
        self.send_message(status)

    def send_request(self, payload, dest_node_id=None, callback=None):
        transfer_id = self._next_transfer_id((payload.type.default_dtid,
                                              dest_node_id))
        transfer = transport.Transfer(
            payload=payload,
            source_node_id=self.node_id,
            dest_node_id=dest_node_id,
            transfer_id=transfer_id,
            service_not_message=True,
            request_not_response=True)

        for frame in transfer.to_frames():
            self.can.send(frame.message_id, frame.bytes, extended=True)

        if callback:
            self.outstanding_requests[transfer.key] = transfer
            self.outstanding_request_callbacks[transfer.key] = callback
            self.outstanding_request_timestamps[transfer.key] = time.time()
            self.outstanding_request_retries[transfer.key] = 3

        logging.debug(
            "Node.send_request(dest_node_id={0:d}): sent {1!r}".format(
            dest_node_id, payload))

    def send_message(self, payload):
        transfer_id = self._next_transfer_id(payload.type.default_dtid)
        transfer = transport.Transfer(
            payload=payload,
            source_node_id=self.node_id,
            transfer_id=transfer_id,
            service_not_message=False)

        for frame in transfer.to_frames():
            self.can.send(frame.message_id, frame.bytes, extended=True)

        logging.debug("Node.send_message(): sent {0!r}".format(payload))


class Monitor(object):
    def __init__(self, payload, transfer, node, *args, **kwargs):
        self.message = payload
        self.transfer = transfer
        self.node = node

    def _execute(self):
        self.on_message(self.message)

    def on_message(self, message):
        pass


class Service(Monitor):
    def __init__(self, *args, **kwargs):
        super(Service, self).__init__(*args, **kwargs)
        self.request = self.message
        self.response = transport.CompoundValue(self.request.type, tao=True,
                                                mode="response")

    def _execute(self):
        result = self.on_request()

        # Send the response transfer
        transfer = transport.Transfer(
            payload=self.response,
            source_node_id=self.node.node_id,
            dest_node_id=self.transfer.source_node_id,
            transfer_id=self.transfer.transfer_id,
            transfer_priority=self.transfer.transfer_priority,
            service_not_message=True,
            request_not_response=False
        )
        for frame in transfer.to_frames():
            self.node.can.send(frame.message_id, frame.bytes,
                               extended=True)

        logging.debug(
            "ServiceHandler._execute(dest_node_id={0:d}): sent {1!r}".format(
            self.transfer.source_node_id, self.response))

    def on_request(self):
        pass
