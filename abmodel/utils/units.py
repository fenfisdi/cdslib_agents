# from scimath.units.length import
from datetime import timedelta


def timedelta_to_days(td: timedelta) -> float:
    """
    """
    # 86400 s = 60 s * 60 m * 24 h
    return td.total_seconds()/86400
