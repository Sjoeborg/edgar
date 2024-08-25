# Edgar Tool

## Description
Obtains all SEC filings as PDF files for the requested ticker symbols and form.

## Installation
To install the dependencies for this project, you need to have [Poetry](https://python-poetry.org/) installed. Once Poetry is installed, run the following command in the project directory:

```sh
poetry install
```

## Usage
### Command Line Arguments
- **`--tickers`**: List of ticker symbols to retrieve filings for. Default values are:
  - `AAPL`
  - `AMZN`
  - `GOOGL`
  - `GSCE`
  - `META`
  - `MSFT`
  - `NFLX`
  - `TSLA`
- **`--form`**: Type of form to retrieve. Default value is `10-K`.
- **`--last_filings`**: Number of forms to retrieve since the most recent one. Default value is `5`.

To download all `10-Q` forms for `AAPL`, `MSFT`, and `GOOGL`, run the following command:
```sh
poetry run python edgar/main.py --tickers AAPL MSFT GOOGL --form 10-Q
```

## Development
Run tests
```sh
poetry run pytest
```

Run lint + format
```sh
poetry run ruff format && poetry run ruff check --fix
```

