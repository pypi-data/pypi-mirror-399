# Copyright (C) GridGain Systems. All Rights Reserved.
# _________        _____ __________________        _____
# __  ____/___________(_)______  /__  ____/______ ____(_)_______
# _  / __  __  ___/__  / _  __  / _  / __  _  __ `/__  / __  __ \
# / /_/ /  _  /    _  /  / /_/ /  / /_/ /  / /_/ / _  /  _  / / /
# \____/   /_/     /_/   \_,__/   \____/   \__,_/  /_/   /_/ /_/
from typing import List

import pytest

from pygridgain import AsyncBinaryMap, AsyncClient, EndPoint
from tests.dummy_server import DummyClusterSharedState, DummyServer, OperationType


@pytest.fixture()
async def dummy_cluster3() -> List[DummyServer]:
    cluster_size = 3
    cluster = []
    state = DummyClusterSharedState()
    for i in range(0, cluster_size):
        server = DummyServer(EndPoint("127.0.0.1", 12000 + i), cluster=state)
        await server.start()
        cluster.append(server)

    yield cluster

    for server in cluster:
        await server.stop()


CONNECTION_TIMEOUT = 1.0


def events_of_type(cluster: List[DummyServer], op_type: OperationType):
    return [e[1] for e in cluster[0].cluster.events if e[0] == op_type]


@pytest.mark.parametrize(
    "operation,operation_type",
    [
        (AsyncBinaryMap.get, OperationType.TUPLE_GET),
        (AsyncBinaryMap.pop, OperationType.TUPLE_GET_AND_DELETE),
        (AsyncBinaryMap.contains, OperationType.TUPLE_CONTAINS_KEY),
    ],
)
@pytest.mark.asyncio
async def test_routing_sequence_key_ops(dummy_cluster3, operation, operation_type):
    address = [server.address for server in dummy_cluster3]
    async with AsyncClient(address=address, connection_timeout=CONNECTION_TIMEOUT) as client:
        assert client is not None
        test_map = await client.structures().get_or_create_binary_map("TestMap")
        await operation(test_map, b"1")
        await operation(test_map, b"2")
        await operation(test_map, b"3")
        await operation(test_map, b"4")
        await operation(test_map, b"5")

        put_events = events_of_type(dummy_cluster3, operation_type)
        assert len(put_events) == 5

        assert put_events[0] == dummy_cluster3[1].name
        assert put_events[1] == dummy_cluster3[2].name
        assert put_events[2] == dummy_cluster3[0].name
        assert put_events[3] == dummy_cluster3[0].name
        assert put_events[4] == dummy_cluster3[1].name


@pytest.mark.asyncio
async def test_routing_sequence_put(dummy_cluster3):
    address = [server.address for server in dummy_cluster3]
    async with AsyncClient(address=address, connection_timeout=CONNECTION_TIMEOUT) as client:
        assert client is not None
        test_map = await client.structures().get_or_create_binary_map("TestMap")
        await test_map.put(b"1", b"1")
        await test_map.put(b"2", b"2")
        await test_map.put(b"3", b"3")
        await test_map.put(b"4", b"4")
        await test_map.put(b"5", b"5")

        put_events = events_of_type(dummy_cluster3, OperationType.TUPLE_GET_AND_UPSERT)
        assert len(put_events) == 5

        assert put_events[0] == dummy_cluster3[1].name
        assert put_events[1] == dummy_cluster3[2].name
        assert put_events[2] == dummy_cluster3[0].name
        assert put_events[3] == dummy_cluster3[0].name
        assert put_events[4] == dummy_cluster3[1].name


@pytest.mark.parametrize(
    "operation,operation_type",
    [
        (AsyncBinaryMap.get, OperationType.TUPLE_GET),
        (AsyncBinaryMap.pop, OperationType.TUPLE_GET_AND_DELETE),
        (AsyncBinaryMap.contains, OperationType.TUPLE_CONTAINS_KEY),
    ],
)
@pytest.mark.asyncio
async def test_routing_same_key_ops(dummy_cluster3, operation, operation_type):
    values_num = 1000
    address = [server.address for server in dummy_cluster3]
    async with AsyncClient(address=address, connection_timeout=CONNECTION_TIMEOUT) as client:
        assert client is not None
        test_map = await client.structures().get_or_create_binary_map("TestMap")
        for _ in range(0, values_num):
            await operation(test_map, b"1")

        put_events = events_of_type(dummy_cluster3, operation_type)
        assert len(put_events) == values_num

        for event in put_events:
            assert event == dummy_cluster3[1].name


@pytest.mark.asyncio
async def test_routing_same_put(dummy_cluster3):
    values_num = 1000
    address = [server.address for server in dummy_cluster3]
    async with AsyncClient(address=address, connection_timeout=CONNECTION_TIMEOUT) as client:
        assert client is not None
        test_map = await client.structures().get_or_create_binary_map("TestMap")
        for _ in range(0, values_num):
            await test_map.put(b"1", b"1")

        put_events = events_of_type(dummy_cluster3, OperationType.TUPLE_GET_AND_UPSERT)
        assert len(put_events) == values_num

        for event in put_events:
            assert event == dummy_cluster3[1].name
