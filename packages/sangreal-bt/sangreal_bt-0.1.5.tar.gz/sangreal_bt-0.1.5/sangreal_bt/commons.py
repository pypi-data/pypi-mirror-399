from pandas.tseries.offsets import Second


class Commons:
    # 300 50 300 期货
    INDEX_FUTURE = (
        "IH",
        "IF",
        "IC",
        "IM",
        "TS",
        "TF",
        "T",
        "TL",
    )

    # 时间偏移常数
    SHIFT_TIME = Second(1)
