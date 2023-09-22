import json
import os

import pandas as pd
import requests
from consts import DEFAULT_FILING_AMOUNT, XBLR_CONVERTER_API_ENDPOINT
from dotenv import load_dotenv
from sec_api import QueryApi

load_dotenv()

SEC_API_KEY = os.environ["SEC_API_KEY"]


class FilingData:

    def __init__(
        self, ticker: str, uid: str, company_name: str, form_type: str, filed_date: str, link: str, end_date: str
    ):
        self.ticker = ticker
        self.uid = uid
        self.company_name = company_name
        self.form_type = form_type  # todo - enum?
        self.filed_date = filed_date  # todo - change to datetime
        self.link = link
        self.end_date = end_date  # todo - change to datetime

        self.xbrl_json = {}

    def parse_xbrl_json(self):
        if self.xbrl_json:
            print("XBLR was already parsed for this filing! skipping...")
            return

        xblr_convert_url = XBLR_CONVERTER_API_ENDPOINT + "?htm-url=" + self.link + "&token=" + SEC_API_KEY
        xblr_convert_response = requests.get(xblr_convert_url)
        xblr_convert_response.raise_for_status()

        self.xbrl_json = json.loads(xblr_convert_response.text)

    def get_income_statement(self):
        assert self.xbrl_json, "XBLR must be parsed before"

        income_statement_store = {}

        # iterate over each US GAAP item in the income statement
        for us_gaap_item in self.xbrl_json["StatementsOfIncome"]:
            values = []
            indicies = []

            for fact in self.xbrl_json["StatementsOfIncome"][us_gaap_item]:
                if "segment" not in fact:
                    index = fact["period"]["startDate"] + "-" + fact["period"]["endDate"]

                    if index not in indicies:
                        values.append(fact["value"])
                        indicies.append(index)

            income_statement_store[us_gaap_item] = pd.Series(values, index=indicies)

        income_statement_df = pd.DataFrame(income_statement_store).T
        return income_statement_df

    def get_balance_sheet(self):
        # todo
        balance_sheet_store = {}

        for usGaapItem in xbrl_json['BalanceSheets']:
            values = []
            indicies = []

            for fact in xbrl_json['BalanceSheets'][usGaapItem]:
                # only consider items without segment.
                if 'segment' not in fact:
                    index = fact['period']['instant']

                    # avoid duplicate indicies with same values
                    if index in indicies:
                        continue

                    # add 0 if value is nil
                    if "value" not in fact:
                        values.append(0)
                    else:
                        values.append(fact['value'])

                    indicies.append(index)

                balance_sheet_store[usGaapItem] = pd.Series(values, index=indicies)

        balance_sheet = pd.DataFrame(balance_sheet_store)
        # switch columns and rows so that US GAAP items are rows and each column header represents a date instant
        return balance_sheet.T

    balance_sheet = get_balance_sheet(xbrl_json)


def parse_query_results_to_filing_data(result: dict) -> list[FilingData]:
    return [
        FilingData(
            ticker=filing.get("ticker"),
            uid=filing.get("id"),
            company_name=filing.get("companyName"),
            form_type=filing.get("formType"),
            filed_date=filing.get("filedAt"),
            link=filing.get("linkToHtml"),
            end_date=filing.get("PeriodOfReport"),
        )
        for filing in result.get("filings")
    ]


def fetch_filings(ticker: str, start: int = 0, end: int = DEFAULT_FILING_AMOUNT):
    query_api = QueryApi(api_key=SEC_API_KEY)

    query = {
        "query": {"query_string": {"query": f'(formType:"10-Q" OR formType:"10-K") AND ticker:{ticker}'}},
        "from": f"{start}",
        "size": f"{end}",  # todo - support fetch all functionality
        "sort": [{"filedAt": {"order": "desc"}}],
    }

    query_result = query_api.get_filings(query)
    return parse_query_results_to_filing_data(query_result)


if __name__ == "__main__":
    apple_filings = fetch_filings("AAPL")

    last_apple_filing = apple_filings[-1]

    last_apple_filing.parse_xbrl_json()

    income_statement = last_apple_filing.get_income_statement()

