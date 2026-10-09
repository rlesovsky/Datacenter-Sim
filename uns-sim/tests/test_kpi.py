import unittest
from pathlib import Path

from catalog.build_catalog import parse_markdown
from sim.hall import Hall
from sim.kpi import Campus, couple_kpis


ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "docs" / "KPI_UNS.md"


class KpiTests(unittest.TestCase):
    def test_catalog_is_one_of_each_and_a_campus_branch(self):
        points = parse_markdown(CATALOG)
        self.assertLess(len(points), 120)
        self.assertGreaterEqual(sum(1 for point in points if point["cell"] == "Chiller01"), 1)
        self.assertTrue(any(point["name"] == "PowerFactor" for point in points))
        self.assertTrue(any(point["name"] == "FlowSCFM" for point in points))
        self.assertFalse(any(point["cell"] == "Chiller02" for point in points))
        campus = [point for point in points if point["scope"] == "campus"]
        self.assertTrue(any(point["cell"] == "KPI" and point["name"] == "PUE" for point in campus))
        self.assertTrue(all(point["value_kind"] == "calc" for point in campus if point["category"] == "KPI"))

    def test_pue_is_facility_over_it(self):
        points = parse_markdown(CATALOG)
        hall_points = [point for point in points if point["scope"] == "hall"]
        campus = Campus([point for point in points if point["scope"] == "campus"], 0.5)
        hall = Hall(1, 1, hall_points, 0.5)
        halls = {(1, 1): hall}
        for _ in range(3):
            hall.couple(60.0)
            for point in hall.points.values():
                point.step(60.0, 60.0)
            couple_kpis(halls, campus, 0.0)
        it_kw = hall.point("HallPower", "ITKW").value
        facility_kw = hall.point("HallPower", "TotalKW").value
        pue = campus.point("KPI", "PUE").value
        self.assertGreater(pue, 1.0)
        self.assertAlmostEqual(pue, facility_kw / it_kw, places=2)
        produced = campus.point("Gen", "SiteProducedKW").value
        demand = campus.point("ElecPlant", "DemandKW").value
        self.assertAlmostEqual(demand, facility_kw - produced, places=1)
        self.assertGreater(campus.point("ElecPlant", "MonthEnergyKWh").value, 0)


if __name__ == "__main__":
    unittest.main()
