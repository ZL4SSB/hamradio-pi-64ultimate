import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from core_services import CatBroker, LogbookService, RadioStateService, band_from_frequency
from station_services import BeaconScheduleService, PropagationEngine, PropagationRequest, maidenhead_to_latlon, path_geometry


class StationCoreTests(unittest.TestCase):
    def test_band_edges(self):
        self.assertEqual(band_from_frequency(14_074_000), "20 m")
        self.assertEqual(band_from_frequency(145_500_000), "2 m")
        self.assertEqual(band_from_frequency(100_000), "Out of band")

    def test_state_notifications(self):
        service, seen = RadioStateService(), []
        service.subscribe(seen.append)
        service.set_frequency_mhz(7.074)
        self.assertEqual(seen[-1]["band"], "40 m")
        self.assertEqual(service.set_vfo("B")["vfo"], "B")

    def test_maidenhead_and_path(self):
        home = maidenhead_to_latlon("RE66")
        target = maidenhead_to_latlon("IO91WM")
        geometry = path_geometry(home, target)
        self.assertTrue(-90 <= home[0] <= 90)
        self.assertGreater(geometry["distance_km"], 1000)
        self.assertAlmostEqual((geometry["short_bearing"] + 180) % 360, geometry["long_bearing"])

    def test_logbook_and_adif(self):
        with tempfile.TemporaryDirectory() as folder:
            service = LogbookService(Path(folder) / "log.sqlite3")
            service.add("zl4ssb", "RE66", 14_074_000, "FT8", "-10", "-12", "test")
            output = service.export_adif(Path(folder) / "log.adi")
            text = output.read_text(encoding="utf-8")
            self.assertIn("<CALL:6>ZL4SSB", text)
            self.assertIn("<EOR>", text)

    def test_cat_and_beacons(self):
        broker = CatBroker(RadioStateService())
        self.assertEqual(broker.note_reconnect()["reconnect_attempts"], 1)
        stamp = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        beacon = BeaconScheduleService().snapshot(stamp)
        self.assertEqual(beacon["seconds_to_next"], 10)
        self.assertEqual(len(beacon["frequencies_mhz"]), 5)

    def test_propagation_missing_data_is_explicit(self):
        request = PropagationRequest((0, 0), (1, 1), 14_100_000,
                                     datetime.now(timezone.utc), 7)
        result = PropagationEngine().evaluate(request)
        self.assertEqual(result["status"], "unavailable")
        self.assertIsNone(result["path_confidence"])


if __name__ == "__main__":
    unittest.main()
