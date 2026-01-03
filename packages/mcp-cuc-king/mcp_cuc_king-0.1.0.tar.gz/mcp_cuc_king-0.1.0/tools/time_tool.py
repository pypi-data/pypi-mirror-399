from typing import Optional
from datetime import datetime
import pytz

# 核心功能：获取当前时间（支持时区）
def get_current_time(timezone: Optional[str] = None) -> str:
    try:
        if timezone:
            tz = pytz.timezone(timezone)
            current_time = datetime.now(tz)
        else:
            current_time = datetime.now()
        return current_time.strftime("%Y-%m-%d %H:%M:%S %Z")
    except pytz.UnknownTimeZoneError:
        return f"错误：时区'{timezone}'无效"

# 直接测试功能（确保能运行）
if __name__ == "__main__":
    print("测试：默认时区")
    print(get_current_time())
    print("测试：上海时区")
    print(get_current_time("Asia/Shanghai"))