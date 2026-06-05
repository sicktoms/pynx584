import unittest
from unittest import mock

from nx584 import api
from nx584 import event_queue


class Zone(object):
    number = 4
    name = "Garage"
    state = False
    condition_flags = []
    type_flags = []
    bypassed = False


class TestAPI(unittest.TestCase):
    def setUp(self):
        self.controller = mock.Mock()
        self.controller.zones = {4: Zone()}
        self.original_controller = api.CONTROLLER
        api.CONTROLLER = self.controller
        self.client = api.app.test_client()

    def tearDown(self):
        api.CONTROLLER = self.original_controller

    def test_bypass_requests_fresh_zone_status(self):
        response = self.client.put("/zones/4", json={"bypassed": True})

        self.assertEqual(200, response.status_code)
        self.controller.zone_bypass_toggle.assert_called_once_with(4)
        self.controller.get_zone_status.assert_called_once_with(4)

    def test_events_recovers_from_server_index_reset(self):
        self.controller.event_queue = event_queue.EventQueue(10)
        self.controller.event_queue.push({"type": "test"})

        response = self.client.get("/events?index=100&timeout=0")

        self.assertEqual(200, response.status_code)
        self.assertEqual([], response.get_json()["events"])
        self.assertEqual(1, response.get_json()["index"])
