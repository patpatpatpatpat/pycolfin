# -*- coding: utf-8 -*-
import re
from collections import OrderedDict

from colorama import Fore, Style, init
from prettytable import PrettyTable
from robobrowser import RoboBrowser

init()

USER_ID_MAX_LENGTH = 9


def validate_user_id(user_id):
    """
    Raise an exception if the user_id does not follow the correct format.
    """
    invalid_user_id_msg = 'Invalid User ID. Please use a dash (-). Example: 1234-4567'
    user_id_pattern = re.compile('(\d{4}-\d{4})')

    if len(user_id) > USER_ID_MAX_LENGTH or not user_id_pattern.match(user_id):
        raise Exception(invalid_user_id_msg)


class COLFin(RoboBrowser):
    """
    TODO: describe me
    """
    # URLs for PLUS accounts
    urls = {
        'login': 'https://www.colfinancial.com/ape/Final2/login/l_login_small_NS3.asp',
    }
    plus_urls = {
        'user_summary': 'https://ph5.colfinancial.com/ape/FINAL2_STARTER/B_home_new/LOG.asp',
        'portfolio_summary': 'https://ph5.colfinancial.com/ape/FINAL2_STARTER/B_home_new/TABPORTFOLIO.asp',
        'detailed_portfolio': 'https://ph5.colfinancial.com/ape/FINAL2_STARTER/trading_PCA3/As_CashBalStockPos_MF.asp',
        # investment guide
    }
    non_plus_urls = {
        'user_summary': 'https://ph16.colfinancial.com/ape/FINAL2_STARTER/B_home_new/LOG.asp',
        'detailed_portfolio': 'https://ph16.colfinancial.com/ape/FINAL2_STARTER/trading_PCA3/As_CashBalStockPos_MF.asp',
        'investment_guide': 'https://ph16.colfinancial.com/ape/FINAL2_STARTER/Research/INVGUIDE_Mid.asp',
    }
    # The values are the exact strings present in the error pages.
    error_messages = {
        'server_error': 'Server error.',
        'session_expired': 'Your session has timed out.',
        'invalid_login': 'Invalid / Not Authorized to Log-in',
    }

    def __init__(self, user_id, password, **kwargs):
        super(COLFin, self).__init__(**kwargs)
        self.login(user_id, password)

    def check_page_for_errors(self):
        if self.response.status_code == 500:
            raise Exception(self.error_messages['server_error'])
        elif self.error_messages['session_expired'] in self.parsed.text:
            raise Exception(self.error_messages['session_expired'])

    def open(self, *args, **kwargs):
        super().open(*args, **kwargs)
        self.check_page_for_errors()

    def login(self, user_id, password):
        """
        How colfinancial's user login works

        Step 1: User ID and password are entered in the form (first) in the login page.
        Step 2: When the form is submitted, it redirects to another page which
                contains another form (second). The credentials used in the first form are transferred to the second form.
        Step 3: Once the second form is submitted, colfinancial checks if the
                credentials are valid. If authorized to log in, page redirects
                to homepage. If not authorized, an alert containing an error
                message is showed.
        """
        validate_user_id(user_id)
        user1, user2 = user_id.split('-')
        # Step 1
        self.open(self.urls['login'])
        first_form = self.get_form('login')
        first_form['txtUser1'] = user1
        first_form['txtUser2'] = user2
        first_form['txtPassword'] = password
        # Step 2
        self.submit_form(first_form)
        second_form = self.get_form('login')
        # Step 3
        self.submit_form(second_form)

        if self.error_messages['invalid_login'] in self.parsed.text:
            raise Exception(self.error_messages['invalid_login'])

    def get_color(self, string):
        """
        0 - Unchanged, use yellow
        Negative - Down for the day, use red
        Positive - Up for the day, use green
        """
        value = float(string.strip('%').replace(',', ''))
        if 0 == value:
            return Fore.YELLOW
        elif value < 0:
            return Fore.RED
        else:
            return Fore.GREEN

    def apply_color(self, string, color):
        """
        Prevents characters after the `string` to also have color
        """
        return color + string + Style.RESET_ALL

    def colorize(self, string):
        color = self.get_color(string)
        return self.apply_color(string, color)

    def fetch_account_summary(self):
        """
        Fetch the following data:
        - Account Number
        - Last Login
        """
        self.open(self.non_plus_urls['user_summary'])
        # misc contains: account type (starter|plus) & display type (e.g: real-time streaming)

        account_with_dash, account, last_login = [
            info.text for info
            in self.find_all('b')
        ]
        self.account_summary = OrderedDict()
        self.account_summary['Last Login'] = last_login

    def show_account_summary(self):
        if hasattr(self, 'account_summary') and self.account_summary:
            table = PrettyTable(self.account_summary.keys(), hrules=1)
            account_summary = self.account_summary.values()
            table.add_row(account_summary)
            print(table)
        else:
            raise Exception('No account data.')

    def fetch_portfolio_summary(self):
        """
        Fetch the table that contains the following:
        - Stock
        - Number of Shares
        - Last Trade Price
        - Change
        - % Change
        """
        self.open(self.plus_urls['portfolio_summary'])
        # First item is string 'My Stocks'; ignore
        _, *data = [
            val.text.strip() for val
            in self.find_all('font')
        ]
        # First 5 items are the columns, the rest are the stock data
        stocks_data = data[5:]
        self.portfolio_summary = []
        portfolio_summary_cols = [
            'Stock',
            'Shares',
            'Last',
            'Change',
            '%Change'
        ]
        stock_data = []
        for num, value in enumerate(stocks_data, start=1):
            stock_data.append(value)
            if num % len(portfolio_summary_cols) == 0:
                ord_dict = OrderedDict()
                for key, value in zip(portfolio_summary_cols, stock_data):
                    ord_dict[key] = value
                self.portfolio_summary.append(ord_dict)
                stock_data = []

    def show_portfolio_summary(self):
        if hasattr(self, 'portfolio_summary') and self.portfolio_summary:
            cols = self.portfolio_summary[0].keys()
            table = PrettyTable(cols, hrules=1)

            for stock in self.portfolio_summary:
                *stock_data, last, change, percent_change = stock.values()
                color = self.get_color(percent_change)
                stock_data.extend([
                    self.apply_color(last, color),
                    self.apply_color(change, color),
                    self.apply_color(percent_change, color),
                ])
                table.add_row(stock_data)
            print(table)
        else:
            raise Exception('No portfolio data')

    def fetch_detailed_portfolio(self):
        """
        Get detailed data about the account's equities and mutual funds.
        """
        self.open(self.non_plus_urls['detailed_portfolio'])
        cleaned_data = [
            d.strip().strip('|').strip()
            for d in self.parsed.text.splitlines()
            if d
        ]
        cleaned_data = [
            d for d in cleaned_data
            if d != 'BUY' and d != 'SELL'
        ]
        self._process_equity_data(cleaned_data)
        self._process_mutual_fund_data(cleaned_data)
        self._process_total_portfolio_data(cleaned_data)

    def _process_equity_data(self, data):
        equity_start = data.index('%Gain/Loss')  # Last item before stock data starts
        equity_end = data.index('TOTAL EQUITIES')
        _, *equity_data = data[equity_start:equity_end]
        detailed_stock_attrs = [
            'Stock Code',
            'Stock Name',
            'Portfolio %',
            'Market Price',
            'Average Price',
            'Total Shares',
            'Uncommitted Shares',
            'Market Value',
            'Gain/Loss',
            '%Gain/Loss',
        ]
        self.detailed_stocks = []

        stock_data = []
        for num, info in enumerate(equity_data, start=1):
            stock_data.append(info)
            if num % len(detailed_stock_attrs) == 0:
                ord_dict = OrderedDict()
                for key, value in zip(detailed_stock_attrs, stock_data):
                    ord_dict[key] = value
                self.detailed_stocks.append(ord_dict)
                stock_data = []

        _, self.total_equities, _, self.total_equities_gain_loss = data[equity_end:][:4]

    def _process_mutual_fund_data(self, data):
        mf_start = data.index('MUTUAL FUNDS')
        mf_end = data.index('TOTAL MUTUAL FUNDS')
        mf_table = data[mf_start:mf_end]
        mf_data_start = mf_table.index('%Gain/Loss')
        _, *all_mf = mf_table[mf_data_start:mf_end]  # Ignore %Gain/Loss
        detailed_mf_attrs = [
            'Fund Code',
            'Fund Name',
            'Portfolio %',
            'NAVPS',
            'Average Price',
            'Total Shares',
            'Uncomitted Shares',
            'Market Value',
            'Gain/Loss',
            '%Gain/Loss',
        ]
        self.detailed_mutual_funds = []

        mf_data = []
        for num, info in enumerate(all_mf, start=1):
            mf_data.append(info)
            if num % len(detailed_mf_attrs) == 0:
                ord_dict = OrderedDict()
                for key, value in zip(detailed_mf_attrs, mf_data):
                    ord_dict[key] = value
                self.detailed_mutual_funds.append(ord_dict)
                mf_data = []

        _, self.total_mf, _, self.total_mf_gain_loss = data[mf_end:][:4]

    def _process_total_portfolio_data(self, data):
        total_port_trade_value_index = data.index('TOTAL PORTFOLIO TRADE VALUE:') + 1
        port_gain_loss_percent_index = data.index('PORTFOLIO GAIN/LOSS:') + 1
        port_gain_loss_value_index = data.index('PORTFOLIO GAIN/LOSS:') + 2
        total_port_trade_value = data[total_port_trade_value_index]
        port_gain_loss_percent = data[port_gain_loss_percent_index]
        port_gain_loss_value = data[port_gain_loss_value_index]

        self.account_summary['Total Portfolio Trade Value'] = total_port_trade_value
        self.account_summary['Portfolio Gain/Loss (%)'] = self.colorize(port_gain_loss_percent)
        self.account_summary['Portfolio Gain/Loss'] = self.colorize(port_gain_loss_value)

    def show_detailed_stocks(self, annotate_with_col_guide=False):
        if hasattr(self, 'detailed_stocks') and self.detailed_stocks:
            cols = list(self.detailed_stocks[0].keys()) 

            if annotate_with_col_guide:
                cols.extend(['COL Rating', 'FV', 'Buy Below'])

            stocks_table = PrettyTable(cols, hrules=1)
            for stock in self.detailed_stocks:
                *stock_data, gain_loss, percent_gain_loss = list(stock.values())
                stock_data.extend([
                    self.colorize(gain_loss),
                    self.colorize(percent_gain_loss),
                ])

                if annotate_with_col_guide:
                    if guide := self.investment_guide.get(stock_data[0]):
                        stock_data.extend([
                            guide['col_rating'],
                            guide['col_fv'],
                            guide['buy_below'],
                        ])
                    else:
                        stock_data.extend([
                            'N/A',
                            'N/A',
                            'N/A',
                        ])

                stocks_table.add_row(stock_data)
            print(stocks_table)

            stocks_total_table = PrettyTable(
                ['Total Equities', 'Total Equities Gain/Loss'],
                hrules=1,
            )
            stocks_total_table.add_row([
                self.total_equities,
                self.colorize(self.total_equities_gain_loss),
            ])
            print(stocks_total_table)

        else:
            raise Exception('No detailed stocks data')

    def show_detailed_mutual_fund(self):
        if hasattr(self, 'detailed_mutual_funds') and self.detailed_mutual_funds:
            cols = self.detailed_mutual_funds[0].keys()
            mf_table = PrettyTable(cols, hrules=1)

            for mf in self.detailed_mutual_funds:
                *mf_data, gain_loss, percent_gain_loss = mf.values()
                mf_data.extend([
                    self.colorize(gain_loss),
                    self.colorize(percent_gain_loss),
                ])
                mf_table.add_row(mf_data)
            print(mf_table)

            mf_total_table = PrettyTable(
                ['Total Mutual Funds', 'Total Mutual Funds Gain/Loss'],
                hrules=1,
            )
            mf_total_table.add_row([
                self.total_mf,
                self.colorize(self.total_mf_gain_loss),
            ])
            print(mf_total_table)
        else:
            raise Exception('No detailed mutual fund data')

    def fetch_investment_guide(self) -> None:
        """
        Fetch the following data
        """
        self.open(self.non_plus_urls["investment_guide"])
        tr_elements = self.find_all('tr')

        guide = {}

        for tr in tr_elements:
            values = [
                element.text.strip() for element
                in tr.find_all('font')
            ]
            if not values:
                continue
            try:
                ticker, company_name, price, col_rating, _, col_fv, buy_below, *_ = values
            except ValueError:
                continue
            guide[ticker] = {
                "company_name": company_name,
                "price": price,
                "col_rating": col_rating,
                "col_fv": col_fv,
                "buy_below": buy_below,
            }
        self.investment_guide = guide
