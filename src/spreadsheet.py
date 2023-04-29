"""
This file is used to connect to the Google Sheets API.
"""
import gspread
import pandas


class Spreadsheet:
    """
    A class to connect to the Google Sheets API and view/edit spreadsheets.
    """

    def __init__(self, credentials_path, spreadsheet_id):
        self.gspread_credentials = gspread.service_account(
            filename=credentials_path)
        self.spreadsheet = self.gspread_credentials.open_by_key(spreadsheet_id)

    def get_cols_as_df(self, column_numbers: list):
        """Gets the specified columns as a dataframe.

        Args:
            column_numbers (list of ints): The column numbers to get. Starts at 1.

        Returns:
            pandas.DataFrame: The columns as a dataframe.
        """
        sheet = self.spreadsheet.sheet1
        columns = [sheet.col_values(col) for col in column_numbers]

        dataframe = pandas.DataFrame(columns).transpose()

        return dataframe


if __name__ == '__main__':
    CREDENTIALS_PATH = "google_credentials.json"
    SPREADSHEET_ID = "18OQs6uJgoyx3zrRhb9tcnBHxpUo4OyyFJKptJHMr-D0"

    ss = Spreadsheet(CREDENTIALS_PATH, SPREADSHEET_ID)

    df = ss.get_cols_as_df([1, 2])
    print(df)
