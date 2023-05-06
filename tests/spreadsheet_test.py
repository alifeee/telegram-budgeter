import math
import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import pandas
import numpy
import datetime
from gspread.client import Client

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from budgeter.spreadsheet import Spreadsheet


class TestSpreadsheet(unittest.TestCase):
    @patch("gspread.Client")
    def test_get_sheet1(self, mock_client):
        # arrange
        expected = [
            ["Date", "Spend", "Category"],
            ["01/01/2021", "£10.00", "Food"],
            ["02/01/2021", "£20.00", "Travel"],
        ]
        mock_worksheet = MagicMock()
        mock_worksheet.get_values = MagicMock(return_value=expected)
        mock_spreadsheet = MagicMock()
        mock_spreadsheet.sheet1 = mock_worksheet
        mock_client.open_by_url = MagicMock(return_value=mock_spreadsheet)

        # act
        spreadsheet = Spreadsheet(
            mock_client,
            "bogus url",
        )
        actual = spreadsheet.get_sheet1()

        # assert
        self.assertEqual(expected, actual)

    def test_verify_format_no_data(self):
        data = []
        valid, message = Spreadsheet.verify_format(data)
        self.assertTrue(valid, message)

    def test_verify_format_only_headers(self):
        data = [
            ["Date", "Spend"],
        ]
        valid, message = Spreadsheet.verify_format(data)
        self.assertTrue(valid, message)

    def test_verify_format_no_headers(self):
        data = [
            ["01/01/2021", "£10.00"],
            ["02/01/2021", "£20.00"],
        ]
        valid, message = Spreadsheet.verify_format(data)
        self.assertFalse(valid, message)

    def test_verify_format_bad_date(self):
        data = [
            ["Date", "Spend"],
            ["01/01/2021", "£10.00"],
            ["not a date", "£30.00"],
            ["04/01/2021", "£40.00"],
        ]
        valid, message = Spreadsheet.verify_format(data)
        self.assertFalse(valid, message)

    def test_verify_format_missing_date(self):
        data = [
            ["Date", "Spend"],
            ["01/01/2021", "£10.00"],
            [None, "£20.00"],
            ["", "£30.00"],
            ["04/01/2021", "£40.00"],
        ]
        valid, message = Spreadsheet.verify_format(data)
        self.assertFalse(valid, message)

    def test_verify_format_missing_spend(self):
        data = [
            ["Date", "Spend"],
            ["01/01/2021", "£10.00"],
            ["02/01/2021", None],
            ["03/01/2021", ""],
            ["04/01/2021", "£40.00"],
        ]
        valid, message = Spreadsheet.verify_format(data)
        self.assertFalse(valid, message)

    def test_verify_format_bad_spend(self):
        data = [
            ["Date", "Spend"],
            ["01/01/2021", "£10.00"],
            ["03/01/2021", "not a number"],
            ["04/01/2021", "£40.00"],
        ]
        valid, message = Spreadsheet.verify_format(data)
        self.assertFalse(valid, message)

    def test_verify_format_missing_row(self):
        data = [
            ["Date", "Spend"],
            ["01/01/2021", "£10.00"],
            [None, None],
            ["", ""],
            ["04/01/2021", "£40.00"],
        ]
        valid, message = Spreadsheet.verify_format(data)
        self.assertFalse(valid, message)

    def test_verify_format_not_enough_columns(self):
        data = [
            ["Date"],
            ["01/01/2021"],
            ["02/01/2021"],
        ]
        valid, message = Spreadsheet.verify_format(data)
        self.assertFalse(valid, message)

    def test_verify_format_valid(self):
        data = [
            ["Date", "Spend"],
            ["01/01/2021", 10.00],
            ["02/01/2021", 20.00],
        ]
        valid, message = Spreadsheet.verify_format(data)
        self.assertTrue(valid, message)
