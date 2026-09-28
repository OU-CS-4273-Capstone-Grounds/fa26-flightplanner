import unittest
from unittest.mock import patch
from src.cli import is_valid_icao_id, run_cli

class TestICAOValidation(unittest.TestCase):

    def test_valid_icao_id(self):
        self.assertTrue(is_valid_icao_id("KJFK"))
        self.assertTrue(is_valid_icao_id("KLAX"))

    def test_invalid_icao_id_too_short(self):
        self.assertFalse(is_valid_icao_id("JFK"))

    def test_invalid_icao_id_too_long(self):
        self.assertFalse(is_valid_icao_id("KJFKX"))

    def test_invalid_icao_id_contains_numbers(self):
        self.assertFalse(is_valid_icao_id("K12F"))

    def test_invalid_icao_id_contains_special_characters(self):
        self.assertFalse(is_valid_icao_id("K-JF"))

    def test_blank_icao_id(self):
        self.assertFalse(is_valid_icao_id(""))
        
class TestCLI(unittest.TestCase):

    @patch("builtins.input", side_effect=["KJFK", "KLAX"])
    @patch("builtins.print")
    def test_valid_inputs(self, mock_print, mock_input):
        run_cli()

        mock_print.assert_called_with(
            "Enjoy your flight from KJFK to KLAX!"
        )
        
    @patch("builtins.input", side_effect=["", ""])
    @patch("builtins.print")
    def test_both_inputs_blank(self, mock_print, mock_input):
        run_cli()

        mock_print.assert_any_call(
            "Departure ICAO identifier cannot be empty."
        )
        
        mock_print.assert_any_call(
            "Departure ICAO identifier must contain exactly 4 letters."
        )

        mock_print.assert_any_call(
            "Destination ICAO identifier cannot be empty."
        )
        
        mock_print.assert_any_call(
            "Destination ICAO identifier must contain exactly 4 letters."
        )

    @patch("builtins.input", side_effect=["JFK", "LAX"])
    @patch("builtins.print")
    def test_both_inputs_invalid(self, mock_print, mock_input):
        run_cli()

        mock_print.assert_any_call(
            "Departure ICAO identifier must contain exactly 4 letters."
        )

        mock_print.assert_any_call(
            "Destination ICAO identifier must contain exactly 4 letters."
        )
        
if __name__ == "__main__":
    unittest.main()