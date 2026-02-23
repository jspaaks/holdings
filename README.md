# Holdings

Visualization of current holdings based on Vanguard downloadable CSV data

## Stack

- frontend
    1. Vue
    1. Vite
    1. TypeScript
- backend
    1. Python data processing using Pandas to wrangle CSV to JSON
    1. json-server mocked server

## Frontend (dev setup)

```console
$ npm run dev
```

## Backend

Change directory into `backend/`.

```console
$ cd backend
```

Download the transactions spreadsheet from Vanguard, then use a spreadsheet program like Excel or LibreOffice Calc to remove the first rows of the downloaded CSV file `OfxDownload.csv`, such that it starts with row headers `Account Number`, `Trade Date`, `Settlement Date`, etc. Save this file as e.g. `data/transactions.csv`.

Create a Python virtual environment
```console
$ python3 -m venv venv
```

Activate the Python virtual environment
```console
$ source venv/bin/activate
```

Install dependencies and create command aliases `process-holdings` and `get-pricing`, both of which
we will use in a moment

```console
$ pip install .
```

Start processing the data from the CSV file

```console
$ process-holdings ./data/transactions.csv > ./data/db.json
```

For reference, `process-holdings` has a help text as well:

```console
$ process-holdings --help
Usage: process-holdings FILENAME

   FILENAME   Name of the file that contains the Vanguard
              transactions for each of your holdings
```

In a second terminal, start the JSON file server and let it watch for changes to the file

```console
$ ./node_modules/.bin/json-server data/db.json --port 3458  # or another port of your choosing
```

In order to show the previous day's closing prices in each graph, you can retrieve pricing data
from `api.massive.com`. This requires that you have an API key, which you can get by registering for
a free account on `massive.com`. Once you have the key, go back to the first terminal, create an
environment variable `API_KEY_MASSIVE` whose value is the key, like so:

```console
export API_KEY_MASSIVE=<your api key>
```

Then run

```console
$ get-pricing http://localhost:3458
```

assuming that port 3458 is where json-server is hosted.

For reference, `get-prices` also has a `--help`:

```console
$ get-prices --help
Usage: get-prices <URL>

   <URL>     URL for the holdings database server
```

It should output some text, and update the `data/db.json` file with the pricing information for the
previous trading day.

Now open your browser to `http://localhost:5173` or wherever you told Vite you want to host the
frontend. It should show images like this for each of the holdings from you transactions file:

![example of holding](sample.png)
