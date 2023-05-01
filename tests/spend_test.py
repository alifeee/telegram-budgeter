import unittest
from freezegun import freeze_time
import os
import sys
import pandas
import datetime
import numpy
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from budgeter.bothandlers.spend import get_first_day_without_data

class TestGetFirstDayWithoutData(unittest.TestCase):
    def test_simple_df(self):
        # Arrange
        df = pandas.DataFrame({
            "Date": ["01/01/2021", "02/01/2021", "03/01/2021"],
            "Spend": [20, 15, numpy.nan]
        })
        df["Date"] = pandas.to_datetime(df["Date"], format="%d/%m/%Y")
        expected = datetime.datetime(2021, 1, 3)

        # Act
        actual = get_first_day_without_data(df)

        # Assert
        self.assertEqual(expected, actual)

    def test_no_missing_data(self):
        # Arrange
        df = pandas.DataFrame({
            "Date": ["01/01/2021", "02/01/2021", "03/01/2021"],
            "Spend": [20, 15, 10]
        })
        df["Date"] = pandas.to_datetime(df["Date"], format="%d/%m/%Y")
        expected = datetime.datetime(2021, 1, 4)

        # Act
        actual = get_first_day_without_data(df)

        # Assert
        self.assertEqual(expected, actual)

    @freeze_time("2021-01-05")
    def test_empty_df(self):
        # Arrange
        df = pandas.DataFrame({
            "Date": [],
            "Spend": []
        })
        expected = datetime.datetime(2021, 1, 4)

        # Act
        actual = get_first_day_without_data(df)

        # Assert
        self.assertEqual(expected, actual)
