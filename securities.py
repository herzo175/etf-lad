import json
import re
import random
from datetime import datetime, timedelta

import requests
from iexfinance.stocks import Stock, get_historical_data
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

from config import IEX_KEY, LOOKBACK_PERIOD


def get_zacks_symbols():
    url = "https://www.zacks.com/funds/top_etf_ajax_datahelper.php"

    headers = {
        "User-Agent": "PostmanRuntime/7.26.1",
    }

    params = {
        "category_id": "all",
        "rank_id": 1,
        "_": random.randint(100_000_000_000_000, 1_000_000_000_000_000)
    }

    response = requests.get(url, headers=headers, params=params)

    assert response.status_code == 200

    quote_pattern = re.compile(r"rel=\"(\w+)\"")

    return [
        quote_pattern.search(button[0]).group(1)
        for button in json.loads(response.text)["data"]
    ]


def get_last_closes(symbol, days_back=LOOKBACK_PERIOD, token=IEX_KEY):
    end = datetime.now()
    start = datetime.now() - timedelta(days=days_back)
    
    closes = get_historical_data(
        symbol,
        start,
        end,
        token=token,
        close_only=True
    )

    return [
        closes[tss]["close"]
        for tss in sorted(
            closes,
            key=lambda ts: datetime.strptime(ts, "%Y-%m-%d")
        )
    ]


def get_current_price(symbol, token=IEX_KEY):
    stk = Stock(symbol, token=token)
    return stk.get_quote()["latestPrice"]


def get_lin_reg_score(closes):
    x = [[i] for i, _ in enumerate(closes)]
    y = closes

    model = LinearRegression().fit(x, y)

    y_pred = [model.predict([i]) for i in x]

    r2 = r2_score(y_pred, y)
    slope = model.coef_[0]

    val =  r2 * slope

    if r2 < 0 and slope < 0:
        return -val

    return val


def filter_symbols_lin_reg(symbols, min_score=0, max_returned=5):
    filtered_symbols = []

    for symbol in symbols:
        closes = get_last_closes(symbol)
        score = get_lin_reg_score(closes)

        print(symbol, score)

        if score > min_score:
            filtered_symbols.append((symbol, score))

    filtered_symbols.sort(key=lambda st: st[1], reverse=True)

    return [st[0] for st in filtered_symbols[:max_returned]]
