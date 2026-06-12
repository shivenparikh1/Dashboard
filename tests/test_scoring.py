import unittest

from src.classification import classify_risk_level
from src.scoring import calculate_score_from_values, calculate_total_risk_score


class ScoringTests(unittest.TestCase):
    def test_total_score_sums_all_five_factors(self):
        score = calculate_total_risk_score(5, 4, 3, 2, 1)
        self.assertEqual(score, 15)

    def test_minimum_and_maximum_scores(self):
        self.assertEqual(calculate_score_from_values([1, 1, 1, 1, 1]), 5)
        self.assertEqual(calculate_score_from_values([5, 5, 5, 5, 5]), 25)

    def test_risk_level_boundaries(self):
        expected_levels = {
            5: "Low",
            10: "Low",
            11: "Medium",
            17: "Medium",
            18: "High",
            22: "High",
            23: "Critical",
            25: "Critical",
        }
        for score, expected in expected_levels.items():
            with self.subTest(score=score):
                self.assertEqual(classify_risk_level(score), expected)

    def test_invalid_factor_rating_raises_error(self):
        with self.assertRaises(ValueError):
            calculate_total_risk_score(0, 3, 3, 3, 3)
        with self.assertRaises(ValueError):
            calculate_total_risk_score(6, 3, 3, 3, 3)

    def test_wrong_number_of_factors_raises_error(self):
        with self.assertRaises(ValueError):
            calculate_score_from_values([1, 2, 3])

    def test_invalid_total_score_raises_error(self):
        with self.assertRaises(ValueError):
            classify_risk_level(26)


if __name__ == "__main__":
    unittest.main()
