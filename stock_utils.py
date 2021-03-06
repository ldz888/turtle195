#!/usr/bin/env python
#-*- coding: utf8 -*-
import numpy as np, pandas as pf, math, datetime as dt, time 
from matplotlib.pylab import date2num, num2date
import matplotlib.pyplot as plt, mpl_finance as mpf

# https://tushare.pro/
import tushare as ts


class StockDataSource:
    '股票数据集合'
    
    ts.set_token("e2a71ab976c499825f6f48186f24700f70e0f13af933e2f508684cc0")
    ts_api = ts.pro_api()

    def __init__(self, path = './data'):
        self.stocks = []
        self.path = path

    def parse_data(self, stype = 'stock'):
        return self._parse_data(self.stocks, stype)

    def parse_price(self, stype = 'stock'):
        return self._parse_price(self.stocks, stype)

    def read(self, code, time_unit = 'daily'):
        # print('read', code, time_unit, 'data')
        local_data = self._read(code, time_unit)
        self.stocks = local_data.sort_index(ascending=False)
        return self.stocks

    def load(self, code, startdate, enddate, stype = 'stock', time_unit = 'daily'):
        print('load', stype, code, time_unit, 'data, from', StockDataSource.str_date(startdate), 
            'to', StockDataSource.str_date(enddate))

        startdate = StockDataSource.float_date(startdate)
        enddate = StockDataSource.float_date(enddate)

        local_data = self._read(code, time_unit)
        _rowcount = len(local_data)
        
        if _rowcount > 0:
            # print( local_data.at[0, 'trade_date'] )
            _head = StockDataSource.float_date(local_data.at[0, 'trade_date'])
            _tear = StockDataSource.float_date(local_data.at[_rowcount-1, 'trade_date'])
            
            if enddate - _head > 10: #_head+1 < enddate:
                down_data = self._download(code, _head + 1, enddate, stype, time_unit)
                local_data = self._join(local_data, down_data)
            if _tear - startdate > 10: #_tear-1 > startdate:
                down_data = self._download(code, startdate, _tear-1, stype, time_unit)
                local_data = self._join(local_data, down_data)
        else:
            local_data = self._download(code, startdate, enddate, stype, time_unit)

        if len(local_data) > _rowcount:
            print('write csv file', len(local_data), 'rows')
            local_data.to_csv(self.path + '/' + code + '.' + time_unit + '.csv')

        self.stocks = local_data.sort_index(ascending=False)
        return self.stocks
        

    def _parse_price(self, stock_data, stype = 'stock'):
        _list = []
        data_list = stock_data.values.tolist()

        for row in data_list:
            if stype == 'index':
                tscode, trade_date, close, _open, high, low = row[0:6]
            elif stype == 'stock':
                tscode, trade_date, _open, high, low, close = row[0:6]
            _timenum = StockDataSource.float_date(trade_date)
            _list.append( (_timenum, _open, high, low, close) )

        return _list

    def _parse_data(self, stock_data, stype = 'stock'):
        data_list = []
        ave_price = []
        volumes = []

        for rnum, row in stock_data.iterrows():
            if stype == 'index':
                tscode, trade_date, close, open, high, low = row[0:6]
            elif stype == 'stock':
                tscode, trade_date, open, high, low, close = row[0:6]

            vol,amount = row[9:11]
            timenum = StockDataSource.float_date(trade_date)

            # _date = dt.datetime.strptime(trade_date, '%Y%m%d')
            # timenum = date2num(_date)

            datas = (timenum, open, high, low, close)
            data_list.append(datas)
            ave_price.append( (high+low)/2 )
            volumes.append(vol)

        data_table = np.transpose( data_list )
        dates = data_table[0]
        return dates, data_list, ave_price, volumes

    def _join(self, csv_data2, net_data1):
        len1 = len(net_data1)
        len2 = len(csv_data2)
        print('join csv_data', len2, ' net_data1', len1)

        if len1 < 1: 
            return csv_data2
        if len2 < 1: 
            return net_data1

        _head1 = net_data1.at[0, 'trade_date']
        _head2 = csv_data2.at[0, 'trade_date']
        _tear1 = net_data1.at[len1-1, 'trade_date']
        _tear2 = csv_data2.at[len2-1, 'trade_date']

        if _head1 < _head2:
            if _tear1 < _tear2:
                temp = csv_data2.loc[csv_data2['trade_date'] > _head1]
                data0 = temp.append(net_data1, ignore_index=True)
            else:
                data0 = csv_data2
        elif _head1 > _head2:
            if _tear1 < _tear2:
                data0 = net_data1
            else:
                temp = net_data1.loc[net_data1['trade_date'] > _head1]
                data0 = temp.append(csv_data2, ignore_index=True)
        else:
            if _tear1 < _tear2:
                data0 = net_data1
            else:
                data0 = csv_data2

        return data0

    def _read(self, code, time_unit = 'daily'):
        return StockDataSource.read_data_file(self.path + '/' + code + '.' + time_unit + '.csv')

    @staticmethod
    def read_data_file(data_file, time_unit = 'daily'):
        try:
            return pf.read_csv(data_file, index_col = 0, dtype = {'trade_date' : str})
            # return pf.read_csv(path + '/' + code + '.' + time_unit + '.csv', 
            #     index_col=0, dtype = {'trade_date' : str})
        except IOError: 
            return pf.DataFrame()

    def _daily2weekly(self, daily_datas):
        weekly_datas = pf.DataFrame()
        kidx = 0
        start = 0
        
        for rnum, row in daily_datas.iterrows():
            ts_code, trade_date, close, open, high, low = row[0:6]
            # vol,amount = row[9:11]./
            pre_close,change,pct_chg,vol,amount = row[6:11]
            _date = dt.strptime(trade_date, '%Y%m%d')
            _weekday = _date.weekday()

            if _weekday == 0:
                if start:
                    _row = {'ts_code': [ts_code], 'trade_date': [_trade_date], 
                        'open': [_open], 'close': [_close], 'high': [_high], 'low': [_low], 
                        'pre_close': [pre_close], 'change': [change], 'pct_chg': [pct_chg], 
                        'vol': [_vol], 'amount': [_amount]}
                    _index = [kidx]
                    weekly_datas = weekly_datas.append(pf.DataFrame(_row, _index))
                    kidx = kidx+1

                start = 1
                _trade_date = trade_date
                _open = open
                _close = close
                _high = high
                _low = low
                _vol = vol
                _amount = amount

            elif start:
                _close = close
                _high = max(_high, high)
                _low = min(_low, low)
                _vol += vol
                _amount += amount

        return weekly_datas

    @staticmethod
    def float_date(_date):
        if isinstance(_date, np.int64):
            _date = str(_date)
        if isinstance(_date, str):
            _date = dt.datetime.strptime(_date, '%Y%m%d')
        if isinstance(_date, dt.datetime):
            _date = date2num(_date)
        return _date

    @staticmethod
    def str_date(_date):
        if isinstance(_date, float):
            _date = num2date(_date).strftime('%Y%m%d')
        elif isinstance(_date, np.int64):
            _date = str(_date)
        elif isinstance(_date, dt.datetime):
            _date = _date.strftime('%Y%m%d')
        return _date

    @staticmethod
    def datetime(_date):
        if isinstance(_date, float):
            _date = num2date(_date)
        elif isinstance(_date, np.int64):
            _date = str(_date)
        if isinstance(_date, str):
            _date = dt.datetime.strptime(_date, '%Y%m%d')
        return _date


    def _download(self, code, startdate, enddate, stype = 'stock', time_unit = 'daily'):
        time.sleep(0.01)
        startdate = StockDataSource.str_date(startdate)
        enddate = StockDataSource.str_date(enddate)
        print('download', stype, code, 'data, from', startdate, 'to', enddate)

        if stype == 'index':
            hist_data = StockDataSource.ts_api.index_daily(ts_code=code, start_date=startdate, end_date=enddate)
            if time_unit == 'weekly':
                hist_data = self._daily2weekly(hist_data)
            # elif time_unit == 'monthly':
            #     hist_data = self._daily2monthly(hist_data)

        elif stype == 'fund':
            hist_data = StockDataSource.ts_api.fund_daily(ts_code=code, start_date=startdate, end_date=enddate)
            if time_unit == 'weekly':
                hist_data = self._daily2weekly(hist_data)
            # elif time_unit == 'monthly':
            #     hist_data = self._daily2monthly(hist_data)

        else:
            if time_unit == 'daily':
                hist_data = ts.pro_bar(pro_api=StockDataSource.ts_api, ts_code=code, adj='qfq', 
                    start_date=startdate, end_date=enddate)
            elif time_unit == 'weekly':
                hist_data = ts.pro_bar(pro_api=StockDataSource.ts_api, ts_code=code, adj='qfq', freq='W', 
                    start_date=startdate, end_date=enddate)
            elif time_unit == 'monthly':
                hist_data = ts.pro_bar(pro_api=StockDataSource.ts_api, ts_code=code, adj='qfq', freq='M', 
                    start_date=startdate, end_date=enddate)
                    
            if hist_data is None:
                hist_data = pf.DataFrame()
            else:
                hist_data.index = range( len(hist_data) )

        print('download', len(hist_data), 'row data.')
        return hist_data


