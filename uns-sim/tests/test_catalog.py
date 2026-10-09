import unittest
from pathlib import Path

from catalog.build_catalog import parse_markdown, summarize
from sim.hall import Hall


ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "docs" / "Data_Wing_UNS.md"


class CatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.points = parse_markdown(CATALOG)

    def test_documented_hall_totals(self):
        counts = summarize(self.points)
        self.assertEqual(counts["ChillerMCP"], 86)
        self.assertEqual(counts["Chiller01"], 149)
        self.assertEqual(counts["Chiller10"], 149)
        self.assertEqual(counts["CDU01"], 94)
        self.assertEqual(counts["AireBlockMCP"], 225)
        self.assertEqual(counts["MiniAireBlock01"], 105)
        self.assertEqual(len(self.points), 2000)
        self.assertEqual(len(counts), 14)

    def test_supply_temp_is_analog(self):
        point = next(
            item
            for item in self.points
            if item["cell"] == "CDU01" and item["name"] == "ServerGlySupTemp"
        )
        self.assertEqual(point["units_code"], "degF")
        self.assertEqual(point["value_kind"], "analog")
        self.assertEqual(point["scan"], "Analog")

    def test_return_runs_warmer_than_supply(self):
        hall = Hall(1, 1, self.points, deadband_pct=0.5)
        for _ in range(40):
            hall.couple(10)
            for point in hall.points.values():
                point.step(0.5, 10)
        supply = hall.point("CDU01", "ServerGlySupTemp").value
        returned = hall.point("CDU01", "ServerGlyRetTemp").value
        self.assertGreater(returned, supply)
        self.assertFalse(hall.point("CDU01", "Pump3VFDRunSts").value)
        self.assertTrue(hall.point("CDU01", "Pump1VFDRunSts").value)


if __name__ == "__main__":
    unittest.main()
