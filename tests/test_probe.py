import json
import unittest
from unittest.mock import MagicMock, patch

import probe_runtime


class ProbeTests(unittest.TestCase):
    def test_nested_audio_report_excludes_unrequested_data(self):
        reply = {"pump_calls": 50, "underruns": 3, "unrequested": "not retained",
                 "out": {"active": 1, "fill_ms": 40.5, "underruns": 2,
                         "unrequested": "not retained"}, "taps": ["not retained"]}
        report = probe_runtime.select_fields(reply, probe_runtime.FIELDS["audio_stats"])
        self.assertEqual(report, {"pump_calls": 50, "underruns": 3,
                                  "out": {"active": 1, "fill_ms": 40.5, "underruns": 2}})

    def test_request_reassembles_status_and_filters_response(self):
        reply = json.dumps({"id": 1, "ok": True, "frame": 10, "unrequested": "not retained"}).encode()
        sock = MagicMock()
        sock.recv.side_effect = [reply[:15], reply[15:]]
        with patch.object(probe_runtime.socket, "create_connection") as connect:
            connect.return_value.__enter__.return_value = sock
            self.assertEqual(probe_runtime.request(4370, "frame"), {"frame": 10})

    def test_commands_outside_allowlist_never_connect(self):
        with patch.object(probe_runtime.socket, "create_connection") as connect:
            with self.assertRaisesRegex(ValueError, "allowlist"):
                probe_runtime.request(4370, "read_memory")
            connect.assert_not_called()

    def test_guest_speed_uses_frame_delta_and_elapsed_wall_time(self):
        with patch.object(probe_runtime, "request", side_effect=[{"frame": 100}, {"frame": 700}]), \
             patch.object(probe_runtime.time, "monotonic", side_effect=[10.0, 20.0]), \
             patch.object(probe_runtime.time, "sleep") as sleep:
            result = probe_runtime.sample_speed(4370, 10)
        sleep.assert_called_once_with(10)
        self.assertEqual(result["guest_frames"], 600)
        self.assertEqual(result["guest_frames_per_second"], 60)
        self.assertAlmostEqual(result["ntsc_speed_percent"], 100.1)

    def test_counter_reset_is_not_reported_as_speed(self):
        with patch.object(probe_runtime, "request", side_effect=[{"frame": 700}, {"frame": 100}]), \
             patch.object(probe_runtime.time, "monotonic", side_effect=[10.0, 20.0]), \
             patch.object(probe_runtime.time, "sleep"):
            with self.assertRaisesRegex(ValueError, "restarted"):
                probe_runtime.sample_speed(4370, 10)
