"""Check that CI cannot mistake an empty or failing Agent result for success."""

import json
import unittest

from check_datadog_image import assert_candidate_output, parse_check_output


def successful_output() -> list:
    return [{
        "runner": {"TotalRuns": 2, "TotalErrors": 0},
        "aggregator": {"metrics": [
            {"metric": "postgresql.wal.records"},
            {"metric": "postgresql.wal.bytes"},
        ]},
    }]


class ImageCheckResultTest(unittest.TestCase):
    def test_accepts_real_check_structure_after_cli_notices(self) -> None:
        payload = json.dumps(successful_output(), indent=2)
        output = "[notice] CLI startup\n" + payload
        self.assertEqual(parse_check_output(output), successful_output())
        assert_candidate_output(output)

    def test_rejects_empty_malformed_or_non_check_json(self) -> None:
        for output in ["", "[]", "[{broken]", '[{"unrelated": true}]']:
            with self.subTest(output=output), self.assertRaises(ValueError):
                parse_check_output(output)

    def test_rejects_check_errors_or_missing_runs(self) -> None:
        for field, value in [("TotalErrors", 1), ("TotalRuns", 0)]:
            payload = successful_output()
            payload[0]["runner"][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                assert_candidate_output(json.dumps(payload))

    def test_rejects_missing_wal_metrics(self) -> None:
        payload = successful_output()
        payload[0]["aggregator"]["metrics"] = []
        with self.assertRaises(ValueError):
            assert_candidate_output(json.dumps(payload))


if __name__ == "__main__":
    unittest.main()
