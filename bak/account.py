#!/usr/bin/env python
#-*- coding: utf8 -*-
import numpy as np, pandas as pf
from matplotlib.pylab import date2num, num2date


class StockAccount:
    '股票交易账户'

    def __init__(self, cash, max_credit = 0):
        self.max_credit = max_credit
        self.cash = cash
        self.credit = 0
        self.cost = 0

        self.max_value = cash
        self.max_back = 0
        self.max_lever = 0

        self.long_count = self.short_count = self.succeed = 0

        self.stocks = pf.DataFrame()
        self.records = []

    def status_info(self):
        print( self.long_count, self.short_count, self.succeed, 
            self.cash, self.credit, self.market_value, self.cost, 
            self.max_value, self.max_back, self.max_lever)

    def get_records(self):
        records = pf.DataFrame(self.records, columns=['order_time', 'price', 
            'volume', 'amount', 'commision', 'total', 'total volume', 'total value',
            'cash', 'credit', 'market value', 'lever', 'back'])
        return records

    def save_records(self, path, code):
        records = self.get_records()
        records.to_csv(path + '/' + code + '.records.csv')

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

    def UpdateValue(self, prices):
        self.market_value = self.cash - self.credit
        for code, row in self.stocks.iterrows():
            row['price'] = prices[code]
            row['market_value'] = row['price']*row['volume']
            self.market_value += row['market_value']

        lever = self.credit/self.market_value
        back_pump = 1 - self.market_value/self.max_value
        
        self.max_value = max(self.max_value, self.market_value)
        self.max_back  = max(self.max_back , back_pump)
        self.max_lever = max(self.max_lever, lever)


    def ProfitDaily(self):
        self.cash *= 1.00005
        self.credit *= 1.0003

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
        # _commision = self.Commision(_value)
        _cost = _value + _commision
        return _cost, _commision, volume

    def Order(self, code, price, volume, order_time):
        _cost, _commision, volume = self.Format(volume, price)

        if _cost < 0 and self.credit > 0:
            self.credit += _cost
            if self.credit < 0:
                self.cash -= self.credit
                self.credit = 0
        elif self.cash < _cost:
            if self.max_credit > 0 and self.credit + _cost - self.cash > self.max_credit:
                volume = (self.max_credit - self.credit + self.cash) / price
                _cost, _commision, volume = self.Format(volume, price)
            self.credit += _cost - self.cash
            self.cash = 0
        else:
            self.cash -= _cost
            
        self.cost += _commision
        order_time = num2date(order_time).strftime('%Y%m%d')


        if  code in self.stocks.index:
            if( self.stocks.loc[code]['volume'] + volume < 0 ):
                raise ValueError("Don't naked short sale.")

            _row = self.stocks.loc[code]
            _volume = _row.volume + volume
            if _volume == 0:
                _cost_price = _row.cost_price
                if _row.volume*_row.cost_price + _cost < 0: 
                    self.succeed += 1
            else:
                _cost_price = (_row.volume*_row.cost_price + _cost) / _volume
            mkt_value = _volume*price
            # print(self.cash, self.credit, _volume, _commision + _value, price, _cost_price, _volume*price, order_time)
            self.stocks.loc[code] = [_volume, price, _cost_price, mkt_value, order_time]

        else:
            if( volume <= 0 ):
                raise ValueError("Don't naked short sale.")
            _cost_price = _cost / volume
            _volume = volume
            mkt_value = volume*price
            _row = {'volume': [volume], 'price': [price], 'cost_price': [_cost_price], 
                'market_value': [mkt_value], 'order_time': [order_time]}
            _index = [code]
            # print(self.cash, self.credit, volume, _commision + _value, price, _cost_price, volume*price, order_time)
            self.stocks = self.stocks.append(pf.DataFrame(_row, _index))

        if volume < 0:
            self.short_count+= 1
        else:
            self.long_count += 1

        self.market_value = self.cash - self.credit + mkt_value
        lever = self.credit/self.market_value
        # if self.max_value 
        back_pump = 1 - self.market_value/self.max_value

        self.max_value = max(self.max_value, self.market_value)
        self.max_back  = max(self.max_back , back_pump)
        self.max_lever = max(self.max_lever, lever)

        _record = (order_time, price, volume, volume*price, _commision, _cost, 
            _volume, mkt_value, self.cash, self.credit, self.market_value, lever, back_pump)
        self.records.append(_record)


    # def Commision(self, _value):
    #     absv = abs(_value)
    #     if absv * 0.001 < 5: # 手续费 千一
    #         _commision = 5
    #     else:
    #         _commision = absv * 0.001

    #     if volume < 0: # 印花税,单边收
    #         _commision += absv * 0.001
    #     _commision += absv * 0.00002 # 过户费
    #     return _commision

        # volume = int(volume/100) * 100
        # _value = price*volume
        # _commision = self.Commision(_value)
        # _cost = _value + _commision
        
        # print(code, price, volume, price*volume, self.cash)
        # if( self.cash < _value ):
        #     raise ValueError("not sufficient funds.")

                # _cash = 500000 - self.credit + self.cash
                # volume = _cash/price
                # volume = int(volume/100) * 100
                # _value = price*volume
                # _commision = self.Commision(_value)
                # _cost = _value + _commision

        # print(self.stocks)
        # print(self.cash, self.market_value, self.stocks.loc[code, 'volume'], 
        #     self.stocks.loc[code, 'price'], self.stocks.loc[code, 'order_time'])

    # stocks = pf.DataFrame()
    # records = []

    # market_value = 0
    # cash = 0
    # cost = 0
    # credit = 0

    # long_count = 0
    # short_count= 0
    # succeed = 0

    # max_value = 0
    # max_back = 0
    # max_lever = 0

    # def prt(self):
    #     print( "total balance = " , (self.market_value + self.cash), \
    #         "\nmarket value = " , self.market_value, "\ncapital = " , self.cash )
