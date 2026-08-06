import unittest
from unittest.mock import patch

from response_blocks import build_blocks_for_tool
from response_blocks.builders import (
    BLOCK_BUILDERS,
    MAX_CARDS_PER_RESPONSE,
    build_comparison_blocks,
    build_prediction_blocks,
    build_recommendation_blocks,
)


def assert_well_formed_block(test_case, block):
    test_case.assertIn("type", block)
    test_case.assertIn("version", block)
    test_case.assertIn("data", block)
    test_case.assertIsInstance(block["data"], dict)


def make_college(**overrides):
    college = {
        "college_id": 1,
        "college": "IIT Bombay",
        "branch": "Computer Science and Engineering",
        "closing_rank": 500,
        "avg_package": 36.9,
        "median_package": 30.0,
        "placement_rate": 96.0,
        "nirf_rank": 3,
        "fees": 1200000,
        "hostel_fees": 120000,
        "website": "https://www.iitb.ac.in",
        "exam": "JEE Advanced",
        "category": "OPEN",
        "quota": "AI"
    }
    college.update(overrides)
    return college


class ComparisonBlocksTests(unittest.TestCase):

    def test_ok_result_produces_one_well_formed_comparison_card(self):
        tool_result = {
            "status": "ok",
            "branch_1": {"college": "IIT Bombay", "branch": "CSE", "avg_package": 36.9},
            "branch_2": {"college": "IIT Delhi", "branch": "CSE", "avg_package": 32.0}
        }

        blocks = build_comparison_blocks(tool_result)

        self.assertEqual(len(blocks), 1)
        assert_well_formed_block(self, blocks[0])
        self.assertEqual(blocks[0]["type"], "comparison_card")
        self.assertEqual(blocks[0]["version"], 1)
        self.assertEqual(blocks[0]["data"]["branch_1"]["college"], "IIT Bombay")
        self.assertEqual(blocks[0]["data"]["branch_2"]["college"], "IIT Delhi")

    def test_not_found_status_produces_no_blocks(self):
        tool_result = {"status": "not_found", "field": "college", "query": "Xyzzy"}
        self.assertEqual(build_comparison_blocks(tool_result), [])

    def test_ambiguous_status_produces_no_blocks(self):
        tool_result = {"status": "ambiguous", "candidates": ["IIT Kanpur", "IIT Kharagpur"]}
        self.assertEqual(build_comparison_blocks(tool_result), [])

    def test_missing_branch_data_falls_back_gracefully(self):
        tool_result = {"status": "ok", "branch_1": {"college": "IIT Bombay"}}
        self.assertEqual(build_comparison_blocks(tool_result), [])

    def test_non_dict_input_falls_back_gracefully(self):
        self.assertEqual(build_comparison_blocks(None), [])
        self.assertEqual(build_comparison_blocks("unexpected string"), [])
        self.assertEqual(build_comparison_blocks([1, 2, 3]), [])


class RecommendationBlocksTests(unittest.TestCase):

    def test_valid_list_produces_well_formed_cards(self):
        blocks = build_recommendation_blocks([make_college()])

        self.assertEqual(len(blocks), 1)
        assert_well_formed_block(self, blocks[0])
        self.assertEqual(blocks[0]["type"], "recommendation_card")
        self.assertEqual(blocks[0]["version"], 1)
        self.assertEqual(blocks[0]["data"]["college_id"], 1)
        self.assertEqual(blocks[0]["data"]["college_name"], "IIT Bombay")

    def test_empty_list_produces_no_blocks(self):
        self.assertEqual(build_recommendation_blocks([]), [])

    def test_caps_at_max_cards_per_response(self):
        colleges = [make_college(college_id=i) for i in range(20)]
        blocks = build_recommendation_blocks(colleges)
        self.assertEqual(len(blocks), MAX_CARDS_PER_RESPONSE)

    def test_non_list_input_falls_back_gracefully(self):
        self.assertEqual(build_recommendation_blocks(None), [])
        # This is the search_colleges shape (dict with "results"), not the
        # recommend_colleges shape (bare list) -- must not be confused.
        self.assertEqual(build_recommendation_blocks({"results": [make_college()]}), [])

    def test_non_dict_items_are_skipped_not_fatal(self):
        blocks = build_recommendation_blocks([make_college(), "garbage", None, 42])
        self.assertEqual(len(blocks), 1)