class StockAccount:
    '股票交易账户'

    def __init__(self, cash, max_credit = 0):
        self.max_credit = max_credit
        self.cash = self.market_value = cash
        self.cost = self.credit = 0

        self.max_value = self.min_value = cash
        self.max_back = self.max_lever = 0
        self.long_count = self.short_count = self.succeed = 0

        self.stocks = pf.DataFrame()
        self.records = []

    def status_info(self):
        print('long %d, short %d, success %d.' %(self.long_count, self.short_count, self.succeed))
        print('value %.2f, credit %.2f, cost %.2f' %( self.market_value*0.0001, self.credit*0.0001, self.cost*0.0001))
        print('max %.2f, min %.2f, back %.2f, lever %.2f' %( self.max_value*0.0001, self.min_value*0.0001, self.max_back*100, self.max_lever*100))

    def get_records(self):
        _records = pf.DataFrame(self.records, columns=['order_time', 'code', 'price', 
            'volume', 'amount', 'commision', 'total', 'total volume', 'total value',
            'cash', 'credit', 'market value', 'lever', 'back'])
        return _records

    def save_records(self, code, path = './records'):
        _records = self.get_records()
        if( len(_records) > 1 ):
            _records.to_csv(path + '/' + code + '.records.csv')

    def Rechange(self, _cash):
        if self.credit > _cash:
            self.credit -= _cash
        elif self.credit > 0:
            self.cash += _cash - self.credit
            self.credit = 0
        else:
            self.cash += _cash

    def Cash(self, _capital):
        if( self.cash >= _capital ):
            self.cash -= _capital
        else:
            raise ValueError("Insufficient account balance")

    def _update_param(self):
        mtk_value = 0
        for code, row in self.stocks.iterrows():
            mtk_value += row['market_value']

        self.market_value = self.cash - self.credit + mtk_value
        self.max_value = max(self.max_value, self.market_value)
        self.min_value = min(self.min_value, self.market_value)
        self.max_back  = max(self.max_back , 1 - self.market_value/self.max_value)
        self.max_lever = max(self.max_lever, self.credit/self.market_value)

    def UpdateValue(self, prices):
        for code, row in self.stocks.iterrows():
            if code in prices:
                self.stocks.at[code, 'price'] = prices[code]
                self.stocks.at[code, 'market_value'] = prices[code]*row['volume']
        self._update_param()


    def ProfitDaily(self):
        self.cash *= 1.00005
        self.credit *= 1.0003
        self._update_param()

    def Format(self, volume, price):
        volume = int(volume/100) * 100
        _value = price*volume
        absv = abs(_value)

        if absv * 0.001 < 5: # 手续费 千一
            _commision = 5
        else:
            _commision = absv * 0.001

        if volume < 0: # 印花税,单边收
            _commision += absv * 0.001
        _commision += absv * 0.00002 # 过户费
        _cost = _value + _commision
        return _cost, _commision, volume

    def Volume(self, code):
        if code in self.stocks.index:
            volume = self.stocks.at[code, 'volume']
        else:
            volume = 0
        return volume

    def Order(self, code, prices, volume, order_time):
        if prices is object:
            if prices['low'] == prices['high']:
                return
            self._Order(code, prices['trade'], volume, order_time)
        elif prices is float:
            self._Order(code, prices, volume, order_time)

    def _Order(self, code, price, volume, order_time):
        _cost, _commision, volume = self.Format(volume, price)
        if not volume or (self.max_credit > 100 and self.credit + _cost - self.cash > self.max_credit):
            return 0
        order_time = StockDataSource.str_date( order_time )
        print(order_time, code, price, volume, _cost, _commision, self.cash, self.credit)

        if _cost < 0 and self.credit > 0:
            self.credit += _cost
            if self.credit < 0:
                self.cash -= self.credit
                self.credit = 0
        elif self.cash < _cost:
            if self.max_credit > 0 and self.credit + _cost - self.cash > self.max_credit:
                volume = (self.max_credit - self.credit + self.cash) / price
                _cost, _commision, volume = self.Format(volume, price)
                print('reset', order_time, code, price, volume, _cost, _commision, self.cash, self.credit)
            self.credit += _cost - self.cash
            self.cash = 0
        else:
            self.cash -= _cost
        self.cost += _commision

        if code in self.stocks.index:
            _row = self.stocks.loc[code]
            _volume = _row.volume + volume

            if _volume < 0:
                print(self.stocks.loc[code])
                raise ValueError("Don't naked short sale.")

            if _volume == 0:
                _cost_price = _row.cost_price
                if _row.volume*_row.cost_price + _cost < 0: 
                    self.succeed += 1
            else:
                _cost_price = (_row.volume*_row.cost_price + _cost) / _volume
            mkt_value = _volume*price
            self.stocks.loc[code] = [_volume, price, _cost_price, mkt_value, order_time]
            
        else:
            if volume <= 0:
                print(order_time, code, volume, price, self.cash)
                raise ValueError("Don't naked short sale.")
            _volume = volume
            _cost_price = _cost / volume
            mkt_value = volume*price

            _row = {'volume': [volume], 'price': [price], 'cost_price': [_cost_price], 
                'market_value': [mkt_value], 'order_time': [order_time]}
            _index = [code]
            self.stocks = self.stocks.append(pf.DataFrame(_row, _index))
            
        if volume < 0:
            self.short_count+= 1
        else:
            self.long_count += 1

        _clear_codes = []
        for code, row in self.stocks.iterrows():
            if row['volume'] < 10 and row['volume'] > -10:
                _clear_codes.append(code)
        if len(_clear_codes):
            self.stocks.drop(index = _clear_codes, axis = 0, inplace=True)

        self._update_param()
        lever = self.credit/self.market_value
        back_pump = 1 - self.market_value/self.max_value

        _record = (order_time, code, price, volume, volume*price, _commision, _cost, 
            _volume, mkt_value, self.cash, self.credit, self.market_value, lever, back_pump)
        self.records.append(_record)
        return volume


