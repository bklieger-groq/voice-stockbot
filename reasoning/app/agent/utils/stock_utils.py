import os
import logging
from polygon import RESTClient
import json
from datetime import datetime, timedelta
import redis
import pickle


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s:%(message)s")

# set up the redis client
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_client = redis.Redis(host=redis_host, port=6379, db=0, decode_responses=False)


def get_cached_data(key: str):
    """Get data from Redis cache"""
    try:
        cached_data = redis_client.get(key)
        if cached_data:
            logging.info(f"Cache hit for {key}")
            return pickle.loads(cached_data)
        return None
    except Exception as e:
        logging.error(f"Error reading from cache: {str(e)}")
        return None


def set_cached_data(key: str, data, cache_duration: int):
    """Set data in Redis cache with expiration"""
    try:
        pickled_data = pickle.dumps(data)
        logging.info(f"Cache write for {key}")
        redis_client.setex(key, cache_duration, pickled_data)
    except Exception as e:
        logging.error(f"Error writing to cache: {str(e)}")


def initialize_polygon_client():
    logging.info("Initializing Polygon API client.")
    POLYGON_API_KEY = os.environ.get("POLYGON_API_KEY")

    if not POLYGON_API_KEY:
        raise EnvironmentError(
            "POLYGON_API_KEY is not set in the environment variables."
        )
    else:
        logging.info("POLYGON_API_KEY : ***************")

    polygon_client = RESTClient(api_key=POLYGON_API_KEY)

    return polygon_client


def get_historical_data(ticker: str, client: RESTClient):
    end_date = datetime.now()
    intervals = [
        ("1 week", timedelta(days=7)),
        ("1 month", timedelta(days=30)),
        ("3 months", timedelta(days=90)),
        ("6 months", timedelta(days=180)),
        ("1 year", timedelta(days=365)),
        ("2 years", timedelta(days=730)),
    ]

    results = {}
    for label, delta in intervals:
        start_date = end_date - delta
        try:
            data = client.get_aggs(ticker, 1, "day", start_date, end_date)
            if data:
                start_price = data[0].close
                end_price = data[-1].close
                change = round((end_price - start_price) / start_price * 100, 2)
                results[label] = {
                    "change": change,
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d"),
                }
        except Exception as e:
            logging.error(f"Error fetching {label} data for {ticker}: {str(e)}")

    return results


