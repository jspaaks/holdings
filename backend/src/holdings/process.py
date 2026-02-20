import json
import os
import sys
import pandas as pd


class Holdings:

    def __init__(self, input_filepath: str | os.PathLike):
        self._holdings = None
        self._read_transactions_from_csv(input_filepath)
        self._sort_by_date()
        self._remove_transactions_fifo()
        self._calc_cost()
        self._calc_shares()
        self._calc_shares_acc()
        self._calc_cost_per_share()
        self._calc_min_price()
        self._calc_max_price()
        self._add_previous_close_placeholder()

    def __str__(self):
        return json.dumps({
            '$schema': 'schema.json',
            'holdings': self._holdings
        }, sort_keys=True, indent=4)

    def _add_previous_close_placeholder(self):
        for holding in self._holdings:
            holding['previous_close'] = None
        return self

    def _calc_cost(self):
        for holding in self._holdings:
            holding['cost'] = sum([t['price'] * t['shares'] for t in holding['buys']])
        return self

    def _calc_cost_per_share(self):
        for holding in self._holdings:
            holding['cost_per_share'] = holding['cost'] / holding['shares']

    def _calc_max_price(self):
        for holding in self._holdings:
            holding['max_price'] = max([t['price'] for t in holding['buys']])

    def _calc_min_price(self):
        for holding in self._holdings:
            holding['min_price'] = min([t['price'] for t in holding['buys']])

    def _calc_shares(self):
        for holding in self._holdings:
            holding['shares'] = sum([t['shares'] for t in holding['buys']])

    def _calc_shares_acc(self):
        for holding in self._holdings:
            acc = 0
            for b in holding['buys']:
                b['shares_acc'] = acc
                acc += b['shares']

    def _read_transactions_from_csv(self, filepath: str | os.PathLike):
        # initialize _holdings
        self._holdings = []

        # try reading csv transaction data from file
        try:
            usecols = ['Trade Date', 'Transaction Type', 'Symbol', 'Shares', 'Share Price']
            df = pd.read_csv(filepath, usecols=usecols)
        except FileNotFoundError as e:
            print(f"Error: The file '{filepath}' was not found.")
            raise e

        # select only those rows that represent a buy or a sell
        df = df.query('`Transaction Type` == "Buy" or `Transaction Type` == "Sell"')

        # rename the column labels
        columns = {
            'Trade Date': 'date',
            'Transaction Type': 'type',
            'Symbol': 'ticker',
            'Shares': 'shares',
            'Share Price': 'price'
        }
        df = df.rename(columns=columns)

        # group by ticker symbol and wrangle transactions into an array
        # of dict where key `id` represents ticker symbol
        grouped = df.groupby('ticker')
        for index, (ticker, group) in enumerate(grouped):
            transactions = group.to_dict(orient='records')
            for t in transactions:
                del t['ticker']
                t['type'] = t['type'].upper()
                if t['type'] == 'SELL':
                    t['shares'] *= -1
            self._holdings.append({
                'id': ticker,
                'transactions': transactions
            })

    def _remove_transactions_fifo(self):
        for holding in self._holdings:
            shares_sold = sum(t['shares'] for t in holding['transactions'] if t['type'] == 'SELL')
            if shares_sold == 0:
                continue
            for t in holding['transactions']:
                if t['type'] != 'BUY':
                    continue
                delta = min(t['shares'], shares_sold)
                t['shares'] -= delta
                shares_sold -= delta
                if shares_sold <= 0:
                    break

            # remove zero-share transactions
            holding['transactions'] = list(filter(lambda t: t['shares'] > 0, holding['transactions']))

            # remove SELLs from transactions
            holding['transactions'] = list(filter(lambda t: t['type'] == 'BUY', holding['transactions']))

        for holding in self._holdings:
            # rename 'transactions' to 'buys'
            holding['buys'] = holding.pop('transactions')

            # remove the 'type' key from each transaction
            for t in holding['buys']:
                del t['type']

        # remove holdings that have no buys
        self._holdings = list(filter(lambda h: h['buys'], self._holdings))

    def _sort_by_date(self):
        for holding in self._holdings:
            holding['transactions'].sort(key=lambda t: t['date'])
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
