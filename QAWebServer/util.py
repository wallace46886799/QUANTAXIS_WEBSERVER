import datetime
import json
import sys
from datetime import date
import time


APPLICATION_JSON = 'application/json'
APPLICATION_XML = 'application/xml'
TEXT_XML = 'text/xml'


boolean = str

if sys.version_info > (3,):
    long = int
    unicode = str
    str = bytes


def convert(value, type):
    """ Convert / Cast function """
    if issubclass(type, str) and not (value.upper() in ['FALSE', 'TRUE']):
        return value.decode('utf-8')
    elif issubclass(type, unicode):
        return unicode(value)
    elif issubclass(type, int):
        return int(value)
    elif issubclass(type, long):
        return long(value)
    elif issubclass(type, float):
        return float(value)
    elif issubclass(type, boolean) and (value.upper() in ['FALSE', 'TRUE']):
        if str(value).upper() == 'TRUE':
            return True
        elif str(value).upper() == 'FALSE':
            return False
    else:
        return value


def report_dates(start_year=2000):
    from datetime import datetime
    end_year = datetime.now().year
    rds = []
    for year in range(start_year, end_year):
        rds.append(datetime(year, 3, 31, 0, 0, 0).strftime('%Y-%m-%d'))
        rds.append(datetime(year, 6, 30, 0, 0, 0).strftime('%Y-%m-%d'))
        rds.append(datetime(year, 9, 30, 0, 0, 0).strftime('%Y-%m-%d'))
        rds.append(datetime(year, 12, 31, 0, 0, 0).strftime('%Y-%m-%d'))
    return rds


def format_ts_datetime(ts):
    dt = ts.strftime("%Y-%m-%d %H:%M:%S")
    return dt


def format_ts_date(ts):
    dt = ts.strftime("%Y-%m-%d")
    return dt


def format_number(number):
    return round(number, 2)


def format_percent(percent):
    dt = '%.2f%%' % percent
    return dt


class CJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)

if __name__ == '__main__':
    print(report_dates())
    print(format_percent(5.4910001755))
