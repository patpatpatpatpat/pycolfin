# -*- coding: utf-8 -*-
import os
from getpass import getpass

import click

from .pycolfin import COLFin


verbosity_help = """
1 = User ID, Last Login
2 = Display all info from 1 and portfolio summary
3 = Display all info in 1 & 2 and detailed portfolio
"""
use_env_vars_help = """
Use USER_ID and PASSWORD from environment variables.
Not recommended if you are using a shared computer!
(This is like storing bank credentials in a text file)
"""


@click.command()
@click.option('--use-env-vars', is_flag=True, default=False, help=use_env_vars_help)
@click.option('-v', '--verbosity', default=3, type=click.IntRange(1, 3), help=verbosity_help)
def main(verbosity, use_env_vars):
    if use_env_vars:
        try:
            user_id = os.environ['USER_ID']
            password = os.environ['PASSWORD']
        except KeyError:
            click.echo('USER_ID and PASSWORD not found in environment variables!')
            exit()
    else:
        user_id = getpass(prompt='User ID:')
        password = getpass(prompt='Password:')

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
        try:
            account.show_detailed_stocks()
        except Exception as e:
            print(e)
        try:
            account.show_detailed_mutual_fund()
        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()
