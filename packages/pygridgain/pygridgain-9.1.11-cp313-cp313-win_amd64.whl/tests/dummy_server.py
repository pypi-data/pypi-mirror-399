# Copyright (C) GridGain Systems. All Rights Reserved.
# _________        _____ __________________        _____
# __  ____/___________(_)______  /__  ____/______ ____(_)_______
# _  / __  __  ___/__  / _  __  / _  / __  _  __ `/__  / __  __ \
# / /_/ /  _  /    _  /  / /_/ /  / /_/ /  / /_/ / _  /  _  / / /
# \____/   /_/     /_/   \_,__/   \____/   \__,_/  /_/   /_/ /_/
import asyncio
import contextlib
import logging
import threading
import uuid
from asyncio import StreamReader, StreamWriter
from enum import IntEnum
from io import BytesIO
from typing import Optional

import msgpack
from msgpack import Packer, Unpacker

from pygridgain import EndPoint, ErrorCode, IgniteError
from pygridgain.async_node_connection import MAGIC_BYTES
from pygridgain.constants import PROTOCOL_BYTE_ORDER


class ExtensionType(IntEnum):
    UUID = 3


class OperationType(IntEnum):
    TUPLE_GET = 12
    TUPLE_GET_AND_UPSERT = 16
    TUPLE_GET_AND_DELETE = 32
    TUPLE_CONTAINS_KEY = 33
    PARTITION_ASSIGNMENT_GET = 53
    MAP_GET_OR_CREATE = 1007


class ResponseFlag(IntEnum):
    ERROR = 4


def pack_uuid(out_buf: BytesIO, value):
    packer = Packer()
    packer.pack_ext_type(typecode=int(ExtensionType.UUID), data=value.bytes)
    out_buf.write(packer.bytes())


def pack_error(out_buf: BytesIO, err: IgniteError):
    pack_uuid(out_buf, uuid.uuid4())
    msgpack.pack(err.code, out_buf)
    msgpack.pack("org.apache.ignite.lang.IgniteException", out_buf)
    msgpack.pack(str(err), out_buf)
    msgpack.pack(None, out_buf)
    msgpack.pack(None, out_buf)


class DummyTable:
    def __init__(self, name: str, tid: int):
        self.name = name
        self.tid = tid
        self.entries = {}


class DummyClusterSharedState:
    def __init__(self, *, partitions: int = 16):
        self._lock = threading.Lock()
        self._store_name = {}
        self._store_id = {}
        self._id_counter = 0
        self._partitions = partitions
        self._nodes = []
        self._assignment = []
        self._events = []

    @property
    def system_schema(self):
        return "SYSTEM"

    @property
    def public_schema(self):
        return "PUBLIC"

    @property
    def partitions(self):
        return self._partitions

    @property
    def assignment(self):
        return self._assignment

    @property
    def events(self):
        return self._events

    def get_or_create_table(self, name: str) -> DummyTable:
        with self._lock:
            table = self._store_name.get(name)
            if table is None:
                self._id_counter += 1
                table = DummyTable(name, self._id_counter)
                self._store_name[table.name] = table
                self._store_id[table.tid] = table
            return table

    def add_node(self, node_name):
        self._nodes.append(node_name)
        self._assignment = []
        for i in range(0, self._partitions):
            self._assignment.append(self._nodes[i % len(self._nodes)])

    def add_event(self, operation: int, node_name: str):
        self._events.append((operation, node_name))


