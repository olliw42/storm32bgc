#encoding=utf-8

import os
import sys
import time
import fcntl
import socket
import struct
import logging
import binascii
import functools


# If PySerial isn't available, we can't support SLCAN
try:
    import serial
except ImportError:
    serial = None
    logging.info("uavcan.driver cannot import PySerial; SLCAN will not be "
                 "available.")


# Python 3.3+'s socket module has support for SocketCAN when running on Linux.
# Use that if possible; otherwise
try:
    socket.CAN_RAW
    def get_socket(ifname):
        s = socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
        s.bind((ifname, ))
        s.setblocking(0)
        return s

except Exception:
    import ctypes
    import ctypes.util
    libc = ctypes.CDLL(ctypes.util.find_library("c"))

    # from linux/can.h
    CAN_RAW = 1

    # from linux/socket.h
    AF_CAN = 29
    SO_TIMESTAMP = 29

    from socket import SOL_SOCKET

    SOL_CAN_BASE            = 100
    SOL_CAN_RAW             = SOL_CAN_BASE + CAN_RAW
    CAN_RAW_FILTER          = 1     # set 0 .. n can_filter(s)
    CAN_RAW_ERR_FILTER      = 2     # set filter for error frames
    CAN_RAW_LOOPBACK        = 3     # local loopback (default:on)
    CAN_RAW_RECV_OWN_MSGS   = 4     # receive my own msgs (default:off)
    CAN_RAW_FD_FRAMES       = 5     # allow CAN FD frames (default:off)

    class sockaddr_can(ctypes.Structure):
        """
        typedef __u32 canid_t;
        struct sockaddr_can {
            sa_family_t can_family;
            int         can_ifindex;
            union {
                struct { canid_t rx_id, tx_id; } tp;
            } can_addr;
        };
        """
        _fields_ = [
            ("can_family", ctypes.c_uint16),
            ("can_ifindex", ctypes.c_int),
            ("can_addr_tp_rx_id", ctypes.c_uint32),
            ("can_addr_tp_tx_id", ctypes.c_uint32)
        ]

    class can_frame(ctypes.Structure):
        """
        typedef __u32 canid_t;
        struct can_frame {
            canid_t can_id;
            __u8    can_dlc;
            __u8    data[8] __attribute__((aligned(8)));
        };
        """
        _fields_ = [
            ("can_id", ctypes.c_uint32),
            ("can_dlc", ctypes.c_uint8),
            ("_pad", ctypes.c_ubyte * 3),
            ("data", ctypes.c_uint8 * 8)
        ]

    class CANSocket(object):
        def __init__(self, fd):
            self.fd = fd

        def recv(self, bufsize, flags=None):
            frame = can_frame()
            nbytes = libc.read(self.fd, ctypes.byref(frame),
                               sys.getsizeof(frame))
            return ctypes.string_at(ctypes.byref(frame),
                                    ctypes.sizeof(frame))[0:nbytes]

        def send(self, data, flags=None):
            frame = can_frame()
            ctypes.memmove(ctypes.byref(frame), data,
                           ctypes.sizeof(frame))
            return libc.write(self.fd, ctypes.byref(frame),
                              ctypes.sizeof(frame))

        def fileno(self):
            return self.fd

        def close(self):
            libc.close(self.fd)

    def get_socket(ifname):
        on = ctypes.c_int(1)
        off = ctypes.c_int(1)
        socket_fd = libc.socket(AF_CAN, socket.SOCK_RAW, CAN_RAW)
        libc.fcntl(socket_fd, fcntl.F_SETFL, os.O_NONBLOCK)
        error = libc.setsockopt(socket_fd, SOL_SOCKET, SO_TIMESTAMP,
                                ctypes.byref(on), ctypes.sizeof(on))
        # error = libc.setsockopt(socket_fd, SOL_CAN_RAW, CAN_RAW_RECV_OWN_MSGS,
        #                         ctypes.byref(off), ctypes.sizeof(off))
        ifidx = libc.if_nametoindex(ifname)
        addr = sockaddr_can(AF_CAN, ifidx)
        error = libc.bind(socket_fd, ctypes.byref(addr), ctypes.sizeof(addr))
        return CANSocket(socket_fd)


# from linux/can.h
CAN_EFF_FLAG = 0x80000000
CAN_EFF_MASK = 0x1FFFFFFF


