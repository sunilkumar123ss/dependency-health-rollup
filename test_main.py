import unittest
from main import DependencyCheck, rollup


class HealthRollupTests(unittest.TestCase):
    def test_all_healthy(self):
        summary = rollup([DependencyCheck('db', 'healthy', True, 10)], 10)
        self.assertEqual(summary.status, 'healthy')
        self.assertEqual(summary.reasons, ())

    def test_optional_failure_degrades(self):
        summary = rollup([DependencyCheck('search', 'unhealthy', False, 10)], 10)
        self.assertEqual(summary.status, 'degraded')

    def test_critical_failure_and_unknown_are_unhealthy(self):
        for status in ('unhealthy', 'unknown'):
            with self.subTest(status=status):
                self.assertEqual(rollup([DependencyCheck('db', status, True, 10)], 10).status, 'unhealthy')

    def test_critical_degraded_is_degraded(self):
        self.assertEqual(rollup([DependencyCheck('db', 'degraded', True, 10)], 10).status, 'degraded')

    def test_freshness_boundary_and_stale_critical(self):
        checks = [DependencyCheck('db', 'healthy', True, 0)]
        self.assertEqual(rollup(checks, 30, 30).status, 'healthy')
        stale = rollup(checks, 31, 30)
        self.assertEqual(stale.status, 'unhealthy')
        self.assertTrue(stale.dependencies[0]['stale'])
        self.assertEqual(stale.dependencies[0]['reported_status'], 'healthy')

    def test_empty_is_unknown(self):
        self.assertEqual(rollup([], 0).status, 'unknown')

    def test_order_is_deterministic_and_worst_severity_wins(self):
        checks = [DependencyCheck('z', 'unhealthy', True, 0), DependencyCheck('a', 'degraded', False, 0)]
        first = rollup(checks, 1)
        self.assertEqual(first, rollup(list(reversed(checks)), 1))
        self.assertEqual(first.status, 'unhealthy')
        self.assertEqual(first.dependencies[0]['name'], 'a')

    def test_duplicate_invalid_status_and_future_rejected(self):
        for checks in ([DependencyCheck('db', 'healthy', True, 0)] * 2,
                       [DependencyCheck('db', 'okay', True, 0)],
                       [DependencyCheck('db', 'healthy', True, 2)]):
            with self.subTest(checks=checks), self.assertRaises(ValueError): rollup(checks, 1)

    def test_invalid_clock_or_age_rejected(self):
        with self.assertRaises(ValueError): rollup([], float('nan'))
        with self.assertRaises(ValueError): rollup([], 0, -1)


if __name__ == '__main__':
    unittest.main()
