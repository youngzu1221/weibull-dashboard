import unittest

from core.spares import (
    calculate_expected_removals,
    calculate_spare_quantity,
    recommend_spare_quantity,
    spare_recommendations_by_confidence,
)


class SpareQuantityTests(unittest.TestCase):
    def test_expected_removals_uses_tat_as_a_fraction_of_a_year(self):
        expected = calculate_expected_removals(
            aircraft_count=5,
            annual_flight_hours=5_000.0,
            turnaround_days=30.0,
            quantity_per_aircraft=2.0,
            mtbur=1_000.0,
        )
        self.assertAlmostEqual(expected, 5_000.0 * 2.0 * 5.0 * 30.0 / (365.0 * 1_000.0))

    def test_recommended_quantity_meets_confidence_target(self):
        result = recommend_spare_quantity(4.0, 95.0)
        self.assertGreaterEqual(result.achieved_confidence, 0.95)
        self.assertLess(result.recommended_spares, 20)

    def test_zero_demand_requires_no_spares(self):
        result = calculate_spare_quantity(1, 0.0, 30.0, 1.0, 1_000.0, 95.0)
        self.assertEqual(result.recommended_spares, 0)
        self.assertEqual(result.achieved_confidence, 1.0)

    def test_rejects_invalid_confidence(self):
        with self.assertRaises(ValueError):
            recommend_spare_quantity(1.0, 100.0)

    def test_confidence_schedule_starts_at_50_and_increases_by_five(self):
        schedule = spare_recommendations_by_confidence(4.0)
        confidence_levels = [round(item.requested_confidence * 100.0, 8) for item in schedule]
        spare_counts = [item.recommended_spares for item in schedule]

        self.assertEqual(confidence_levels, [float(level) for level in range(50, 100, 5)])
        self.assertEqual(spare_counts, sorted(spare_counts))


if __name__ == "__main__":
    unittest.main()
