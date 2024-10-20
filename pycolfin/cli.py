# -*- coding: utf-8 -*-
import os
from getpass import getpass

import click

from .pycolfin import COLFin


use_env_vars_help = """
Use USER_ID and PASSWORD from environment variables.
Not recommended if you are using a shared computer!
(This is like storing bank credentials in a text file)
"""
annotate_investment_guide = """
Include guide from COL
"""


@click.command()
@click.option('--use-env-vars', is_flag=True, default=False, help=use_env_vars_help)
@click.option('--annotate-with-col-guide', is_flag=True, default=False, help=annotate_investment_guide)
def main(annotate_with_col_guide, use_env_vars):
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

    account.fetch_account_summary()
    account.fetch_detailed_portfolio()

    if annotate_with_col_guide:
        account.fetch_investment_guide()
        account.show_detailed_stocks(annotate_with_col_guide=True)
    else:
        account.show_detailed_stocks()

    account.show_detailed_mutual_fund()
    account.show_account_summary()

if __name__ == "__main__":
    main()
