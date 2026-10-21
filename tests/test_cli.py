import unittest
from unittest.mock import patch
from src.cli import display_weather_information, is_valid_icao_id, run_cli
from src.weather import WeatherAPIError

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
        
    def test_invalid_icao_id_not_in_airport_database(self):
        self.assertFalse(is_valid_icao_id("ZZZZ"))

    def test_blank_icao_id(self):
        self.assertFalse(is_valid_icao_id(""))
        
class TestWeatherDisplay(unittest.TestCase):

    @patch("src.cli.get_taf")
    @patch("src.cli.get_metar")
    @patch("builtins.print")
    def test_weather_display(
        self, mock_print, mock_metar, mock_taf
    ):

        # Provide example METAR data
        mock_metar.return_value = {
            "temp_c": 20,
            "wind_dir_deg": 180,
            "wind_speed_kt": 10,
            "visibility_sm": 10,
            "altimeter_hpa": "1032.3 hPa",
            "flight_category": "VFR",
            "raw_text": "Example METAR"
        }

        # Provide example TAF data
        mock_taf.return_value = {
            "issued": "2026-10-16",
            "valid_from": "2026-10-16",
            "valid_to": "2026-10-17",
            "raw_text": "Example TAF"
        }

        display_weather_information("KJFK")

        # Verify METAR was requested
        mock_metar.assert_called_once_with("KJFK")

        # Verify TAF was requested
        mock_taf.assert_called_once_with("KJFK")

        # Verify weather information was displayed
        mock_print.assert_any_call("Temperature: 20 °C")
        mock_print.assert_any_call("Wind Speed: 10 knots")
        mock_print.assert_any_call("Flight Category: VFR")
        
    @patch("src.cli.get_taf", return_value=None)
    @patch("src.cli.get_metar", return_value=None)
    @patch("builtins.print")
    def test_missing_weather_data(
        self, mock_print, mock_metar, mock_taf
    ):

        display_weather_information("KJFK")

        mock_print.assert_any_call(
            "No current weather data is available for this ICAO ID."
        )

        mock_print.assert_any_call(
            "No forecast data available for this ICAO ID."
        )

    @patch("src.cli.get_taf", return_value=None)
    @patch("src.cli.get_metar")
    @patch("builtins.print")
    def test_weather_api_error(
        self, mock_print, mock_metar, mock_taf
    ):

        # Simulate a failed API request
        mock_metar.side_effect = WeatherAPIError(
            "Connection failed"
        )

        display_weather_information("KJFK")

        mock_print.assert_any_call(
            "Unable to retrieve METAR: Connection failed"
        )

        # The program should still attempt the TAF
        mock_taf.assert_called_once_with("KJFK")

class TestCLI(unittest.TestCase):

    @patch("src.cli.display_weather_information")
    @patch("src.cli.distance_nm", return_value=2145.97)
    @patch("builtins.input", side_effect=["KJFK", "KLAX"])
    @patch("builtins.print")
    def test_valid_inputs(self, mock_print, mock_input, mock_distance, mock_weather):
        run_cli()

        mock_print.assert_any_call(
            "Enjoy your flight from KJFK to KLAX!"
        )
        # Verify distance calculation was called
        mock_distance.assert_called_once()

        # Verify weather was requested for both airports
        mock_weather.assert_any_call("KJFK")
        mock_weather.assert_any_call("KLAX")

        self.assertEqual(mock_weather.call_count, 2)
    
    # Test that the calculated distance is displayed
    @patch("src.cli.display_weather_information")
    @patch("src.cli.distance_nm", return_value=2145.97)
    @patch("builtins.input", side_effect=["KJFK", "KLAX"])
    @patch("builtins.print")
    def test_distance_display(
        self, mock_print, mock_input,
        mock_distance, mock_weather
    ):
        run_cli()

        mock_print.assert_any_call(
            "Distance Between Airports: 2145.97 nautical miles"
        )    
        
    @patch("builtins.input", side_effect=["", ""])
    @patch("builtins.print")
    def test_both_inputs_blank(self, mock_print, mock_input):
        run_cli()

        mock_print.assert_any_call(
            "Departure ICAO identifier cannot be empty."
        )

        mock_print.assert_any_call(
            "Destination ICAO identifier cannot be empty."
        )

    @patch("builtins.input", side_effect=["JFK", "LAX"])
    @patch("builtins.print")
    def test_both_inputs_invalid(self, mock_print, mock_input):
        run_cli()

        mock_print.assert_any_call(
            "Departure ICAO identifier is not a valid airport."
        )

        mock_print.assert_any_call(
            "Destination ICAO identifier is not a valid airport."
        )
        

    @patch("builtins.input", side_effect=["ZZZZ", "XXXX"])
    @patch("builtins.print")
    def test_nonexistent_airports(self, mock_print, mock_input):
        run_cli()

        mock_print.assert_any_call(
            "Departure ICAO identifier is not a valid airport."
        )

        mock_print.assert_any_call(
            "Destination ICAO identifier is not a valid airport."
        )
        
if __name__ == "__main__":
    unittest.main()