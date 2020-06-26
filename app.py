import broker
import securities
from config import POOL_SIZE


def main():
    # get top 40 ish etf's
    pool = securities.get_zacks_symbols()

    # Get top symbols
    filtered_pool = securities.filter_symbols_lin_reg(pool, max_returned=POOL_SIZE)

    # reconcile portfolio to match pool
    if broker.is_market_open():
        broker.reconcile_portfolio(filtered_pool)


if __name__ == "__main__":
    main()
