from datetime import datetime

from utils.trading_calendar import cal

if __name__ == "__main__":
    date = datetime(2025, 4, 5)
    print(cal.is_trading_day(date, "HK"))  # 输出: False (清明节港股休市)

    print(cal.is_trading_day("2025/03/21", "US"))  # 输出: True (美国市场正常交易)
    print(cal.is_trading_day("2025-03-21", "US"))  # 输出: True (美国市场正常交易)
    print(cal.is_trading_day("20250321", "US"))  # 输出: True (美国市场正常交易)
