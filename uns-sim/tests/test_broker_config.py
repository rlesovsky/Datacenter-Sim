import tempfile
import unittest
from pathlib import Path

from sim.broker_config import check_broker, read_broker, write_broker


SAMPLE = """broker:
  host: 127.0.0.1
  port: 1883
  tls: false
  username: ""
  password: ""
  client_id: uns-sim-w1

enterprise: DataCenter
"""


class BrokerConfigTests(unittest.TestCase):
    def test_round_trip_keeps_the_rest_of_the_file(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "site.yaml"
            path.write_text(SAMPLE, encoding="utf-8")
            write_broker(path, "10.1.2.3", 1884, "ops", "p@ss word")
            text = path.read_text(encoding="utf-8")
            self.assertIn("enterprise: DataCenter", text)
            self.assertIn("client_id: uns-sim-w1", text)
            broker = read_broker(path)
            self.assertEqual(broker["host"], "10.1.2.3")
            self.assertEqual(broker["port"], 1884)
            self.assertEqual(broker["username"], "ops")
            self.assertEqual(broker["password"], "p@ss word")

    def test_rejects_a_blank_host(self) -> None:
        self.assertIsNotNone(check_broker("", 1883, "", ""))
        self.assertIsNone(check_broker("192.168.10.253", 1883, "admin", "hivemq"))


if __name__ == "__main__":
    unittest.main()
