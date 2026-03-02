import json
import os
import sys
from pathlib import Path
import pandas as pd


class Holdings:

    def __init__(self, input_filepath: str | os.PathLike):
        self._skiprows = 2
        self._sheet = None
        self._holdings = None

        self._read_from_csv(input_filepath)
        self._rename_sheet_column_labels()
        self._group_by_ticker()
        self._reformat_dates()
        self._sort_holdings_by_date()

        self._calc_cost()
        self._calc_shares()
        self._calc_cost_per_share()
        self._calc_min_price()
        self._calc_max_price()
        self._add_previous_close_placeholder()

    def __str__(self):
        return json.dumps({
            '$schema': 'schema.json',
            'holdings': self._holdings,
        }, sort_keys=True, indent=4)

    def _add_previous_close_placeholder(self):
        for holding in self._holdings:
            holding['previous_close'] = None
        return self

    def _calc_cost(self):
        for holding in self._holdings:
            holding['cost'] = sum([ell['price'] * ell['shares'] for ell in holding['lots']])
        return self

    def _calc_cost_per_share(self):
        for holding in self._holdings:
            holding['cost_per_share'] = holding['cost'] / holding['shares']
        return self

    def _calc_max_price(self):
        for holding in self._holdings:
            holding['max_price'] = max([ell['price'] for ell in holding['lots']])

    def _calc_min_price(self):
        for holding in self._holdings:
            holding['min_price'] = min([ell['price'] for ell in holding['lots']])

    def _calc_shares(self):
        for holding in self._holdings:
            holding['shares'] = sum([ell['shares'] for ell in holding['lots']])

    def _group_by_ticker(self):
        # group by ticker symbol and wrangle transactions into an array
        # of dict where key `id` represents ticker symbol
        self._holdings = []

        # select only those rows that represent a buy or a sell and group them by ticker symbol
        grouped = self._sheet.groupby('ticker')

        for ticker, group in grouped:
            lots = group.to_dict(orient='records')
            for index, ell in enumerate(lots):
                del ell['ticker']
                ell['order'] = index
            self._holdings.append({
                'id': ticker,
                'lots': lots
            })

    def _read_from_csv(self, filepath: str | os.PathLike):
        filepath = Path(filepath)
        if not filepath.is_file():
            raise FileNotFoundError(f"File not found: '{filepath}'")

        usecols = ['Acquired date', 'Symbol/CUSIP', 'Quantity', 'Cost per share']
        self._sheet = pd.read_csv(filepath, usecols=usecols, skiprows=self._skiprows)

    def _reformat_dates(self):
        for holding in self._holdings:
            for ell in holding['lots']:
                month, day, year = ell['date'].split('/')
                ell['date'] = f'{year}-{month}-{day}'

    def _rename_sheet_column_labels(self):
        columns = {
            'Acquired date': 'date',
            'Symbol/CUSIP': 'ticker',
            'Quantity': 'shares',
            'Cost per share': 'price',
        }
        self._sheet.rename(columns=columns, inplace=True)

    def _sort_holdings_by_date(self):
        for holding in self._holdings:
            holding['lots'].sort(key=lambda ell: (ell['date'], ell['order']))
        return self


def cli():
    if len(sys.argv) != 2 or sys.argv[1] in ['-h', '--help']:
        print(
            "Usage: process-holdings FILENAME\n" +
            "\n" +
            "   FILENAME   Name of the file that contains the Vanguard\n" +
            "              transactions for each of your holdings")
        return

    holdings = Holdings(sys.argv[1])
    print(holdings)


if __name__ == "__main__":
    cli()