class SocketCAN(object):
    def __init__(self, interface):
        self.interface = interface
        self.socket = None

    def _read(self, fd, events, callback=None):
        messages = []
        packet = self.socket.recv(16)
        while len(packet) == 16:
            can_id, can_dlc, can_data = \
                struct.unpack("=IB3x8s", packet)
            message = (can_id & CAN_EFF_MASK, can_data[0:can_dlc],
                       True if (can_id & CAN_EFF_FLAG) else False)
            messages.append(message)

            try:
                packet = self.socket.recv(16)
            except Exception:
                break

        if callback:
            for message in messages:
                logging.debug("CAN.recv(): {!r} data:{}".format(
                              message, binascii.hexlify(message[1])))
                try:
                    callback(self, message)
                except Exception:
                    raise
        else:
            for message in messages:
                logging.debug("CAN.recv(): {!r} data:{}".format(
                              message, binascii.hexlify(message[1])))
            return messages

    def _recv(self, callback=None):
        return self._read(0, None, callback)

    def add_to_ioloop(self, ioloop, callback=None):
        ioloop.add_handler(
            self.socket.fileno(),
            functools.partial(self._read, callback=callback),
            ioloop.READ)

    def open(self, callback=None):
        self.socket = get_socket(self.interface)

    def close(self, callback=None):
        self.socket.close()

    def send(self, message_id, message, extended=False):
        logging.debug("CAN.send({!r}, {!r}, {!r})".format(
                      message_id, binascii.hexlify(message), extended))

        message_pad = bytes(message) + b"\x00" * (8 - len(message))
        self.socket.send(struct.pack("=IB3x8s", message_id | CAN_EFF_FLAG,
                                     len(message), message_pad))


class SLCAN(object):
    def __init__(self, device, baudrate=1000000):
        if not serial:
            raise RuntimeError(
                "PySerial not imported; SLCAN is not available")

        self.conn = serial.Serial(device, 3000000, timeout=0)
        self._read_handler = self._get_bytes_sync
        self.partial_message = ""
        self.baudrate = baudrate

    def _get_bytes_sync(self):
        return self.conn.read(1)

    def _get_bytes_async(self):
        return os.read(self.conn.fd, 1024)

    def _ioloop_event_handler(self, fd, events, callback=None):
        self._recv(callback=callback)

    def _parse(self, message):
        try:
            if message[0] == "T":
                id_len = 8
            else:
                id_len = 3

            # Parse the message into a (message ID, data) tuple.
            packet_id = int(message[1:1 + id_len], 16)
            packet_len = int(message[1 + id_len])
            packet_data = binascii.a2b_hex(
                message[2 + id_len:2 + id_len + packet_len * 2])

            # ID, data, extended
            return packet_id, packet_data, (id_len == 8)
        except Exception:
            return None

    def _recv(self, callback=None):
        bytes = ""
        new_bytes = self._read_handler()
        while new_bytes:
            bytes += new_bytes
            new_bytes = self._read_handler()

        if not bytes:
            if callback:
                return
            else:
                return []

        # Split into messages
        messages = [self.partial_message]
        for byte in bytes:
            if byte in "tT":
                messages.append(byte)
            elif messages and byte in "0123456789ABCDEF":
                messages[-1] += byte
            elif byte in "\x07\r":
                messages.append("")

        if messages[-1]:
            self.partial_message = messages.pop()
        # Filter, parse and return the messages
        messages = list(self._parse(m) for m in messages
                        if m and m[0] in ("t", "T"))
        messages = filter(lambda x: x and x[0], messages)

        if callback:
            for message in messages:
                #logging.debug("CAN.recv(): {!r}".format(message))
                try:
                    callback(self, message)
                except Exception:
                    raise
        else:
            #for message in messages:
            #    logging.debug("CAN.recv(): {!r}".format(message))
            return messages

    def add_to_ioloop(self, ioloop, callback=None):
        self._read_handler = self._get_bytes_async
        ioloop.add_handler(
            self.conn.fd,
            functools.partial(self._ioloop_event_handler, callback=callback),
            ioloop.READ)

    def open(self, callback=None):
        self.close()
        speed_code = {
            1000000: 8,
            500000: 6,
            250000: 5,
            125000: 4
        }[self.baudrate]
        self.conn.write("S{0:d}\r".format(speed_code))
        self.conn.flush()
        self._recv()
        self.conn.write("O\r")
        self.conn.flush()
        self._recv()
        time.sleep(0.1)

    def close(self, callback=None):
        self.conn.write("C\r")
        self.conn.flush()
        time.sleep(0.1)

    def send(self, message_id, message, extended=False):
        #logging.debug("CAN.send({!r}, {!r}, {!r})".format(
        #              message_id, message, extended))

        if extended:
            start = "T{0:08X}".format(message_id)
        else:
            start = "t{0:03X}".format(message_id)
        line = "{0:s}{1:1d}{2:s}\r".format(start, len(message),
                                           binascii.b2a_hex(message))
        self.conn.write(line)
        self.conn.flush()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: driver.py CAN_DEVICE")
        sys.exit()

    if "tty" in sys.argv[1]:
        can = SLCAN(sys.argv[1])
    else:
        can = SocketCAN(sys.argv[1])

    can.open()
    while True:
        messages = can._recv()
        for message in messages:
            print(message)

