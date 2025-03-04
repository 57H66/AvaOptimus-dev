import requests

async def get_token_info(token_symbol):
    try:
        # 获取代币价格与24小时交易量信息
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={token_symbol}"
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200:
            price = data.get("lastPrice")
            volume = data.get("volume")
            price_change_percent = data.get("priceChangePercent")
            if price and volume and price_change_percent:
                # 计算以 USDT 计价的交易量并转换为 M 单位，保留到小数点后 1 位
                volume_in_usdt = float(price) * float(volume)
                volume_in_usdt_m = round(volume_in_usdt / 1000000, 1)
                return f"{token_symbol[:-4]} 的价格是：{price} USDT\n" \
                       f"24小时交易量： {volume_in_usdt_m}MUSDT\n" \
                       f"24小时涨跌幅： {price_change_percent}%\n" \
                       f"请输入下一个要查询的代币名称"
            else:
                return f"无法获取 {token_symbol[:-4]} 的价格，请检查输入是否正确。"
        else:
            return f"请求Binance API时出错：{response.status_code}"
    except Exception as e:
        return f"发生错误：{str(e)}"

async def get_funding_rate_and_open_interest(token_symbol):
    try:
        # 构建获取合约资金费率的请求 URL
        # 从 Binance 的期货 API 获取指定交易对的最新资金费率，只取 1 条记录
        funding_rate_url = f"https://fapi.binance.com/fapi/v1/fundingRate?symbol={token_symbol}&limit=1"
        # 发送 HTTP GET 请求获取资金费率数据
        funding_rate_response = requests.get(funding_rate_url)
        # 将响应内容解析为 JSON 格式
        funding_rate_data = funding_rate_response.json()

        # 检查请求是否成功（状态码为 200）且返回的数据不为空
        if funding_rate_response.status_code == 200 and funding_rate_data:
            # 从返回的数据中提取资金费率
            funding_rate = funding_rate_data[0].get("fundingRate")
        else:
            # 如果请求失败或数据为空，将资金费率设为 None
            funding_rate = None

        # 构建获取合约初始持仓量的请求 URL
        # 从 Binance 的期货 API 获取指定交易对的当前持仓量
        open_interest_url = f"https://fapi.binance.com/fapi/v1/openInterest?symbol={token_symbol}"
        # 发送 HTTP GET 请求获取持仓量数据
        open_interest_response = requests.get(open_interest_url)
        # 将响应内容解析为 JSON 格式
        open_interest_data = open_interest_response.json()

        # 检查请求是否成功（状态码为 200）
        if open_interest_response.status_code == 200:
            # 从返回的数据中提取初始持仓量，并转换为浮点数
            initial_open_interest = float(open_interest_data.get("openInterest"))
        else:
            # 如果请求失败，将初始持仓量设为 None
            initial_open_interest = None

        # 用于存储最终要返回的信息
        result = []

        # 如果成功获取到资金费率
        if funding_rate is not None:
            # 将资金费率转换为百分比并去掉多余的零
            funding_rate_percent = float(funding_rate) * 100
            # 使用 {:.4g} 格式化，去掉多余的零
            result.append(f"{token_symbol[:-4]} 的合约资金费率是：{funding_rate_percent:.4g}%\n")
            
        # 如果成功获取到初始持仓量
        if initial_open_interest is not None:
            # 将初始持仓量信息添加到结果列表中
            result.append(f"{token_symbol[:-4]} 的当前合约持仓量是：{initial_open_interest}\n")

        # 如果结果列表不为空
        if result:
            # 将结果列表中的信息拼接成一个字符串，并添加提示信息
            return ''.join(result) + "请输入下一个要查询的代币名称"
        else:
            # 如果结果列表为空，提示用户检查输入是否正确
            return f"无法获取 {token_symbol[:-4]} 的相关信息，请检查输入是否正确。"

    except Exception as e:
        # 如果发生异常，返回错误信息
        return f"发生错误：{str(e)}"



def get_top_20_tokens_by_volume():
    try:
        # 从 Binance 获取当日交易量数据
        url = "https://api.binance.com/api/v3/ticker/24hr"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            # 定义稳定币列表
            stable_coins = ['USDT', 'USDC', 'BUSD', 'DAI', 'FDUSD']
            # 过滤掉非 USDT 交易对以及稳定币对 USDT 的交易对，并转换交易量单位为 m USDT
            filtered_data = []
            for item in data:
                symbol = item['symbol']
                if symbol.endswith('USDT'):
                    token_name = symbol[:-4]
                    if token_name not in stable_coins:
                        volume_m_usdt = float(item['quoteVolume']) / 1000000
                        filtered_data.append({'symbol': symbol, 'quoteVolume': volume_m_usdt})
            # 按交易量排序并获取前 20 名
            sorted_data = sorted(filtered_data, key=lambda x: x['quoteVolume'], reverse=True)[:20]
            popular_tokens = []
            
            medals = ["🥇", "🥈", "🥉"]
            for idx, item in enumerate(sorted_data, start=1):
                symbol = item['symbol']
                token_name = symbol[:-4]
                volume = f"{item['quoteVolume']:.2f} m USDT"
                if idx <= 3:
                    # 排名前三添加奖牌表情，不显示序号
                    line = f"{medals[idx-1]} {token_name}USDT: {volume}"
                else:
                    line = f"{idx}. {token_name}USDT: {volume}"
                popular_tokens.append(line)

            return "\n".join(popular_tokens)
        else:
            return f"请求 Binance API 时出错：{response.status_code}"
    except Exception as e:
        return f"发生错误：{str(e)}"