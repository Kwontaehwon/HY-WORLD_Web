import datetime


def format_datetime(value):
    today = datetime.datetime.now()
    if value.year == today.year:
        fmt = '%m/%d %H:%M'
    else :
        fmt = '%Y/%m/%d'
    return value.strftime(fmt)