class StockDisp:
    '股票数据可视化'
    
    def __init__(self, title, subcount = 1, xlabel='date', ylabel='price'):
        if subcount == 1:
            self.fig, self.ax1 = plt.subplots(1, 1, sharex=True)
        else:
            self.fig, [self.ax1, self.ax2] = plt.subplots(2,1,sharex=True)
        self.fig.subplots_adjust(left=0.05, bottom=0.05, right=0.95, top=0.95)

        plt.xticks(rotation=45)
        plt.yticks()
        plt.xlabel(xlabel)

        self.ax1.xaxis_date()
        self.ax1.set_title(title)
        self.ax1.set_ylabel(ylabel)

    def show(self):
        plt.grid()
        plt.show()

    def save(self, filename, path='./images'):
        plt.savefig( path + '/' + filename)


    def LogKDisp(self, ax1, data_list):
        data_table = np.transpose( data_list )
        data_table[1] = list(map(lambda x: math.log(x), data_table[1]))
        data_table[2] = list(map(lambda x: math.log(x), data_table[2]))
        data_table[3] = list(map(lambda x: math.log(x), data_table[3]))
        data_table[4] = list(map(lambda x: math.log(x), data_table[4]))

        data_list = np.transpose( data_table )
        mpf.candlestick_ohlc(ax1, data_list, width=1.5, colorup='r', colordown='green')

    def LogPlot(self, ax1, dates, vals, _color='r', shift = 0, _label='label'):
        vals = list(map(lambda x: math.log(x)-shift, vals))
        ax1.plot(dates, vals, color=_color, lw=2, label=_label)

    def KDisp(self, ax1, data_list):
        mpf.candlestick_ohlc(ax1, data_list, width=1.5, colorup='red', colordown='green')

    def Plot(self, ax1, dates, vals, _color='r', shift = 0, _label='label'):
        if shift:
            vals = list(map(lambda x: x-shift, vals))
        ax1.plot(dates, vals, color=_color, lw=2, label=_label)


