import base64
import json
import logging
import os

import argparse
import httpx
from selenium import webdriver
from selenium.webdriver.common.by import By


logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

api_headers = {
    'User-Agent': 'SjoborgAB martin@sjoborg.org',
    'Accept-Encoding': 'gzip, deflate',
    'Host': 'data.sec.gov',
}

ticker_page = 'https://www.sec.gov/files/company_tickers.json'
submission_endpoint = 'https://data.sec.gov'
form_endpoint = 'https://www.sec.gov/Archives/edgar/data'
output_dir = 'output'

default_tickers = ['AAPL', 'MSFT', 'GOOGL', 'META', 'AMZN', 'NFLX', 'TSLA', 'GSCE']
default_form = '10-K'
last_n_filings = 5


def get_ticker_cik_map(driver: webdriver.Chrome) -> dict[str, str]:
    """
    Obtains a bi-directional dictionary, mapping company ticker symbols to 10-digit CIK numbers and vice versa.
    """
    # Get the ticker-cik table from the source of the page
    driver.get(f'view-source:{ticker_page}')
    table_element = driver.find_element(By.TAG_NAME, 'table')
    table = json.loads(table_element.text)

    map = {}
    for _, v in table.items():
        ticker = v['ticker']
        full_cik = str(v['cik_str']).zfill(10)
        map[ticker] = full_cik
        map[full_cik] = ticker

    return map


def get_forms(cik: str, ticker: str, form: str) -> list[str]:
    """
    Obtains the URLs of all submitted forms for a given CIK number from the Edgar API.
    """
    r = httpx.get(
        f'{submission_endpoint}/submissions/CIK{cik}.json', headers=api_headers
    )
    assert r.status_code == 200, f'HTTP {r.status_code}: Edgar API returned an error.'

    try:
        recent_filings = r.json()['filings']['recent']
    except KeyError:
        logger.warning(f'No filings found for {ticker}.')
        return []

    # Find all URLs for the specified form
    forms: list[str] = []
    if 'form' not in recent_filings:
        logger.warning(f'No form data found for {ticker}.')
        return forms

    for i, f in enumerate(recent_filings['form']):
        if f == form:
            try:
                accession_number = recent_filings['accessionNumber'][i]
                document_name = recent_filings['primaryDocument'][i]
            except (IndexError, KeyError):
                logger.warning(f'No {form} forms found for {ticker}.')
                return forms
            formatted_accession_number = accession_number.replace('-', '')
            forms.append(
                f'{form_endpoint}/{cik}/{formatted_accession_number}/{document_name}'
            )

    return forms


def get_pdf_page(url: str, directory: str, driver: webdriver.Chrome) -> None:
    """
    Saves a PDF page to a specified directory. Name of the file is the name of the htm page without the ticker.
    """
    # Get the name of the file without the ticker and remove the .htm extension
    filename = url[url.rfind('-') + 1 : url.find('.htm')]

    if not os.path.exists(directory):
        os.makedirs(directory)

    if not os.path.exists(f'{directory}/{filename}.pdf'):
        driver.get(url)
        pdf_string = driver.print_page()

        with open(f'{directory}/{filename}.pdf', 'wb') as f:
            f.write(base64.b64decode(pdf_string))


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Retrieve forms as PDF files for one or more tickers'
    )
    parser.add_argument(
        '--tickers',
        nargs='+',
        default=default_tickers,
        help=f'List of ticker symbols to retrieve filings for. DEFAULT: {", ".join(default_tickers)}',
    )
    parser.add_argument(
        '--form', default=default_form, help=f'Form type to retrieve (default: {default_form}).'
    )
    parser.add_argument(
        '--last_filings', default=last_n_filings, help=f'Number of filings to retrieve (default: {last_n_filings}).'
    )
    return parser.parse_args()


def initialize_driver() -> webdriver.Chrome:
    return webdriver.Chrome()


def process_tickers(driver, tickers, form, last_filings):
    logger.info(f"Retrieving all {form} forms for {', '.join(tickers)}")
    cik_map = get_ticker_cik_map(driver)
    ciks = [cik_map[ticker] for ticker in tickers if ticker in cik_map]
    logger.info(f'Obtained {len(ciks)} out of {len(tickers)} CIKs.')
    if len(ciks) < len(tickers):
        logger.warning('Some CIKs could not be found, check the ticker list.')

    for cik in ciks:
        ticker = cik_map[cik]
        form_list = get_forms(cik, ticker, form)
        logger.info(f'Found {len(form_list)} {form} forms for {ticker}.')
        for form_url in form_list[0:min(last_filings, len(form_list))]:
            get_pdf_page(
                url=form_url, directory=f'{output_dir}/{ticker}/{form}', driver=driver
            )


def main():
    args = parse_arguments()
    driver = initialize_driver()
    try:
        process_tickers(driver, args.tickers, args.form, args.last_filings)
    finally:
        driver.quit()


if __name__ == '__main__':
    main()
