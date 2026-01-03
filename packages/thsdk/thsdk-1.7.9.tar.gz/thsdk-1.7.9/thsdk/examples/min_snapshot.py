from thsdk import THS
import pandas as pd
import time

# pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None)

# THS({"username": "your_username", "password": "your_password"}) 填写支持L2账户可以查询到历史巨鲸bigcash大单资金数据
# L2账户查询返回 包含字段: ['时间', '价格', '成交量', '外盘成交量', '内盘成交量', '总金额', '主动买入特大单金额', '主动卖出特大单金额', '主动买入大单金额', '主动卖出大单金额', '被动买入特大单金额', '被动卖出特大单金额', '被动买入大单金额', '被动卖出大单金额', '主动买入中单金额', '主动卖出中单金额', '被动买入中单金额', '被动卖出中单金额']
with THS() as ths:
    code = "USZA300033"
    date = "20251225"

    response = ths.min_snapshot(code, date)
    print(f"查询历史分时快照: 代码={code}, 日期={date}")

    if not response or not response.success or response.error:
        print(f"❌ 查询失败，错误信息: {getattr(response, 'error', '未知错误')}")
    elif not response.data or len(response.data) == 0:
        print("⚠️ 未获取到分时快照数据（返回数据为空）。")
    else:
        df = response.df
        if "时间" in df.columns:
            try:
                # 转为上海时区的本地时间
                df["时间"] = pd.to_datetime(df["时间"], unit="s", utc=True).dt.tz_convert("Asia/Shanghai")
            except Exception as ex:
                print(f"时间列转换失败: {ex}")
        # 展示前几行
        print(df)
        print(f"\n共{len(df)}条分时数据。")
        print(f"包含字段: {list(df.columns)}")

    time.sleep(1)
