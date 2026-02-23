from datetime import datetime
import os
import sys
import time
from typing import List
import requests
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_result


def is_too_many_requests(response):
    too_many_requests = isinstance(response, requests.Response) and response.status_code == 429
    if too_many_requests:
        print(f'{datetime.now()} -- Too many requests, trying again in a moment')
    return too_many_requests


def get_apikey_from_env():
    name = 'API_KEY_MASSIVE'
    try:
        return os.environ[name]
    except KeyError as e:
        print(f'Could not find environment variable named {name} holding the\n' +
              'API key for https://api.massive.com, aborting.\n')
        raise e


def get_symbols(url: str) -> List[str]:
    response = requests.get(f'{url}/holdings')
    response.raise_for_status()
    holdings = response.json()
    epochms = int(time.time()) * 1000
    ids = []
    for h in holdings:
        if h['previous_close'] is None or epochms - h['previous_close']['t'] > 24 * 60 * 60 * 1000:
            ids.append(h['id'])
    return ids


def get_previous_close(symbol: str, apikey: str) -> dict[str, int]:
    # https://massive.com/docs/rest/stocks/aggregates/previous-day-bar
    print(f'{datetime.now()} -- Attempting to retrieve the previous closing price for {symbol}')
    query = f'https://api.massive.com/v2/aggs/ticker/{symbol}/prev?adjusted=true&apiKey={apikey}'
    response = make_throttled_request(query)
    response.raise_for_status()
    candlesticks = response.json()['results']
    return {
        't': candlesticks[-1]['t'],
        'price': candlesticks[-1]['c']
    }


@retry(
    stop=stop_after_attempt(2),
    wait=wait_fixed(60),
    retry=retry_if_result(is_too_many_requests)
)
def make_throttled_request(query):
    return requests.get(query)


def post_previous_close(symbol: str, url: str, previous_close: dict[str, int]) -> None:
    print(f'{datetime.now()} -- Attempting to update {symbol} with previous closing price')
    response = requests.get(f'{url}/holdings/{symbol}')
    response.raise_for_status()
    holding = response.json()
    holding.update({'previous_close': previous_close})
    response = requests.patch(f'{url}/holdings/{symbol}', json=holding)
    response.raise_for_status()


def cli():
    if len(sys.argv) != 2 or sys.argv[1] in ['-h', '--help']:
        print('Usage: get-prices <URL>\n' +
              '\n' +
              '   <URL>     URL for the holdings database server')
        return

    url = sys.argv[1]
    apikey = get_apikey_from_env()

    for symbol in get_symbols(url):
        previous_close = get_previous_close(symbol, apikey)
        post_previous_close(symbol, url, previous_close)


if __name__ == '__main__':
    cli()
