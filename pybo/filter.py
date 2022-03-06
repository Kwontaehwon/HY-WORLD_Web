import datetime


def format_datetime(value):
    today = datetime.datetime.now()
    if value.year == today.year:
        fmt = '%m/%d %H:%M'
    else :
        fmt = '%Y년 %m월 %d일 %H:%M'
    return value.strftime(fmt)
