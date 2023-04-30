"""Tests for spreadsheet.py."""
import unittest
from unittest.mock import patch, MagicMock
from spreadsheet import SpreadsheetCredentials, Spreadsheet


class TestSpreadsheet(unittest.TestCase):
    @patch('spreadsheet.gspread.service_account')
    def test_get_cols(self, mock_gspread_service_account):
        mock_gspread_service_account.return_value = MagicMock()
        # arrange
        expected = [
            ['Date', 'Spend', "Category"],
            ['01/01/2021', '£10.00', 'Food'],
            ['02/01/2021', '£20.00', 'Travel']
        ]
        credentials = SpreadsheetCredentials("credentials_path")
        spreadsheet = Spreadsheet(credentials, "spreadsheet_id")
        # spreadsheet.spreadsheet.sheet1.col_values(i) returns a different column for each i
        columns = [
            ['Date', '01/01/2021', '02/01/2021'],
            ['Spend', '£10.00', '£20.00'],
            ['Category', 'Food', 'Travel']
        ]
        spreadsheet.spreadsheet.sheet1.col_values = MagicMock(
            side_effect=lambda i: columns[i - 1]
        )

        # act
        actual = spreadsheet.get_cols([1, 2, 3])

        # assert
        self.assertEqual(expected, actual)
