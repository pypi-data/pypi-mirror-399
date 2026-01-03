# Copyright (C) GridGain Systems. All Rights Reserved.
# _________        _____ __________________        _____
# __  ____/___________(_)______  /__  ____/______ ____(_)_______
# _  / __  __  ___/__  / _  __  / _  / __  _  __ `/__  / __  __ \
# / /_/ /  _  /    _  /  / /_/ /  / /_/ /  / /_/ / _  /  _  / / /
# \____/   /_/     /_/   \_,__/   \____/   \__,_/  /_/   /_/ /_/
from typing import Union

import pytest


def partition(data: Union[bytes, bytearray], part_cnt: int) -> int:
    # noinspection PyProtectedMember
    from pygridgain import _native_extension

    return _native_extension.primitive_partition(data, part_cnt)


# Values are generated using Java code (see HashUtils class)
data_binary = [
    (bytes([42]), 11, 3),
    (bytes([1, 1]), 7, 287),
    (bytes([1, 2, 3, 4]), 10, 1018),
    (bytes([128, 0, 255, 255, 127, 129, 128]), 0, 96),
    (b"abc", 17, 337),
    (b"Lorem ipsum dolor sit amet", 2, 306),
    (bytes([(i * 759028375) & 0xFF for i in range(0, 10000)]), 20, 836),
]

names_binary = [f"data_len{len(data[0])}_{data[1]}_{data[2]}" for i, data in enumerate(data_binary)]


@pytest.mark.parametrize("data,part24,part1024", data_binary, ids=names_binary)
def test_primitive_partition_binary(data: Union[bytes, bytearray], part24: int, part1024: int):
    assert partition(data, 24) == part24
    assert partition(data, 1024) == part1024
