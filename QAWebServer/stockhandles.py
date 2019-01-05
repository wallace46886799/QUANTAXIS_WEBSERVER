# coding:utf-8
#
# The MIT License (MIT)
#
# Copyright (c) 2016-2018 yutiansut/QUANTAXIS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from QUANTAXIS.QAFetch.QAQuery import (QA_fetch_stock_day, QA_fetch_financial_report, QA_fetch_stock_list,
                                       QA_fetch_stock_info, QA_util_to_json_from_pandas)
from plugins.QAFarvirate import (QA_add_stock_fav, QA_delete_stock_fav, QA_fetch_stock_fav)
from QAWebServer.basehandles import QABaseHandler
import pandas as pd
from util import report_dates, format_ts_date, format_percent, format_number


class StockListHandler(QABaseHandler):
    def get(self):
        page = int(self.get_argument('page', default=1))
        page_size = int(self.get_argument('page_size', default=10))
        start = (page - 1) * page_size
        end = page * page_size - 1
        stock_list = QA_fetch_stock_list()
        stock_list['pre_close'] = stock_list['pre_close'].apply(lambda x: round(x, 2))
        stock_fav = QA_fetch_stock_fav()
        stock_list = stock_list[stock_list["code"].isin(stock_fav['code'].tolist())]
        total = len(stock_list)
        data = QA_util_to_json_from_pandas(stock_list[start:end])
        return self.write({'result': data, 'page': int(page), 'page_size': int(page_size), 'total': int(total)})


# https://github.com/QUANTAXIS/QUANTAXIS/blob/cbb1130e8f4fa804a77f456ac11306c74c756228/Documents/QA_FINANCIAL.md
# https://github.com/QUANTAXIS/QUANTAXIS/blob/master/Documents/financial_means.md#8-%E8%8E%B7%E5%88%A9%E8%83%BD%E5%8A%9B%E5%88%86%E6%9E%90
# http://211.159.182.106/#
# https://www.cnblogs.com/skying555/p/5914391.html
class StockDividendHandler(QABaseHandler):
    def get(self):
        code = self.get_argument('code', default='000001')
        start_year = self.get_argument('start_year', default='2002')
        res = QA_fetch_financial_report([code], report_dates(int(start_year)))
        temp = pd.DataFrame({
            'report_date': res.report_date,
            'code': res.code,
            'cashPaymentsForDistrbutionOfDividendsOrProfits': res.cashPaymentsForDistrbutionOfDividendsOrProfits
        })
        temp['report_date'].apply(format_ts_date)
        data = QA_util_to_json_from_pandas(temp)
        return self.write({'result': data})


class StockRoeHandler(QABaseHandler):
    def get(self):
        code = self.get_argument('code', default='000001')
        start_year = self.get_argument('start_year', default='2002')
        res = QA_fetch_financial_report([code], report_dates(int(start_year)))

        temp = pd.DataFrame({
            'report_date': res.report_date,
            'code': res.code,
            'ROE': res.ROE
        })

        temp['report_date_str'] = temp['report_date'].apply(format_ts_date)
        temp['ROE'] = temp['ROE'].apply(format_number)
        temp['ROE_str'] = temp['ROE'].apply(format_percent)
        data = QA_util_to_json_from_pandas(temp)
        return self.write({'result': data})


class StockBasicHandler(QABaseHandler):
    def get(self):
        code = self.get_argument('code', default='000001')
        data = QA_fetch_stock_info(code)
        return self.write({'result': data})


class StockReportingHandler(QABaseHandler):
    def get(self):
        code = self.get_argument('code', default='000001')
        data = QA_fetch_stock_info(code)
        return self.write({'result': data})


class StockPEPBHandler(QABaseHandler):
    def get(self):
        code = self.get_argument('code', default='000001')
        start_date = self.get_argument('start_date', default='2018-01-01')
        end_date = self.get_argument('end_date', default='2018-12-31')
        start_year = self.get_argument('start_year', default='2017')

        stock_prices = QA_fetch_stock_day(code, start_date, end_date, format='pandas')

        financial_reports = QA_fetch_financial_report([code], report_dates(int(start_year)))

        # PE= 股价/每股收益
        # PB= 股价/每股净资产
        # PEG=PE/（企业年盈利增长率*100）
        price_pd = pd.DataFrame({
            'code': stock_prices.code,
            'date': stock_prices.date,
            'close': stock_prices.close
        })

        reports_pd = pd.DataFrame({
            'code': financial_reports.code,
            'report_date': financial_reports.report_date,
            'EPS': financial_reports.EPS,
            'netAssetsPerShare': financial_reports.netAssetsPerShare,
            'netProfitGrowthRate': financial_reports.netProfitGrowthRate
        })

        reports_pd['report_date_str'] = reports_pd['report_date'].apply(format_ts_date)

        eps_sum = reports_pd.loc[reports_pd["report_date_str"] == "2017-12-31"].EPS.sum()
        aps_sum = reports_pd.loc[reports_pd["report_date_str"] == "2017-12-31"].netAssetsPerShare.sum()
        pgr_sum = reports_pd.loc[reports_pd["report_date_str"] == "2017-12-31"].netProfitGrowthRate.sum()

        price_pd['date_str'] = price_pd['date'].apply(lambda x: x.strftime("%Y-%m-%d"))
        price_pd['eps_sum'] = price_pd['close'].apply(lambda x: round(eps_sum, 2))
        price_pd['aps_sum'] = price_pd['close'].apply(lambda x: round(aps_sum, 2))
        price_pd['pgr_sum'] = price_pd['close'].apply(lambda x: round(pgr_sum, 2))
        price_pd['pe'] = price_pd['close'].apply(lambda x: round(x / eps_sum, 2))
        price_pd['pb'] = price_pd['close'].apply(lambda x: round(x / aps_sum, 2))
        price_pd['peg'] = price_pd['pe'].apply(lambda x: round(x / pgr_sum, 2))

        return self.write({'stock_prices': QA_util_to_json_from_pandas(price_pd),
                           'financial_reports': QA_util_to_json_from_pandas(reports_pd)})


class StockFavHandler(QABaseHandler):
    def get(self):
        data = QA_fetch_stock_fav()
        return self.write({'result': QA_util_to_json_from_pandas(data)})

    def post(self):
        code = self.get_body_argument('code', default='000001')
        data = QA_add_stock_fav(code)
        return self.write({'result': data, 'code': code})

    def delete(self):
        code = self.get_argument('code', default='000001')
        data = QA_delete_stock_fav(code)
        return self.write({'result': data, 'code': code})
