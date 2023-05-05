"""
This file is used to connect to the Google Sheets API.
"""
import re
import datetime
import gspread
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


class SpreadsheetCredentials:
    """
    A class to store the credentials for the Google Sheets API.
    """

    def __init__(self, credentials_path: str):
        self.gspread_credentials = gspread.service_account(filename=credentials_path)


class Spreadsheet:
    """
    A class to connect to the Google Sheets API and view/edit spreadsheets.
    """

    def __init__(self, credentials: SpreadsheetCredentials, spreadsheet_url: str):
        self.spreadsheet = credentials.gspread_credentials.open_by_url(spreadsheet_url)

    def get_cols(self, column_numbers: list, ignore_first_row=False):
        """Gets the specified columns as a 2d array.

        Args:
            column_numbers (list of ints): The column numbers to get. Starts at 1.

        Returns:
            list of lists: The columns as a 2d array.
        """
        columns = [self.spreadsheet.sheet1.col_values(col) for col in column_numbers]
        columns_2d = [list(x) for x in zip(*columns)]

        if ignore_first_row:
            return columns_2d[1:]
        return columns_2d

    def get_parsed_data(self):
        """Gets the data as a pandas dataframe.
        The first column is converted to a datetime object,
            the second column is stripped and converted to a float.
        """
        cols = self.get_cols([1, 2])
        dframe = pandas.DataFrame(cols[1:], columns=["Date", "Spend"])
        dframe["Date"] = pandas.to_datetime(dframe["Date"], format="%d/%m/%Y")
        dframe["Spend"] = dframe["Spend"].map(lambda x: re.sub(r"[^0-9\.]", "", x))
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
    SPREADSHEET_ID = "18OQs6uJgoyx3zrRhb9tcnBHxpUo4OyyFJKptJHMr-D0"
    credentials = SpreadsheetCredentials(CREDENTIALS_PATH)
    spreadsheet = Spreadsheet(credentials, SPREADSHEET_ID)

    # data
    columns = spreadsheet.get_cols([1, 2])

    # dataframe conversion
    df = pandas.DataFrame(columns[1:], columns=["Date", "Spend"])
    df["Date"] = pandas.to_datetime(df["Date"], format="%d/%m/%Y")
    df["Spend"] = df["Spend"].str.strip("£").astype(float)

    print(df)


if __name__ == "__main__":
    main()
