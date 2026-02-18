from datetime import date, timedelta
import json
import os
import sys
from typing import List

def get_apikey_from_env():
    name = 'API_KEY_MASSIVE'
    try:
        return os.environ[name]
    except KeyError as e:
        print(f'Could not find environment variable named {name} holding the\n' +
              'API key for https://api.massive.com, aborting.\n')
        raise e


def get_symbols(url: str) -> List[str]:
    mocked_holdings = [
        {
            'id': 'VOO',
            'previous_close': {
                'price': 22.81,
                't': 1770930000
            },
            'transactions': [],
        },
        {
            'id': 'RSP',
            'previous_close': None,
            'transactions': [],
        },
        {
            'id': 'EMBJ',
            'previous_close': {
                'price': 125.01,
                't': 1750930000
            },
            'transactions': [],
        }
    ]
    return [h['id'] for h in mocked_holdings if h['previous_close'] is None or h['previous_close']['t'] < 1770930000]

def get_last_trading_minute() -> tuple[a,b]:
    # use endpoint 'https://api.massive.com/v2/aggs/ticker/AAPL/range/1/day/2026-02-04/2026-02-18?adjusted=true&sort=asc&limit=15&apiKey=apikey'
    today = date.today()
    two_weeks_ago = today - timedelta(days=14)
    apikey = get_apikey_from_env()
    query = f'https://api.massive.com/v2/aggs/ticker/AAPL/range/1/day/{two_weeks_ago}/{today}?adjusted=true&sort=asc&limit=15&apiKey={apikey}'
    print(query)

    # use requests to do the query
    # take results[resultCount-1].t, add 16*60*60*1000 milliseconds to get to 16:00 EST, call it 'end'
    # subtract 59 * 1000 to get the minute before, call it 'start'
    return {
        'start': 1771016340000,
        'end': 1771016400000
    }
    # query = f'https://api.massive.com/v2/aggs/ticker/AAPL/range/1/minute/{a}/{b}?adjusted=true&sort=asc&limit=1&apiKey={apikey}'


def get_previous_close(symbol: str, apikey: str, t: int):
    print('Attempting to GET previous close from api.massive.com')


def post_previous_close():
    print('Attempting to POST previous close to cache')


def main():
    if len(sys.argv) != 2:
        print('Usage: python3 get_prices.py <URL>\n' +
              '\n' +
              '   <URL>     URL for the holdings database server')
        return

    URL = sys.argv[1]

    minute = get_last_trading_minute()

    for symbol in get_symbols(URL):
        # get_previous_close(symbol, APIKEY)
        # post_previous_close(symbol, price, URL)
        print(symbol)


if __name__ == '__main__':
    main()
