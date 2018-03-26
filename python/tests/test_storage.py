"""
Basic tests for the storage integrity of the data.
"""
from __future__ import print_function
from __future__ import division

import unittest
import tempfile
import os

import numpy as np
import hypothesis
import hypothesis.strategies as hst
import hypothesis.extra.numpy as hnp

import kastore as kas


class TestRoundTrip(unittest.TestCase):
    """
    Tests that we can round trip data through a temporary file.
    """
    def setUp(self):
        fd, self.temp_file = tempfile.mkstemp(suffix=".kas", prefix="kas_rt_test")
        os.close(fd)

    def tearDown(self):
        os.unlink(self.temp_file)

    def verify(self, data):
        kas.dump(data, self.temp_file)
        new_data = kas.load(self.temp_file)
        self.assertEqual(sorted(new_data.keys()), sorted(data.keys()))
        for key, source_array in data.items():
            dest_array = new_data[key]
            # Numpy's testing assert_equal will deal correctly with NaNs.
            np.testing.assert_equal(source_array, dest_array)


class TestRoundTripSimple(TestRoundTrip):
    """
    Simple round-trip tests for some hand crafted cases.
    """
    def test_single_key(self):
        self.verify({"a": np.zeros(1)})

    def test_many_keys(self):
        data = {}
        for j in range(100):
            data[str(j)] = j + np.zeros(j, dtype=np.uint32)
        self.verify(data)


class TestRoundTripKeys(TestRoundTrip):
    """
    Test round tripping with keys generated by hypothesis.
    """
    @hypothesis.given(key=hst.text())
    def test_single_key(self, key):
        self.verify({key: np.zeros(1)})

    @hypothesis.given(keys=hst.sets(hst.text(), min_size=1))
    def test_many_keys(self, keys):
        data = {key: np.ones(j) * j for j, key in enumerate(keys)}
        self.verify(data)


shape_strategy = hnp.array_shapes(max_dims=1)


class TestRoundTripDataTypes(TestRoundTrip):
    """
    Test round tripping of the various types using Hypothesis.
    """
    @hypothesis.given(value=hnp.arrays(dtype=np.uint8, shape=shape_strategy))
    def test_single_uint8(self, value):
        self.verify({"a": value})

    @hypothesis.given(value=hnp.arrays(dtype=np.int8, shape=shape_strategy))
    def test_single_int8(self, value):
        self.verify({"a": value})

    @hypothesis.given(value=hnp.arrays(dtype=np.int32, shape=shape_strategy))
    def test_single_int32(self, value):
        self.verify({"a": value})

    @hypothesis.given(value=hnp.arrays(dtype=np.uint32, shape=shape_strategy))
    def test_single_uint32(self, value):
        self.verify({"a": value})

    @hypothesis.given(value=hnp.arrays(dtype=np.int64, shape=shape_strategy))
    def test_single_int64(self, value):
        self.verify({"a": value})

    @hypothesis.given(value=hnp.arrays(dtype=np.uint64, shape=shape_strategy))
    def test_single_uint64(self, value):
        self.verify({"a": value})

    @hypothesis.given(value=hnp.arrays(dtype=np.float32, shape=shape_strategy))
    def test_single_float32(self, value):
        self.verify({"a": value})

    @hypothesis.given(value=hnp.arrays(dtype=np.float64, shape=shape_strategy))
    def test_single_float64(self, value):
        self.verify({"a": value})
