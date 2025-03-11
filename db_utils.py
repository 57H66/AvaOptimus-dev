import psycopg2
from psycopg2 import sql
from config import DB_CONFIG
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 初始化数据库表
def init_db():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # 创建 K 线数据表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS kline_data (
                symbol TEXT,
                open_time BIGINT,
                open_price DECIMAL(20, 8),
                high_price DECIMAL(20, 8),
                low_price DECIMAL(20, 8),
                close_price DECIMAL(20, 8),
                volume DECIMAL(20, 2),
                close_time BIGINT,
                quote_asset_volume DECIMAL(20, 2),
                number_of_trades INT,
                taker_buy_base_asset_volume DECIMAL(20, 2),
                taker_buy_quote_asset_volume DECIMAL(20, 2),
                PRIMARY KEY (symbol, open_time)
            )
        """)

        # 创建实时价格表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS realtime_prices (
                symbol TEXT,
                price DECIMAL(20, 8),
                timestamp BIGINT,
                PRIMARY KEY (symbol, timestamp)
            )
        """)

        # 创建 24 小时价格变动统计表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_change_24h (
                symbol TEXT,
                price_change DECIMAL(20, 8),
                price_change_percent DECIMAL(5, 2),
                weighted_avg_price DECIMAL(20, 8),
                prev_close_price DECIMAL(20, 8),
                last_price DECIMAL(20, 8),
                last_qty DECIMAL(20, 8),
                bid_price DECIMAL(20, 8),
                bid_qty DECIMAL(20, 8),
                ask_price DECIMAL(20, 8),
                ask_qty DECIMAL(20, 8),
                open_price DECIMAL(20, 8),
                high_price DECIMAL(20, 8),
                low_price DECIMAL(20, 8),
                volume DECIMAL(20, 2),
                quote_volume DECIMAL(20, 2),
                open_time BIGINT,
                close_time BIGINT,
                first_id INT,
                last_id INT,
                count INT,
                timestamp BIGINT,
                PRIMARY KEY (symbol, timestamp)
            )
        """)

        # 创建合约数据表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contract_data (
                symbol TEXT,
                funding_rate DECIMAL(10, 8),
                open_interest DECIMAL(20, 2),
                timestamp BIGINT,
                PRIMARY KEY (symbol, timestamp)
            )
        """)

        conn.commit()
        cursor.close()
        conn.close()
        logging.info("Database tables initialized successfully")
    except Exception as e:
        logging.error(f"Error initializing database tables: {e}")

# 插入 K 线数据
def insert_kline_data(symbol, kline):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        insert_query = sql.SQL("""
            INSERT INTO kline_data (symbol, open_time, open_price, high_price, low_price, close_price, volume, close_time, quote_asset_volume, number_of_trades, taker_buy_base_asset_volume, taker_buy_quote_asset_volume)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (symbol, open_time) DO NOTHING
        """)
        cursor.execute(insert_query, (
            symbol, int(kline[0]), float(kline[1]), float(kline[2]), float(kline[3]), float(kline[4]),
            float(kline[5]), int(kline[6]), float(kline[7]), int(kline[8]), float(kline[9]), float(kline[10])
        ))
        conn.commit()
        cursor.close()
        conn.close()
        logging.info(f"Successfully inserted K-line data for {symbol}")
    except Exception as e:
        logging.error(f"Error inserting K-line data for {symbol}: {e}")

# 插入实时价格数据
def insert_realtime_price(symbol, price, timestamp):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        insert_query = sql.SQL("""
            INSERT INTO realtime_prices (symbol, price, timestamp)
            VALUES (%s, %s, %s)
            ON CONFLICT (symbol, timestamp) DO NOTHING
        """)
        cursor.execute(insert_query, (symbol, price, timestamp))
        conn.commit()
        cursor.close()
        conn.close()
        logging.info(f"Successfully inserted real-time price for {symbol}")
    except Exception as e:
        logging.error(f"Error inserting real-time price for {symbol}: {e}")

# 插入 24 小时价格变动统计数据
def insert_24h_price_change(symbol, data, timestamp):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        insert_query = sql.SQL("""
            INSERT INTO price_change_24h (symbol, price_change, price_change_percent, weighted_avg_price, prev_close_price, last_price, last_qty, bid_price, bid_qty, ask_price, ask_qty, open_price, high_price, low_price, volume, quote_volume, open_time, close_time, first_id, last_id, count, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (symbol, timestamp) DO NOTHING
        """)
        cursor.execute(insert_query, (
            symbol, float(data["priceChange"]), float(data["priceChangePercent"]), float(data["weightedAvgPrice"]),
            float(data["prevClosePrice"]), float(data["lastPrice"]), float(data["lastQty"]), float(data["bidPrice"]),
            float(data["bidQty"]), float(data["askPrice"]), float(data["askQty"]), float(data["openPrice"]),
            float(data["highPrice"]), float(data["lowPrice"]), float(data["volume"]), float(data["quoteVolume"]),
            int(data["openTime"]), int(data["closeTime"]), int(data["firstId"]), int(data["lastId"]),
            int(data["count"]), timestamp
        ))
        conn.commit()
        cursor.close()
        conn.close()
        logging.info(f"Successfully inserted 24h price change for {symbol}")
    except Exception as e:
        logging.error(f"Error inserting 24h price change for {symbol}: {e}")

# 插入合约数据
def insert_contract_data(symbol, funding_rate, open_interest, timestamp):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        insert_query = sql.SQL("""
            INSERT INTO contract_data (symbol, funding_rate, open_interest, timestamp)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (symbol, timestamp) DO NOTHING
        """)
        cursor.execute(insert_query, (symbol, funding_rate, open_interest, timestamp))
        conn.commit()
        cursor.close()
        conn.close()
        logging.info(f"Successfully inserted contract data for {symbol}")
    except Exception as e:
        logging.error(f"Error inserting contract data for {symbol}: {e}")