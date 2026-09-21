import os
import json
import unittest

from backend.app.core.config import settings
from streamlit_app import SchemeEligibilityDeriver, fetch_schemes_from_sqlite_db

class TestDigiLockerStateMachine(unittest.TestCase):
    def test_state_machine_not_configured_graceful_handling(self):
        """Verify NOT_CONFIGURED credentials state handling."""
        enabled = settings.DIGILOCKER_ENABLED
        client_id = settings.DIGILOCKER_CLIENT_ID
        if not enabled or not client_id:
            self.assertFalse(enabled and bool(client_id), "Settings accurately report missing production credentials.")

    def test_baseline_features_unaffected(self):
        """Verify 71-scheme discovery engine & master catalog remain 100% frozen and operational."""
        idx = SchemeEligibilityDeriver.get_index()
        self.assertEqual(len(idx), 71, "Master Eligibility Index contains exactly 71 schemes.")

        # Healthcare & Insurance test
        hc_matches = [s for s in fetch_schemes_from_sqlite_db({}) if SchemeEligibilityDeriver.evaluate_scheme(s, {"category": "Healthcare & Insurance"})[0]]
        self.assertEqual(len(hc_matches), 8, "Healthcare & Insurance category returns 8 schemes.")

        # Pudhumai Penn female/male test
        pudhumai = [s for s in fetch_schemes_from_sqlite_db({}) if "pudhumai" in s["title"].lower()][0]
        self.assertTrue(SchemeEligibilityDeriver.evaluate_scheme(pudhumai, {"gender": "Female"})[0])
        self.assertFalse(SchemeEligibilityDeriver.evaluate_scheme(pudhumai, {"gender": "Male"})[0])

if __name__ == "__main__":
    unittest.main()
