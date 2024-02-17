import unittest
from main import DependencyCheck, rollup


class HealthRollupTests(unittest.TestCase):
    def test_all_healthy(self):
        summary = rollup([DependencyCheck('db', 'healthy', True, 10)], 10)
        self.assertEqual(summary.status, 'healthy')
        self.assertEqual(summary.reasons, ())










if __name__ == '__main__':
    unittest.main()
