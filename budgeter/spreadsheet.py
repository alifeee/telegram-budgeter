"""
This file is used to connect to the Google Sheets API.
"""
import re
import datetime
import gspread
from gspread.utils import ValueRenderOption, DateTimeOption
import pandas


def verifyurl(url: str):
    """Verifies that a url is a valid Google Sheets url.

    Args:
        url (str): The url to verify.

    Returns:
        bool: True if valid, False if not.
    """
    try:
        _ = gspread.utils.extract_id_from_url(url)
    except gspread.exceptions.NoValidUrlKeyFound:
        return False
    return True


def is_date(string: str):
    """Checks if a string is a valid date.

    Args:
        string (str): The string to check.

    Returns:
        bool: True if valid, False if not.
    """
    try:
        _ = datetime.datetime.strptime(string, "%d/%m/%Y")
    except ValueError:
        return False
    return True


def is_float(string: str):
    """Checks if a string is a valid float.

    Args:
        string (str): The string to check.

    Returns:
        bool: True if valid, False if not.
    """
    try:
        _ = float(string)
    except ValueError:
        return False
    return True


class Spreadsheet:
    """
    A class to connect to the Google Sheets API and view/edit spreadsheets.
    """

    def __init__(self, spreadsheet_client: gspread.client.Client, spreadsheet_url: str):
        """Creates a Spreadsheet object.

        Args:
            credentials (gspread.client.Client): A spreadsheet client created by gspread.service_account().
            spreadsheet_url (str): The url of the spreadsheet to connect to.
        """
        self.spreadsheet_client = spreadsheet_client
        self.spreadsheet_url = spreadsheet_url

    def get_sheet1(self):
        """Gets the first sheet of the spreadsheet.

        Returns:
            list[list]: The sheet as a 2d array. [row][column]
        """
        spreadsheet = self.spreadsheet_client.open_by_url(self.spreadsheet_url)
        return spreadsheet.sheet1.get_values(
            value_render_option=ValueRenderOption.unformatted,
            date_time_render_option=DateTimeOption.formated_string,
        )

    def verify_format(data: list[list]):
        """Verifies that the spreadsheet is formatted correctly, i.e.,
        - A1 and B1 are strings (column headers)
        - A2 onwards are dates
        - B2 onwards are floats
        - If An is empty, Bn is empty
        - If Bn is empty, An is empty

        Args:
            data (list[list]): The spreadsheet data, as a 2d array. [row][column]

        Returns:
            bool: True if the spreadsheet is formatted correctly, False if not.
            message: A message explaining why the spreadsheet is not formatted correctly.
        """
        # check empty
        if len(data) == 0:
            return True, None
        # check columns
        if len(data[0]) == 1:
            return False, "There is only one column. There should be two or zero."

        # check headers
        A1 = data[0][0]
        B1 = data[0][1]
        if not (isinstance(A1, str) and isinstance(B1, str)):
            return False, "A1 and B1 should be headers (strings)"
        if is_date(A1):
            return False, "A1 is a date. It should be a header (string)"
        if is_float(B1):
            return False, "B1 is a float. It should be a header (string)"

        # check data
        blank_row = False
        for row in data[1:]:
            A = row[0]
            B = row[1]
            if A is None and B is None:
                blank_row = True
                continue
            if blank_row:
                return False, "There is a blank row in the middle of the data."
            if not is_date(A):
                return False, "A2 onwards must be dates."
            if not is_float(B):
                return False, "B2 onwards must be floats."
            if A is None and B is not None:
                return False, "There is a date missing. Remove the spend or add a date."
            if B is None and A is not None:
                return (
                    False,
                    "There is a spend missing. Remove the date or add a spend.",
                )

        return True, None

    def get_spending_dataframe(self):
        """Gets the data as a pandas dataframe.
        Columns: "Date", "Spend"
        The first column is converted to a datetime object,
            the second column is stripped to a float.
        """
        data = self.get_sheet1()
        first_two_columns = [row[:2] for row in data]
        dframe = pandas.DataFrame(first_two_columns[1:], columns=["Date", "Spend"])
        dframe["Date"] = pandas.to_datetime(dframe["Date"], format="%d/%m/%Y")
        dframe["Spend"] = pandas.to_numeric(dframe["Spend"])
        return dframe

    def add_data(self, date: datetime.datetime, spend: float):
        """Adds a row to the spreadsheet.

        Args:
            date (datetime.datetime): The date to add.
            spend (float): The spend to add.

        Returns:
            Dataframe: The dataframe with the new row added.
        """
        date_str = date.strftime("%d/%m/%Y")
        self.spreadsheet.sheet1.append_row(
            [date_str, spend],
            value_input_option=gspread.worksheet.ValueInputOption.user_entered,
        )
        return self.get_parsed_data()


def main():
    # authentication
    CREDENTIALS_PATH = "google_credentials.json"
    SPREADSHEET_ID = "https://docs.google.com/spreadsheets/d/18OQs6uJgoyx3zrRhb9tcnBHxpUo4OyyFJKptJHMr-D0/edit"
    credentials = gspread.service_account(filename=CREDENTIALS_PATH)
    spreadsheet = Spreadsheet(credentials, SPREADSHEET_ID)

    # data
    df = spreadsheet.get_spending_dataframe()
    print(df)


if __name__ == "__main__":
    main()
