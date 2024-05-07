import time, struct
import hmac


def getMS():
    "获取毫秒字符串。"
    return str(int(1000 * time.time()))


def cvtSec(sec):
    MinutesGet, SecondsGet = divmod(sec, 60)

    HoursGet, MinutesGet = divmod(MinutesGet, 60)

    # print("Total hours are: ", HoursGet)
    # print("Total minutes are: ", MinutesGet)
    # print("Total seconds are: ", SecondsGet)

    return "%d:%02d:%02d" % (HoursGet, MinutesGet, SecondsGet)
