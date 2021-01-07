import math

import requests

from config import APCA_API_KEY_ID, APCA_API_KEY_SECRET, APCA_ENDPOINT
from securities import get_current_price


def get_broker_headers(broker_api_key=APCA_API_KEY_ID, broker_api_secret=APCA_API_KEY_SECRET):
    return {
        "APCA-API-KEY-ID": broker_api_key,
        "APCA-API-SECRET-KEY": broker_api_secret
    }


def is_market_open(endpoint=APCA_ENDPOINT, broker_api_key=APCA_API_KEY_ID, broker_api_secret=APCA_API_KEY_SECRET):
    response = requests.get(f"{endpoint}/v2/clock", headers=get_broker_headers(broker_api_key, broker_api_secret))

    assert response.status_code == 200, (
        f"is_market_open request failed, code: {response.status_code}, reason: {response.text}"
    )

    return response.json()["is_open"]


def get_cash(endpoint=APCA_ENDPOINT, broker_api_key=APCA_API_KEY_ID, broker_api_secret=APCA_API_KEY_SECRET):
    response = requests.get(f"{endpoint}/v2/account", headers=get_broker_headers(broker_api_key, broker_api_secret))

    assert response.status_code == 200, (
        f"get_cash request failed, code: {response.status_code}, reason: {response.text}"
    )

    return float(response.json()["cash"])


def get_positions(endpoint=APCA_ENDPOINT, broker_api_key=APCA_API_KEY_ID, broker_api_secret=APCA_API_KEY_SECRET):
    response = requests.get(f"{endpoint}/v2/positions", headers=get_broker_headers(broker_api_key, broker_api_secret))

    assert response.status_code == 200, (
        f"get_positions request failed, code: {response.status_code}, reason: {response.text}"
    )

    return [
        {
            "symbol": pos["symbol"],
            "qty": int(pos["qty"]),
            "side": pos["side"],
            "market_value": float(pos["market_value"])
        }
        for pos in response.json()
    ]


def place_order(
    symbol,
    num_shares,
    endpoint=APCA_ENDPOINT,
    broker_api_key=APCA_API_KEY_ID,
    broker_api_secret=APCA_API_KEY_SECRET
):
    order = {
        "symbol": symbol.upper(),
        "qty": int(abs(num_shares)),
        "side": "sell" if num_shares < 0 else "buy",
        "type": "market",
        "time_in_force": "gtc"
    }

    response = requests.post(
        f"{endpoint}/v2/orders",
        json=order,
        headers=get_broker_headers(broker_api_key, broker_api_secret)
    )

    assert response.status_code == 200, (
        f"place_order request failed, code: {response.status_code}, reason: {response.text}"
    )


def get_buying_power(
    side="long",
    endpoint=APCA_ENDPOINT,
    broker_api_key=APCA_API_KEY_ID,
    broker_api_secret=APCA_API_KEY_SECRET
):
    positions = get_positions(endpoint, broker_api_key, broker_api_secret)
    cash = get_cash(endpoint, broker_api_key, broker_api_secret)

    #  cash + total long positions
    # (in short): cash + total short positions
    return cash + sum(pos["market_value"] for pos in positions if pos["side"] == side)


def reconcile_portfolio(
    target_symbols,
    side="long",
    endpoint=APCA_ENDPOINT,
    broker_api_key=APCA_API_KEY_ID,
    broker_api_secret=APCA_API_KEY_SECRET
):
    buying_power = get_buying_power(side, endpoint, broker_api_key, broker_api_secret)

    positions = {
        pos["symbol"]: pos
        for pos in get_positions(endpoint, broker_api_key, broker_api_secret)
    }

    target_symbols_set = set(target_symbols)
    combined_symbols = target_symbols_set | set(positions)
    num_target_symbols = len(target_symbols_set)

    if num_target_symbols < 1:
        target_symbol_value = 0
    else:
        target_symbol_value = buying_power / len(target_symbols_set)

    # TODO: also check open orders
    for symbol in combined_symbols:
        if symbol in target_symbols:
            quote = get_current_price(symbol)

            shares = math.floor(target_symbol_value / quote)

            if symbol in positions:
                # symbol desired and already held, but may need to adjust
                diff = shares - positions[symbol]["qty"]

                if diff != 0:
                    place_order(symbol, diff, endpoint, broker_api_key, broker_api_secret)

            else:
                # purchase shares
                place_order(symbol, shares, endpoint, broker_api_key, broker_api_secret)
        else:
            # sell position
            shares = -(positions[symbol]["qty"])
            place_order(symbol, shares, endpoint, broker_api_key, broker_api_secret)
