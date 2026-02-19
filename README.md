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

Install dependencies and create command alias `process-holdings`

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

Deactivate Python environment, don't need it anymore

```console
$ deactivate
```

Start the JSON file server and let it watch for changes to the file

```console
$ ./node_modules/.bin/json-server data/db.json
```

## Frontend (dev setup)

```console
$ npm run dev
```
