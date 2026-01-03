import dqtrader_rs


def is_stock(market: str):
    return dqtrader_rs.is_stock_by_market(market)


def is_future(market: str):
    return dqtrader_rs.is_future_by_market(market)
