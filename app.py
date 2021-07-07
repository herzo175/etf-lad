import pickle
import os

import click

import broker
import securities
from config import POOL_SIZE, PICKLE_FILE_NAME


@click.group()
def cli():
    return


@cli.command()
def trade():
    # get top 40 ish etf's
    pool = securities.get_zacks_symbols()

    # Get top symbols
    filtered_pool = securities.filter_symbols_lin_reg(
        pool, max_returned=POOL_SIZE)

    print(f"Target pool: {filtered_pool}")

    # reconcile portfolio to match pool
    # create pickle file with if market not open
    if broker.is_market_open():
        broker.reconcile_portfolio(filtered_pool)
    else:
        with open(PICKLE_FILE_NAME, "wb") as pf:
            pickle.dump(filtered_pool, pf)


@cli.command()
def retry():
    # if market open, load pool from pickle and call reconcile
    if broker.is_market_open() and os.path.exists(PICKLE_FILE_NAME):
        with open(PICKLE_FILE_NAME, "rb") as pf:
            filtered_pool = pickle.load(pf)

            broker.reconcile_portfolio(filtered_pool)

        # Delete pickle file if pool has been reconciled
        os.remove(PICKLE_FILE_NAME)


if __name__ == "__main__":
    cli()