class MovingAverage:
    '股票的移动平均线'

    def __init__(self, _prices):
        self.ma_indexs = {}
        self.prices = np.asarray(_prices)
        # self.moving_average(self.prices, _n)

    def moving_average(self, n):
        mas = []

        if n in self.ma_indexs:
            return self.ma_indexs[n]

        elif n == 1:
            mas.append(self.prices[0])
            for i in range(1, len(self.prices)):
                mas.append(self.prices[i-1])

        elif n == 2:
            mas.append(self.prices[0])
            mas.append(self.prices[0])
            for i in range(2, len(self.prices)):
                mas.append((self.prices[i-1] + self.prices[i-2])/2)

        else: # if n not in self.ma_indexs:
            m1 = int(n/2)
            m2 = n - m1

            if m1 not in self.ma_indexs:
                self.moving_average(m1)
                # self.ma_indexs[m1] = self.moving_average(m1)
            hs1 = self.ma_indexs[m1]

            if m2 not in self.ma_indexs:
                self.moving_average(m2)
                # self.ma_indexs[m2] = self.moving_average(m2)
            hs2 = self.ma_indexs[m2]

            for i in range(0, m2):
                mas.append(hs2[i])
            for i in range(m2, len(self.prices)):
                mas.append((hs2[i]*m2 + hs1[i-m2]*m1)/n)
        
        self.ma_indexs[n] = mas
        return self.ma_indexs[n]


        #     if not hist_data is None:
        #         _rowcount = len(hist_data)
        #     if _rowcount:
        #         hist_data.index = range( _rowcount )

        # if not hist_data is None:
        #     _rowcount = len(hist_data)
        # else:
        #     hist_data = pf.DataFrame()

                # hist_data = StockDataSource.ts_api.daily(ts_code=code, start_date=startdate, end_date=enddate)
                # hist_data = StockDataSource.ts_api.weekly(ts_code=code, start_date=startdate, end_date=enddate)
                # hist_data = StockDataSource.ts_api.monthly(ts_code=code, start_date=startdate, end_date=enddate)

    # def parse_data(self, code):
    #     if code not in self.stocks:
    #         return []
    #     return self._parse_data(self.stocks[code])

        # print({ 'long': self.long_count, 'short': self.short_count, 'success': self.succeed, 
        #     'cash': self.cash, 'credit': self.credit, 'value': self.market_value, 'cost': self.cost, 
        #     'min value': self.min_value, 'max value': self.max_value, 'max back': self.max_back, 'max lever': self.max_lever })

    # def _clearup(self):
    #     _clear_codes = []
    #     for code, row in self.stocks.iterrows():
    #         if row['volume'] < 10 and row['volume'] > -10:
    #             _clear_codes.append(code)
    #     if len(_clear_codes):
    #         self.stocks.drop(index = _clear_codes, axis = 0, inplace=True)

        # if (code in self.stocks.index and volume <= 0 ) or self.stocks.at[code, 'volume'] + volume < 0:

                # print(order_time, code, price, volume, _cost, _commision, self.cash)
            # if( self.stocks.loc[code]['volume'] + volume < 0 ):
            #     raise ValueError("Don't naked short sale.")

            # print( 417, self.stocks.loc[code] )
            # print(self.cash, self.credit, _volume, _commision + _value, price, _cost_price, _volume*price, order_time)

            # print( 428, _row )
            # print(self.cash, self.credit, volume, _commision + _value, price, _cost_price, volume*price, order_time)

        # self._clearup()
        
