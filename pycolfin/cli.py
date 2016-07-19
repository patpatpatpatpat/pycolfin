# -*- coding: utf-8 -*-
import click

from .pycolfin import COLFin

from getpass import getpass


verbosity_help = """
1 = User ID, Last Login, Equity Value, Day Change
2 = Display all info from 1 and portfolio summary
3 = Display all info in 1 & 2 and detailed portfolio
"""


@click.command()
@click.option('-v', '--verbosity', default=3, type=click.IntRange(1, 3), help=verbosity_help)
def main(verbosity):
    user_id = getpass(prompt='User ID:')
    password = getpass(prompt='Password:')
    account = None

    try:
        account = COLFin(user_id, password, parser='html.parser')
    except Exception as e:
        click.echo(e.__str__())
        exit()

    if verbosity >= 1:
        account.fetch_account_summary()
        account.show_account_summary()
    if verbosity >= 2:
        account.fetch_portfolio_summary()
        account.show_portfolio_summary()
    if verbosity == 3:
        account.fetch_detailed_portfolio()
        account.show_detailed_stocks()
        account.show_detailed_mutual_fund()


if __name__ == "__main__":
    main()