class PredictionBlocksTests(unittest.TestCase):

    def test_valid_results_produce_cards_with_exam_context(self):
        tool_result = {"exam": "JEE Advanced", "results": [make_college()]}

        blocks = build_prediction_blocks(tool_result)

        self.assertEqual(len(blocks), 1)
        assert_well_formed_block(self, blocks[0])
        self.assertEqual(blocks[0]["type"], "prediction_card")
        self.assertEqual(blocks[0]["version"], 1)
        self.assertEqual(blocks[0]["data"]["exam"], "JEE Advanced")
        self.assertEqual(blocks[0]["data"]["category"], "OPEN")
        self.assertEqual(blocks[0]["data"]["quota"], "AI")

    def test_empty_results_produce_no_blocks(self):
        self.assertEqual(build_prediction_blocks({"results": []}), [])

    def test_missing_results_key_falls_back_gracefully(self):
        self.assertEqual(build_prediction_blocks({"exam": None}), [])

    def test_non_dict_input_falls_back_gracefully(self):
        self.assertEqual(build_prediction_blocks(["not", "a", "dict"]), [])
        self.assertEqual(build_prediction_blocks(None), [])


class BuildBlocksForToolTests(unittest.TestCase):
    """Covers the public entry point independently of the agent/frontend."""

    def test_routes_compare_colleges_to_comparison_builder(self):
        tool_result = {
            "status": "ok",
            "branch_1": {"college": "A"},
            "branch_2": {"college": "B"}
        }
        blocks = build_blocks_for_tool("compare_colleges", tool_result)
        self.assertEqual(blocks[0]["type"], "comparison_card")

    def test_routes_recommend_colleges_to_recommendation_builder(self):
        blocks = build_blocks_for_tool("recommend_colleges", [make_college()])
        self.assertEqual(blocks[0]["type"], "recommendation_card")

    def test_routes_search_colleges_to_prediction_builder(self):
        blocks = build_blocks_for_tool("search_colleges", {"results": [make_college()]})
        self.assertEqual(blocks[0]["type"], "prediction_card")

    def test_unrecognized_tool_falls_back_to_no_blocks(self):
        self.assertEqual(build_blocks_for_tool("search_documents", {"anything": True}), [])
        self.assertEqual(build_blocks_for_tool("nonexistent_tool", {}), [])

    def test_builder_exception_is_caught_not_raised(self):
        with patch.dict(BLOCK_BUILDERS, {"compare_colleges": lambda result: 1 / 0}):
            blocks = build_blocks_for_tool("compare_colleges", {})
        self.assertEqual(blocks, [])

    def test_none_tool_result_is_safe_for_every_registered_builder(self):
        for tool_name in BLOCK_BUILDERS:
            with self.subTest(tool=tool_name):
                self.assertEqual(build_blocks_for_tool(tool_name, None), [])

    def test_every_block_from_every_builder_is_well_formed(self):
        cases = [
            ("compare_colleges", {
                "status": "ok",
                "branch_1": {"college": "A"},
                "branch_2": {"college": "B"}
            }),
            ("recommend_colleges", [make_college()]),
            ("search_colleges", {"results": [make_college()]}),
        ]

        for tool_name, tool_result in cases:
            with self.subTest(tool=tool_name):
                blocks = build_blocks_for_tool(tool_name, tool_result)
                self.assertTrue(blocks, f"{tool_name} produced no blocks to check")
                for block in blocks:
                    assert_well_formed_block(self, block)


if __name__ == "__main__":
    unittest.main(verbosity=2)
