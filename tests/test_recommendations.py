import unittest

from src.recommendations import generate_recommendations


class RecommendationTests(unittest.TestCase):
    def test_recommendations_include_risk_type_action(self):
        actions = generate_recommendations(
            "Logistics", "Semiconductors", risk_level="High"
        )
        self.assertIn("alternate ports", actions[0])

    def test_recommendations_include_component_action(self):
        actions = generate_recommendations(
            "Quality", "Battery Cells", risk_level="Critical"
        )
        self.assertIn("cell chemistry", actions[1])

    def test_critical_risk_receives_immediate_escalation(self):
        actions = generate_recommendations(
            "Geopolitical", "Wiring Harnesses", risk_level="Critical"
        )
        self.assertIn("response room today", actions[2])

    def test_unknown_values_receive_fallback_actions(self):
        actions = generate_recommendations(
            "Other", "Custom Assembly", risk_level="Medium"
        )
        self.assertEqual(len(actions), 3)
        self.assertIn("Validate the event", actions[0])
        self.assertIn("Review inventory coverage", actions[1])


if __name__ == "__main__":
    unittest.main()
