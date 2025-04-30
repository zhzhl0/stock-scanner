import json
import os
import re
from datetime import date, datetime, timedelta
from typing import Union

import pandas as pd


class TradingCalendar:
    def __init__(self, config_path="config.json"):
        """初始化：读取配置文件"""
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件 {config_path} 不存在")

        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

        self.markets = self.config.get("markets", {})

    def _parse_date(self, date_input) -> date:
        """
        将输入的日期转换为 datetime.date 类型
        支持以下格式：
            - 'YYYY-MM-DD'
            - 'YYYY/MM/DD'
            - 'YYYYMMDD'
            - datetime.date 或 datetime 对象
        """
        if isinstance(date_input, (date, datetime)):
            return date_input.date() if isinstance(date_input, datetime) else date_input
        elif isinstance(date_input, str):
            # 去除多余空格
            date_str = date_input.strip().replace("/", "-").replace(" ", "")

            # 支持格式：YYYYMMDD -> 转换为 YYYY-MM-DD
            if re.fullmatch(r"\d{8}", date_str):
                return date.fromisoformat(f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}")
            # 支持 YYYY-MM-DD、YYYYMM-DD、YYYY-MMDD 等变体
            try:
                return date.fromisoformat(date_str)
            except ValueError:
                raise ValueError("日期字符串格式非法，请使用类似 '20250405' 或 '2025-04-05'")
        else:
            raise TypeError("date 输入必须是 str、datetime 或 date 类型")

    def is_trading_day(self, date: Union[str, date, datetime], market: str = "CN") -> bool:
        """判断某一天是否是特定市场的交易日，支持 str / date / datetime 类型"""
        parsed_date = self._parse_date(date)

        if market not in self.markets:
            raise ValueError(f"不支持的市场代码：{market}")

        mcfg = self.markets[market]
        today = parsed_date.strftime("%Y-%m-%d")

        # 排除周末
        if parsed_date.weekday() in mcfg.get("weekend", [5, 6]):
            return False

        # 排除节假日
        if today in mcfg.get("holidays", []):
            return False

        # A股特殊处理：调休但非交易日
        if market == "CN" and today in mcfg.get("makeup_days_but_closed", []):
            return False

        return True

    def get_holidays(self, market: str = "CN"):
        """获取某市场的节假日列表"""
        if market not in self.markets:
            raise ValueError(f"不支持的市场代码：{market}")
        return self.markets[market].get("holidays", [])

    def get_trading_days(self, year: int, month: int = None, market: str = "CN"):
        """获取某年或某月的所有交易日"""
        trading_days = []

        if month:
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1)
            else:
                end_date = datetime(year, month + 1, 1)
        else:
            start_date = datetime(year, 1, 1)
            end_date = datetime(year + 1, 1, 1)

        current = start_date
        while current < end_date:
            if self.is_trading_day(current, market):
                trading_days.append(current.date())
            current += timedelta(days=1)

        return trading_days

    def generate_calendar_to_df(self, year: int, market: str = "CN"):
        """生成一年的交易日历 DataFrame"""
        trading_days = self.get_trading_days(year, market=market)
        df = pd.DataFrame(trading_days, columns=["Trading Day"])
        df["Weekday"] = pd.to_datetime(df["Trading Day"]).dt.day_name()
        return df

    def generate_calendar_to_csv(self, year: int, market: str = "CN", filename: str = None):
        """生成交易日历并保存为 CSV"""
        df = self.generate_calendar_to_df(year, market)
        if not filename:
            filename = f"{market}_trading_calendar_{year}.csv"
        df.to_csv(filename, index=False)
        print(f"✅ 文件已保存：{filename}")
        return df


cal = TradingCalendar(config_path="config.json")
