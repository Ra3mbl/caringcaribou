from __future__ import print_function
from .mock_ecu import MockEcuIso14229
from lib import iso14229_1
from lib import iso15765_2
import can
import unittest


class DiagnosticsOverIsoTpTestCase(unittest.TestCase):

    ARB_ID_REQUEST = 0x200C
    ARB_ID_RESPONSE = 0x200D

    def setUp(self):
        # Initialize virtual CAN bus
        can_bus = can.interface.Bus("test", bustype="virtual")
        mock_ecu_can_bus = can.interface.Bus("test", bustype="virtual")
        # Initialize mock ECU
        self.ecu = MockEcuIso14229(self.ARB_ID_REQUEST, self.ARB_ID_RESPONSE, bus=mock_ecu_can_bus)
        self.ecu.add_listener(self.ecu.message_handler)
        # Setup diagnostics on top of ISO-TP layer
        self.tp = iso15765_2.IsoTp(self.ARB_ID_REQUEST, self.ARB_ID_RESPONSE, bus=can_bus)
        self.diagnostics = iso14229_1.Iso14229_1(self.tp)
        # Reduce timeout value to speed up testing
        self.diagnostics.P3_CLIENT = 0.5

    def tearDown(self):
        if isinstance(self.diagnostics, iso14229_1.Iso14229_1):
            self.diagnostics.__exit__(None, None, None)
        if isinstance(self.tp, iso15765_2.IsoTp):
            self.tp.__exit__(None, None, None)

    def test_create_iso_14229_1(self):
        self.assertIsInstance(self.diagnostics, iso14229_1.Iso14229_1, "Failed to initialize ISO-14229-1")

    def test_read_data_by_identifier_success(self):
        result = self.diagnostics.read_data_by_identifier([MockEcuIso14229.REQUEST_POSITIVE])
        self.assertIsInstance(result, list, "Did not receive response")
        self.assertTrue(self.diagnostics.is_positive_response(result))

    def test_read_data_by_identifier_failure(self):
        result = self.diagnostics.read_data_by_identifier([MockEcuIso14229.REQUEST_NEGATIVE])
        self.assertIsInstance(result, list, "Did not receive response")
        self.assertFalse(self.diagnostics.is_positive_response(result))

    def test_write_data_by_identifier_success(self):
        result = self.diagnostics.write_data_by_identifier(MockEcuIso14229.REQUEST_IDENTIFIER_VALID,
                                                           MockEcuIso14229.REQUEST_VALUE)
        self.assertIsInstance(result, list, "Did not receive response")
        self.assertTrue(self.diagnostics.is_positive_response(result))

    def test_write_data_by_identifier_failure(self):
        result = self.diagnostics.write_data_by_identifier(MockEcuIso14229.REQUEST_IDENTIFIER_INVALID,
                                                           MockEcuIso14229.REQUEST_VALUE)
        self.assertIsInstance(result, list, "Did not receive response")
        self.assertFalse(self.diagnostics.is_positive_response(result))
