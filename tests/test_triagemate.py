import unittest
from unittest.mock import patch
import json
from datetime import datetime, timezone, timedelta

from triagemate import core

class TestTriagemate(unittest.TestCase):
    @patch('triagemate.core._request')
    def test_label_issue(self, mock_request):
        mock_request.return_value = {"labels": [{"name": "bug"}]}
        core.label_issue("owner", "repo", 1, ["bug"], "token")
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(args[0], "POST")
        self.assertIn("/issues/1/labels", args[1])
        self.assertEqual(args[3], {"labels": ["bug"]})

    def test_is_stale(self):
        stale_days = 30
        old_date = datetime.now(timezone.utc) - timedelta(days=stale_days + 1)
        issue = {"updated_at": old_date.isoformat().replace("+00:00", "Z")}
        self.assertTrue(core.is_stale(issue, stale_days))
        recent_date = datetime.now(timezone.utc) - timedelta(days=stale_days - 1)
        issue["updated_at"] = recent_date.isoformat().replace("+00:00", "Z")
        self.assertFalse(core.is_stale(issue, stale_days))

    def test_generate_summary(self):
        issues = [
            {"state": "open", "labels": [{"name": "bug"}]},
            {"state": "open", "labels": [{"name": "enhancement"}]},
            {"state": "closed", "labels": []},
        ]
        summary_json = core.generate_summary(issues)
        summary = json.loads(summary_json)
        self.assertEqual(summary["total_issues"], 3)
        self.assertEqual(summary["open_issues"], 2)
        self.assertEqual(summary["closed_issues"], 1)
        self.assertEqual(summary["label_counts"]["bug"], 1)
        self.assertEqual(summary["label_counts"]["enhancement"], 1)

    def test_suggest_priority(self):
        issue_bug = {"labels": [{"name": "bug"}], "comments": 10}
        self.assertEqual(core.suggest_priority(issue_bug), "high")
        issue_enh = {"labels": [{"name": "enhancement"}], "comments": 4}
        self.assertEqual(core.suggest_priority(issue_enh), "medium")
        issue_low = {"labels": [{"name": "question"}], "comments": 1}
        self.assertEqual(core.suggest_priority(issue_low), "low")

if __name__ == "__main__":
    unittest.main()
