import unittest
from unittest import TestCase


class TestDemoFunctions(TestCase):
    def test_calculate_statistics(self):
        from demo_libry_lokesh.demo_functions import calculate_statistics
        import numpy as np

        data = [1, 2, 3, 4, 5]
        stats = calculate_statistics(data)

        assert np.isclose(stats['mean'], 3.0), "Mean calculation is incorrect"
        assert np.isclose(stats['median'], 3.0), "Median calculation is incorrect"
        assert np.isclose(stats['std_dev'], np.std(data)), "Standard deviation calculation is incorrect"
        
        
if __name__ == "__main__":
    unittest.main()