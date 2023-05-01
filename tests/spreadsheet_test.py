import math
import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import pandas
import numpy
import datetime
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from budgeter.spreadsheet import SpreadsheetCredentials, Spreadsheet


class TestSpreadsheet(unittest.TestCase):
    @patch('gspread.service_account')
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

    @patch('gspread.service_account')
    def test_get_parsed_data(self, mock_gspread_service_account):
        mock_gspread_service_account.return_value = MagicMock()
        # arrange
        expected = pandas.DataFrame({
            "Date": [
                datetime.datetime(2021, 1, 1),
                datetime.datetime(2021, 1, 2),
                datetime.datetime(2021, 1, 3)
            ],
            "Spend": [20, 10.50, math.nan],
        })
        credentials = SpreadsheetCredentials("credentials_path")
        spreadsheet = Spreadsheet(credentials, "spreadsheet_id")
        columns = [
            ['Date', '01/01/2021', '02/01/2021', '03/01/2021'],
            ['Spend', '£20.00', '£10.50', 'garbage'],
            ['Category', 'Food', 'Travel', 'garbage']
        ]
        spreadsheet.spreadsheet.sheet1.col_values = MagicMock(
            side_effect=lambda i: columns[i - 1]
        )

        # act
        actual = spreadsheet.get_parsed_data()

        # assert
        self.assertEqual(expected["Date"].dtype, actual["Date"].dtype)
        self.assertEqual(expected["Spend"].dtype, actual["Spend"].dtype)
        self.assertEqual(expected["Date"].tolist(), actual["Date"].tolist())
        # nans do not compare equal, so...
        self.assertTrue(
            numpy.array_equal(
                expected["Spend"].fillna(0).tolist(),
                actual["Spend"].fillna(0).tolist()
            )
        )
