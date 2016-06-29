
import unittest
import math
import random

from api.utils import get_histogram, stdev


class HistogramTests(unittest.TestCase):
    def test_returns_bins_on_empty_input(self):
        bins = get_histogram([], 10)
        self.assertEqual(len(bins), 10)
        self.assertEqual(bins[0]['min'], 0.0)
        self.assertEqual(bins[0]['max'], 0.1)
        self.assertEqual(bins[-1]['max'], 1.0)
        for b in bins:
            self.assertEqual(b['count'], 0)

    def test_raises_on_invalid_num_bins(self):
        self.assertRaises(
            ValueError,
            get_histogram,
            [1, 2, 3],
            0
        )

    def test_when_inputs_are_same_value(self):
        bins = get_histogram([5, 5, 5], 2)
        self.assertEqual(len(bins), 2)
        self.assertEqual(bins[0]['min'], 4.5)
        self.assertEqual(bins[1]['max'], 5.5)
        self.assertEqual(bins[1]['count'], 3)

    def test_simple_histogram(self):
        num_bins = 3
        bins = get_histogram([1, 2, 3], num_bins)
        self.assertEqual(len(bins), num_bins)
        self.assertEqual(bins[0]['min'], 1)
        self.assertEqual(bins[2]['max'], 3)
        for b in bins:
            self.assertEqual(b['count'], 1)

    def test_bigger_histogram(self):
        num_bins = 12
        values = [round(random.random(), 2) for _ in range(10000)]
        bins = get_histogram(values, num_bins)
        self.assertEqual(len(bins), num_bins)
        mx = max(values)
        mn = min(values)
        self.assertEqual(bins[0]['min'], mn)
        self.assertEqual(bins[-1]['max'], mx)


class StandardDeviationTests(unittest.TestCase):
    def test_returns_nan_on_empty_input(self):
        values = []
        self.assertTrue(math.isnan(stdev(values)))

    def test_returns_zero_when_values_are_same(self):
        values = [1, 1, 1]
        self.assertEqual(0, stdev(values))

    def test_retuns_standard_deviation(self):
        values = [10, 20, 30, 40, 50]
        self.assertAlmostEqual(14.1421356, stdev(values))