def get_stock_fundamentals(ticker: str, client: RESTClient):
    cache_key = f"stock_fundamentals_{ticker}"
    cache_key_text = cache_key + "_text"
    cache_key_json = cache_key + "_json"

    # Try to get from cache
    cached_data_text = get_cached_data(cache_key_text)
    cached_data_json = get_cached_data(cache_key_json)
    if cached_data_text and cached_data_json:
        return cached_data_text, cached_data_json

    try:
        # fetch fundamentals
        fundamentals = client.get_ticker_details(ticker)

        # extract all information except branding and phone
        relevant_info = {
            "address": {
                "address1": (
                    fundamentals.address.address1 if fundamentals.address else None
                ),
                "address2": (
                    fundamentals.address.address2 if fundamentals.address else None
                ),
                "city": fundamentals.address.city if fundamentals.address else None,
                "state": fundamentals.address.state if fundamentals.address else None,
                "country": (
                    fundamentals.address.country if fundamentals.address else None
                ),
                "postal_code": (
                    fundamentals.address.postal_code if fundamentals.address else None
                ),
            },
            "cik": fundamentals.cik,
            "currency_name": fundamentals.currency_name,
            "description": fundamentals.description,
            "homepage_url": fundamentals.homepage_url,
            "list_date": fundamentals.list_date,
            "locale": fundamentals.locale,
            "market_cap": fundamentals.market_cap,
            "name": fundamentals.name,
            "primary_exchange": fundamentals.primary_exchange,
            "share_class_shares_outstanding": fundamentals.share_class_shares_outstanding,
            "sic_description": fundamentals.sic_description,
            "ticker": fundamentals.ticker,
            "total_employees": fundamentals.total_employees,
            "weighted_shares_outstanding": fundamentals.weighted_shares_outstanding,
        }

        for key, value in relevant_info.items():
            if key == "address":
                for addr_key, addr_value in value.items():
                    if addr_value is None:
                        # logging.error(f"⚠️ WARNING: Missing {key}.{addr_key} for {ticker}")
                        relevant_info[key][addr_key] = "not available"
            elif value is None:
                # logging.error(f"⚠️ WARNING: Missing {key} for {ticker}")
                relevant_info[key] = "not available"

        # fetch live price and historical data
        snapshot = client.get_snapshot_ticker(
            "stocks", ticker
        )  # TODO: Prompt AI to use ETFs instead of indicies until expand this functionality. QQQ/SPY.
        logging.info(f"Snapshot for {ticker}: {snapshot}")

        # round since number is approx due to 15 minute delay
        live_price = round(snapshot.day.close) if snapshot and snapshot.day else None
        historical_data = get_historical_data(ticker, client)

        # get fundamental financials information
        financials = get_stock_financials(ticker, client)

        revenue_eps_str = ""

        if (
            len(financials["revenues"]) >= 4
            and len(financials["basic_earnings_per_share"]) >= 4
        ):
            # sum last 4 quarters of revenue
            trailing_revenue = sum(rev["value"] for rev in financials["revenues"][:4])
            latest_revenue_date = financials["revenues"][0]["date"]

            # sum last 4 quarters of EPS
            trailing_eps = sum(
                eps["value"] for eps in financials["basic_earnings_per_share"][:4]
            )
            latest_eps_date = financials["basic_earnings_per_share"][0]["date"]

            revenue_eps_str += f"Annual Revenue (Trailing 12 mo): ${trailing_revenue:,.2f} as of {latest_revenue_date}"
            revenue_eps_str += f"\nAnnual EPS (Trailing 12 mo): ${trailing_eps:,.2f} as of {latest_eps_date}"

        # add live price and historical data to relevant_info
        relevant_info["live_price"] = live_price
        relevant_info["todays_change"] = snapshot.todays_change if snapshot else None
        relevant_info["todays_change_percent"] = (
            snapshot.todays_change_percent if snapshot else None
        )
        relevant_info["historical_changes"] = historical_data

        text_version = f"""
Company: {relevant_info['name']} ({relevant_info['ticker']})
Description: {relevant_info['description']}
Address: {relevant_info['address']['address1']}, {relevant_info['address']['city']}, {relevant_info['address']['state']} {relevant_info['address']['postal_code']}
Website: {relevant_info['homepage_url']}
List Date: {relevant_info['list_date']}
Locale: {relevant_info['locale']}
Market Cap: {f"${relevant_info['market_cap']:,.2f}" if isinstance(relevant_info['market_cap'], (int, float)) else 'not available'}
Primary Exchange: {relevant_info['primary_exchange']}
Industry: {relevant_info['sic_description']}
Total Employees: {f"{relevant_info['total_employees']:,}" if isinstance(relevant_info['total_employees'], (int, float)) else 'not available'}
Share Class Shares Outstanding: {f"{relevant_info['share_class_shares_outstanding']:,}" if isinstance(relevant_info['share_class_shares_outstanding'], (int, float)) else 'not available'}
Weighted Shares Outstanding: {f"{relevant_info['weighted_shares_outstanding']:,}" if isinstance(relevant_info['weighted_shares_outstanding'], (int, float)) else 'not available'}
{revenue_eps_str}

Live Price: about ${live_price:.3f} (delayed by 15 min, see live price on screen)
Today's Change: ${relevant_info['todays_change']:.2f} ({relevant_info['todays_change_percent']:.2f}%) (delayed by 15 min, see live price on screen)

Historical Changes:
"""
        for period, data in historical_data.items():
            text_version += f"Change in last {period} ({data['start_date']} to {data['end_date']}): {data['change']}%\n"

        json_version = json.dumps(relevant_info, indent=2)

        set_cached_data(cache_key_text, text_version, 1200)
        set_cached_data(cache_key_json, json_version, 1200)

        return text_version, json_version

    except Exception as e:
        logging.error(f"Error fetching fundamental data for {ticker}: {str(e)}")
        return f"Error: Unable to fetch fundamental data for {ticker}", "{}"


def process_financials(financials):
    data = {}
    for item in financials:
        date = item.end_date

        # process balance sheet
        if item.financials.balance_sheet:
            for key, datapoint in item.financials.balance_sheet.items():
                if key not in data:
                    data[key] = []
                data[key].append({"date": date, "value": datapoint.value})

        # process income statement
        if item.financials.income_statement:
            for key, value in item.financials.income_statement.__dict__.items():
                if hasattr(value, "value"):
                    if key not in data:
                        data[key] = []
                    data[key].append({"date": date, "value": value.value})

        # process cash flow statement
        if (
            item.financials.cash_flow_statement
            and item.financials.cash_flow_statement.net_cash_flow
        ):
            if "net_cash_flow" not in data:
                data["net_cash_flow"] = []
            data["net_cash_flow"].append(
                {
                    "date": date,
                    "value": item.financials.cash_flow_statement.net_cash_flow.value,
                }
            )

        if (
            item.financials.cash_flow_statement
            and item.financials.cash_flow_statement.net_cash_flow_from_financing_activities
        ):
            if "net_cash_flow_from_financing_activities" not in data:
                data["net_cash_flow_from_financing_activities"] = []
            data["net_cash_flow_from_financing_activities"].append(
                {
                    "date": date,
                    "value": item.financials.cash_flow_statement.net_cash_flow_from_financing_activities.value,
                }
            )

    return data


def get_stock_financials(ticker: str, client: RESTClient):
    try:
        # fetch fundamentals
        financials = client.vx.list_stock_financials(ticker, timeframe="quarterly")
        processed_financials = process_financials(financials)

        return processed_financials
    except Exception as e:
        logging.error(f"Error fetching fundamental data for {ticker}: {str(e)}")

