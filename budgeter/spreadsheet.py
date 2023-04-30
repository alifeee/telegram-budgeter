"""
This file is used to connect to the Google Sheets API.
"""
import gspread
import pandas


class SpreadsheetCredentials:
    """
    A class to store the credentials for the Google Sheets API.
    """

    def __init__(self, credentials_path: str):
        self.gspread_credentials = gspread.service_account(
            filename=credentials_path
        )


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
        columns = [
            self.spreadsheet.sheet1.col_values(col)
            for col in column_numbers
        ]
        columns_2d = [list(x) for x in zip(*columns)]

        if ignore_first_row:
            return columns_2d[1:]
        return columns_2d


if __name__ == '__main__':
    # authentication
    CREDENTIALS_PATH = "google_credentials.json"
    SPREADSHEET_ID = "18OQs6uJgoyx3zrRhb9tcnBHxpUo4OyyFJKptJHMr-D0"
    credentials = SpreadsheetCredentials(CREDENTIALS_PATH)
    spreadsheet = Spreadsheet(credentials, SPREADSHEET_ID)

    # data
    cols = spreadsheet.get_cols([1, 2])

    # dataframe conversion
    df = pandas.DataFrame(cols[1:], columns=['Date', 'Spend'])
    df['Date'] = pandas.to_datetime(df['Date'], format='%d/%m/%Y')
    df['Spend'] = df['Spend'].str.strip('£').astype(float)

    print(df)
