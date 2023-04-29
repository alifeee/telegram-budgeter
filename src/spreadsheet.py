"""
This file is used to connect to the Google Sheets API.
"""
import gspread
import pandas

gc = gspread.service_account(filename='google_credentials.json')

sh = gc.open_by_key("18OQs6uJgoyx3zrRhb9tcnBHxpUo4OyyFJKptJHMr-D0")

row_A = sh.sheet1.col_values(1)
row_B = sh.sheet1.col_values(2)

df = pandas.DataFrame([row_A, row_B]).transpose()

df.columns = ['A', 'B']

print(df)
