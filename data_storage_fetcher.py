import asyncio
import aiohttp
import logging
from db_utils import insert_kline_data, insert_realtime_price, insert_24h_price_change, insert_contract_data

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 异步获取 K 线数据并存储
async def fetch_and_store_kline_data(session, symbol):
    while True:
        try:
            url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=5m&limit=1"
            async with session.get(url) as response:
                if response.status == 200:
                    kline = await response.json()
                    if kline:
                        insert_kline_data(symbol, kline[0])
                        logging.info(f"Successfully fetched and stored K-line data for {symbol}")
                else:
                    logging.error(f"Failed to fetch K-line data for {symbol}. Status code: {response.status}")
        except Exception as e:
            logging.error(f"Error fetching and storing K-line data for {symbol}: {e}")
        # 每 5 分钟请求一次
        await asyncio.sleep(5 * 60)

# 异步获取实时价格并存储
async def fetch_and_store_realtime_price(session, symbol):
    while True:
        try:
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    price = float(data.get("price"))
                    timestamp = int(asyncio.get_running_loop().time() * 1000)
                    insert_realtime_price(symbol, price, timestamp)
                    logging.info(f"Successfully fetched and stored real-time price for {symbol}")
                else:
                    logging.error(f"Failed to fetch real-time price for {symbol}. Status code: {response.status}")
        except Exception as e:
            logging.error(f"Error fetching and storing real-time price for {symbol}: {e}")
        # 每 15 秒请求一次
        await asyncio.sleep(15)

# 异步获取 24 小时价格变动统计并存储
async def fetch_and_store_24h_price_change(session, symbol):
    while True:
        try:
            url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    timestamp = int(asyncio.get_running_loop().time() * 1000)
                    insert_24h_price_change(symbol, data, timestamp)
                    logging.info(f"Successfully fetched and stored 24h price change for {symbol}")
                else:
                    logging.error(f"Failed to fetch 24h price change for {symbol}. Status code: {response.status}")
        except Exception as e:
            logging.error(f"Error fetching and storing 24h price change for {symbol}: {e}")
        # 每 2 小时请求一次
        await asyncio.sleep(2 * 60 * 60)

# 异步获取合约数据并存储
async def fetch_and_store_contract_data(session, symbol):
    while True:
        try:
            # 合约资金费率
            funding_rate_url = f"https://fapi.binance.com/fapi/v1/fundingRate?symbol={symbol}&limit=1"
            async with session.get(funding_rate_url) as funding_rate_response:
                if funding_rate_response.status == 200:
                    funding_rate_data = await funding_rate_response.json()
                    if funding_rate_data:
                        funding_rate = float(funding_rate_data[0].get("fundingRate"))
                    else:
                        funding_rate = None
                else:
                    logging.error(f"Failed to fetch funding rate for {symbol}. Status code: {funding_rate_response.status}")
                    funding_rate = None

            # 合约持仓量
            open_interest_url = f"https://fapi.binance.com/fapi/v1/openInterest?symbol={symbol}"
            async with session.get(open_interest_url) as open_interest_response:
                if open_interest_response.status == 200:
                    open_interest_data = await open_interest_response.json()
                    open_interest = float(open_interest_data.get("openInterest"))
                else:
                    logging.error(f"Failed to fetch open interest for {symbol}. Status code: {open_interest_response.status}")
                    open_interest = None

            if funding_rate is not None and open_interest is not None:
                timestamp = int(asyncio.get_running_loop().time() * 1000)
                insert_contract_data(symbol, funding_rate, open_interest, timestamp)
                logging.info(f"Successfully fetched and stored contract data for {symbol}")
        except Exception as e:
            logging.error(f"Error fetching and storing contract data for {symbol}: {e}")
        # 每 15 分钟请求一次
        await asyncio.sleep(15 * 60)