class DummyServer:
    def __init__(self, address: EndPoint, *, cluster: DummyClusterSharedState):
        self._serve_task = None
        self._address = address
        self._server: Optional[asyncio.Server] = None
        self._handshake_performed = False
        self._protocol_ver = None
        self._extensions = {}
        self._observable_timestamp = 1
        self._cluster: Optional[DummyClusterSharedState] = cluster
        self._name = str(uuid.uuid4())

        if self._cluster is not None:
            self._cluster.add_node(self._name)

    @property
    def name(self):
        return self._name

    @property
    def address(self):
        return self._address

    @property
    def observable_timestamp(self):
        self._observable_timestamp += 1
        return self._observable_timestamp

    @property
    def partitions(self):
        return self._cluster.partitions

    @property
    def assignment(self):
        return self._cluster.assignment

    @property
    def cluster(self):
        return self._cluster

    def _handle_handshake(self, unpacker: Unpacker, out_buf: BytesIO):
        ver_major = unpacker.unpack()
        ver_minor = unpacker.unpack()
        ver_patch = unpacker.unpack()
        self._protocol_ver = (ver_major, ver_minor, ver_patch)

        client_type = unpacker.unpack()
        if client_type != 5:
            raise IgniteError(ErrorCode.PROTOCOL, f"Unexpected client type: {client_type}")

        _feature_bitmask = unpacker.unpack()

        extensions = {}
        extensions_size = unpacker.unpack()
        for _ in range(0, extensions_size):
            key = unpacker.unpack()
            value = unpacker.unpack()
            extensions[key] = value
        self._extensions = extensions

        msgpack.pack(ver_major, out_buf)
        msgpack.pack(ver_minor, out_buf)
        msgpack.pack(ver_patch, out_buf)

        msgpack.pack(None, out_buf)  # Error
        msgpack.pack(0, out_buf)  # Idle timeout in ms

        node_id = str(uuid.uuid4())
        msgpack.pack(node_id, out_buf)

        msgpack.pack(self._name, out_buf)

        cluster_id = uuid.uuid4()
        msgpack.pack(1, out_buf)
        pack_uuid(out_buf, cluster_id)

        cluster_name = str(uuid.uuid4())
        msgpack.pack(cluster_name, out_buf)

        msgpack.pack(self.observable_timestamp, out_buf)

        msgpack.pack(9, out_buf)
        msgpack.pack(1, out_buf)
        msgpack.pack(127, out_buf)
        msgpack.pack(0, out_buf)
        msgpack.pack("DEV", out_buf)

        msgpack.pack(b"0", out_buf)

        msgpack.pack(0, out_buf)  # Extensions

    def _handle_message(self, unpacker: Unpacker, out_buf: BytesIO):
        if not self._handshake_performed:
            logging.debug("Handshake request received")
            self._handle_handshake(unpacker, out_buf)
            self._handshake_performed = True
        else:
            op_code = unpacker.unpack()
            req_id = unpacker.unpack()
            logging.debug(f"Message received op_code={op_code}, req_id={req_id}")

            msgpack.pack(req_id, out_buf)
            msgpack.pack(0, out_buf)  # flags
            msgpack.pack(self.observable_timestamp, out_buf)

            self.cluster.add_event(op_code, self.name)

            try:
                if op_code == OperationType.MAP_GET_OR_CREATE:
                    if self._cluster is None:
                        raise IgniteError(ErrorCode.INTERNAL, "Cluster shared state is not initialized")

                    name = unpacker.unpack()

                    table = self._cluster.get_or_create_table(name)

                    msgpack.pack(self._cluster.system_schema, out_buf)
                    msgpack.pack(table.name, out_buf)

                    msgpack.pack(self._cluster.public_schema, out_buf)
                    msgpack.pack(table.name, out_buf)

                    msgpack.pack(table.tid, out_buf)

                elif op_code == OperationType.PARTITION_ASSIGNMENT_GET:
                    _tid = unpacker.unpack()
                    timestamp = unpacker.unpack()

                    msgpack.pack(len(self.assignment), out_buf)
                    msgpack.pack(True, out_buf)
                    msgpack.pack(timestamp, out_buf)

                    for node_name in self.assignment:
                        msgpack.pack(node_name, out_buf)

                elif op_code in [OperationType.TUPLE_GET_AND_UPSERT, OperationType.TUPLE_GET, OperationType.TUPLE_GET_AND_DELETE]:
                    _tid = unpacker.unpack()
                    _tx = unpacker.unpack()
                    schema_ver = unpacker.unpack()

                    _null_bitset = unpacker.unpack()
                    _tuple = unpacker.unpack()

                    msgpack.pack(schema_ver, out_buf)
                    msgpack.pack(None, out_buf)

                elif op_code == OperationType.TUPLE_CONTAINS_KEY:
                    _tid = unpacker.unpack()
                    _tx = unpacker.unpack()
                    schema_ver = unpacker.unpack()

                    _null_bitset = unpacker.unpack()
                    _tuple = unpacker.unpack()

                    msgpack.pack(schema_ver, out_buf)
                    msgpack.pack(False, out_buf)

                else:
                    raise IgniteError(ErrorCode.INTERNAL, f"Operation {op_code} with request ID {req_id} is not supported")

            except IgniteError as err:
                out_buf.seek(0)
                msgpack.pack(req_id, out_buf)
                msgpack.pack(ResponseFlag.ERROR, out_buf)
                msgpack.pack(self.observable_timestamp, out_buf)
                pack_error(out_buf, err)

    async def handle_client(self, reader: StreamReader, writer: StreamWriter):
        try:
            logging.debug(f"Server on {self.address.host}:{self.address.port} has started")
            if not self._handshake_performed:
                header = await reader.read(4)
                if header != MAGIC_BYTES:
                    ascii_code = header.decode("ascii")
                    raise IgniteError(
                        ErrorCode.HANDSHAKE_HEADER,
                        f"Invalid magic header in thin client connection. Expected 'IGNI', but was '{ascii_code}'",
                    )
                writer.write(MAGIC_BYTES)

            while True:
                size_bytes = await reader.read(4)
                if len(size_bytes) == 0:
                    break

                size = int.from_bytes(size_bytes, byteorder=PROTOCOL_BYTE_ORDER)

                payload = await reader.read(size)
                if len(payload) == 0:
                    break

                unpacker = msgpack.Unpacker()
                unpacker.feed(payload)

                out_buf = BytesIO()
                self._handle_message(unpacker, out_buf)

                data = out_buf.getvalue()
                size_buffer = int.to_bytes(len(data), 4, byteorder=PROTOCOL_BYTE_ORDER)
                writer.write(size_buffer + data)

                await writer.drain()

        except asyncio.CancelledError:
            pass
        finally:
            # noinspection PyBroadException
            try:
                await writer.drain()
                writer.close()
                await writer.wait_closed()
            except Exception as err:
                logging.debug(
                    f"Error while closing a connection: {err}",
                )

    async def start(self):
        self._server = await asyncio.start_server(self.handle_client, self._address.host, self._address.port)
        self._serve_task = asyncio.create_task(self._server.serve_forever())

    async def stop(self):
        # noinspection PyBroadException
        try:
            logging.debug(f"Server on {self.address.host}:{self.address.port} is stopping")
            self._server.close()
            self._server.close_clients()
            await self._server.wait_closed()
            self._serve_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._serve_task
        except Exception as err:
            logging.debug(
                f"Error while stopping a server: {err}",
            )
        finally:
            logging.debug(f"Server on {self.address.host}:{self.address.port} has stopped")
