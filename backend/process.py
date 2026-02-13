import json
import sys
import pandas as pd


def main():
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        try:
            usecols = ['Trade Date', 'Transaction Type', 'Symbol', 'Shares', 'Share Price']
            df = pd.read_csv(filename, usecols=usecols)
        except FileNotFoundError:
            print(f"Error: The file '{filename}' was not found.")
    else:
        print("Usage: python process.py <filename>")

    namesMap = {
        'Trade Date': 'date',
        'Transaction Type': 'type',
        'Symbol': 'ticker',
        'Shares': 'shares',
        'Share Price': 'price'
    }
    df = df.rename(columns = namesMap)
    grouped  = df.groupby('ticker')
    objs = {
        'holdings': []
    }
    for name, group in grouped:
        obj = {
            'ticker': name,
            'transactions': group.to_dict(orient='records')
        }
        for t in obj['transactions']:
            del t['ticker']
            if t['type'] == 'Buy': t['type'] = 'BUY'
            if t['type'] == 'Sell': t['type'] = 'SELL'
            if t['type'] == 'SELL': t['shares'] *= -1

        objs['holdings'].append(obj)
    print(json.dumps(objs, indent=4))


if __name__ == "__main__":
    main()