# if __name__ == "__main__":
#     dataset = StockDataSource('./test')
#     data = dataset._download('600547.sh', '20070101', '20190101', 'stock', 'daily')
#     print( data )
    # data = dataset._download('000300.sh', '20180101', '20190101', 'index', 'daily')
    # print( data )
    # data = dataset._download('002001.sz', '20180101', '20190101', 'stock', 'daily')
    # print( data )


# def parse_stock_data(stock_data):
#     data_list = []
#     ave_price = []
#     volumes = []

#     for rnum, row in stock_data.iterrows():
#         tscode, trade_date, close, open, high, low = row[0:6]
#         vol,amount = row[9:11]
#         _date = dt.datetime.strptime(trade_date, '%Y%m%d')
#         timenum = date2num(_date)

#         datas = (timenum, open, high, low, close)
#         data_list.append(datas)
#         ave_price.append( (high+low)/2 )
#         volumes.append(vol)

#     data_table = np.transpose( data_list )
#     dates = data_table[0]
#     return dates, data_list, ave_price, volumes

        # if startdate is not np.int64:
        #     startdate = np.int64(startdate)
        # if enddate is not np.int64:
        #     enddate = np.int64(enddate)

            # _head = np.int64(local_data.at[0, 'trade_date'])
            # _tear = np.int64(local_data.at[_rowcount-1, 'trade_date'])
            # print(_head, _tear, enddate, startdate)
            # print(enddate - _head, _tear - startdate)

        # self.market_value = self.cash - self.credit + mkt_value
        # lever = self.credit/self.market_value
        # back_pump = 1 - self.market_value/self.max_value

        # self.max_value = max(self.max_value, self.market_value)
        # self.max_back  = max(self.max_back , back_pump)
        # self.max_lever = max(self.max_lever, lever)
        # print(self.stocks)

        # self.market_value = self.cash - self.credit
        # for code, row in self.stocks.iterrows():
        #     if code in prices:
        #         row['price'] = prices[code]
        #         row['market_value'] = row['price']*row['volume']
        #     self.market_value += row['market_value']

        # lever = self.credit/self.market_value
        # back_pump = 1 - self.market_value/self.max_value
        
        # self.max_value = max(self.max_value, self.market_value)
        # self.max_back  = max(self.max_back , back_pump)
        # self.max_lever = max(self.max_lever, lever)
