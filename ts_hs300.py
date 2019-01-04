#!/usr/bin/env python
#-*- coding: utf8 -*-
import argparse, datetime as dt
from matplotlib.pylab import date2num, num2date
from ttindex import TurTleIndex
from stock_utils import StockDataSet, StockDisp, StockAccount


hs300 = '000300.sh'
# hs300_stocks = [
#     ('sh', '603156', '养元饮品'), ('sh', '601138', '工业富联'), ('sz', '002001', '新和成'), ('sz', '000661', '长春高新'), ('sh', '600998', '九州通'), ('sz', '002179', '中航光电'), ('sh', '600004', '白云机场'), ('sz', '300296', '利亚德'), ('sh', '603986', '兆易创新'), ('sz', '002120', '韵达股份'), ('sz', '002311', '海大集团'), ('sz', '002422', '科伦药业'), ('sz', '002773', '康弘药业'), ('sh', '603259', '药明康德'), ('sh', '600027', '华电国际'), ('sz', '000408', '藏格控股'), ('sz', '002271', '东方雨虹'), ('sh', '600566', '济川药业'), ('sz', '000703', '恒逸石化'), ('sz', '002032', '苏泊尔'), ('sz', '300142', '沃森生物'), ('sh', '601066', '中信建投'), ('sh', '600760', '中航沈飞'), ('sz', '300408', '三环集团'), ('sz', '000786', '北新建材'), ('sh', '601808', '中海油服'), ('sh', '600176', '中国巨石'), ('sh', '600438', '通威股份'), ('sz', '002493', '荣盛石化'), ('sz', '001965', '招商公路'), ('sz', '002625', '光启技术'), ('sz', '300433', '蓝思科技'), ('sz', '002925', '盈趣科技'), 
#     ('sz', '002050', '三花智控'), ('sz', '002085', '万丰奥威'), ('sh', '600867', '通化东宝'), ('sh', '600809', '山西汾酒'), ('sh', '601838', '成都银行'), ('sh', '600339', '中油工程'), ('sh', '601108', '财通证券'), ('sh', '601360', '三六零'), ('sh', '600516', '方大炭素'), ('sh', '601238', '广汽集团'), ('sh', '600398', '海澜之家'), ('sh', '603288', '海天味业'), ('sh', '601828', '美凯龙'), ('sh', '600025', '华能水电'), ('sh', '600346', '恒力股份'), ('sh', '600487', '亨通光电'), ('sh', '603260', '合盛硅业'), ('sh', '603833', '欧派家居'), ('sh', '600011', '华能国际'), ('sh', '603799', '华友钴业'), ('sz', '002624', '完美世界'), ('sz', '002572', '索菲亚'), ('sz', '300003', '乐普医疗'), ('sz', '002468', '申通快递'), ('sz', '002601', '龙蟒佰利'), ('sh', '601012', '隆基股份'), ('sh', '600390', '五矿资本'), ('sz', '002294', '信立泰'), ('sz', '300136', '信维通信'), ('sz', '300015', '爱尔眼科'), ('sz', '000898', '鞍钢股份'), ('sh', '601212', '白银有色'), ('sh', '600219', '南山铝业'), 
#     ('sh', '601898', '中煤能源'), ('sh', '601991', '大唐发电'), ('sz', '300122', '智飞生物'), ('sh', '601878', '浙商证券'), ('sz', '002460', '赣锋锂业'), ('sh', '601228', '广州港'), ('sz', '002555', '三七互娱'), ('sz', '002558', '世纪游轮'), ('sz', '002602', '世纪华通'), ('sh', '600233', '圆通速递'), ('sz', '002508', '老板电器'), ('sz', '002411', '必康股份'), ('sz', '002352', '顺丰控股'), ('sz', '002044', '美年健康'), ('sz', '000959', '首钢股份'), ('sz', '000961', '中南建设'), ('sh', '600436', '片仔癀'), ('sh', '600522', '中天科技'), ('sh', '600909', '华安证券'), ('sh', '603160', '汇顶科技'), ('sh', '603858', '步长制药'), ('sh', '601997', '贵阳银行'), ('sh', '601992', '金隅股份'), ('sh', '601881', '中国银河'), ('sh', '601229', '上海银行'), ('sh', '601117', '中国化学'), ('sh', '600977', '中国电影'), ('sh', '600926', '杭州银行'), ('sh', '600919', '江苏银行'), ('sh', '600549', '厦门钨业'), ('sh', '601155', '新城控股'), ('sz', '300033', '同花顺'), ('sz', '002466', '天齐锂业'), 
#     ('sz', '000627', '天茂集团'), ('sz', '002714', '牧原股份'), ('sz', '300072', '三聚环保'), ('sh', '600482', '中国动力'), ('sz', '000983', '西山煤电'), ('sz', '000671', '阳光城'), ('sz', '000938', '紫光股份'), ('sh', '601611', '中国核建'), ('sz', '002797', '第一创业'), ('sz', '002310', '东方园林'), ('sh', '601877', '正泰电器'), ('sh', '600498', '烽火通信'), ('sh', '600297', '广汇汽车'), ('sz', '000839', '中信国安'), ('sz', '002027', '分众传媒'), ('sh', '600061', '国投安信'), ('sh', '600606', '绿地控股'), ('sh', '600704', '物产中大'), ('sh', '600816', '安信信托'), ('sz', '001979', '招商蛇口'), ('sz', '000415', '渤海租赁'), ('sz', '300144', '宋城演艺'), ('sh', '601198', '东兴证券'), ('sh', '601211', '国泰君安'), ('sh', '601985', '中国核电'), ('sz', '002736', '国信证券'), ('sz', '300059', '东方财富'), ('sh', '600958', '东方证券'), ('sh', '601021', '春秋航空'), ('sh', '601788', '光大证券'), ('sh', '601919', '中国远洋'), ('sz', '000166', '申万宏源'), 
#     ('sh', '601727', '上海电气'), ('sh', '600570', '恒生电子'), ('sh', '600038', '哈飞股份'), ('sz', '300251', '光线传媒'), ('sz', '300124', '汇川技术'), ('sz', '300070', '碧水源'), ('sz', '300024', '机器人'), ('sz', '300017', '网宿科技'), ('sz', '002153', '石基信息'), ('sz', '000413', '东旭光电'), ('sh', '601216', '内蒙君正'), ('sh', '601225', '陕西煤业'), ('sh', '600023', '浙能电力'), ('sz', '002252', '上海莱士'), ('sz', '000503', '海虹控股'), ('sz', '002475', '立讯精密'), ('sz', '002008', '大族激光'), ('sz', '002456', '欧菲光'), ('sz', '002230', '科大讯飞'), ('sz', '002065', '东华软件'), ('sz', '000826', '桑德环境'), ('sh', '600018', '上港集团'), ('sh', '600688', '上海石化'), ('sh', '600705', '中航投资'), ('sz', '000333', '美的集团'), ('sz', '000963', '华东医药'), ('sz', '002450', '康得新'), ('sh', '600332', '广州药业'), ('sh', '603993', '洛阳钼业'), ('sz', '002236', '大华股份'), ('sz', '002673', '西部证券'), ('sh', '600157', '永泰能源'), ('sh', '600340', '华夏幸福'), 
#     ('sh', '600637', '百视通'), ('sh', '600886', '国投电力'), ('sh', '601800', '中国交建'), ('sz', '002081', '金螳螂'), ('sz', '002241', '歌尔声学'), ('sh', '601336', '新华保险'), ('sh', '601555', '东吴证券'), ('sh', '601633', '长城汽车'), ('sh', '601669', '中国水电'), ('sh', '601901', '方正证券'), ('sh', '600372', '中航电子'), ('sz', '002594', '比亚迪'), ('sh', '601018', '宁波港'), ('sh', '601377', '兴业证券'), ('sh', '601933', '永辉超市'), ('sz', '000776', '广发证券'), ('sz', '002146', '荣盛发展'), ('sz', '002415', '海康威视'), ('sh', '600115', '东方航空'), ('sh', '600406', '国电南瑞'), ('sh', '600276', '恒瑞医药'), ('sh', '600535', '天士力'), ('sh', '600703', '三安光电'), ('sh', '600887', '伊利股份'), ('sh', '600893', '航空动力'), ('sh', '601818', '光大银行'), ('sh', '601288', '农业银行'), ('sz', '002304', '洋河股份'), ('sh', '600999', '招商证券'), ('sh', '601607', '上海医药'), ('sh', '601688', '华泰证券'), ('sh', '601888', '中国国旅'), ('sh', '601989', '中国重工'), 
#     ('sz', '002007', '华兰生物'), ('sh', '600369', '西南证券'), ('sh', '601618', '中国中冶'), ('sh', '601668', '中国建筑'), ('sh', '600518', '康美药业'), ('sh', '601766', '中国南车'), ('sh', '600352', '浙江龙盛'), ('sh', '600588', '用友软件'), ('sh', '600674', '川投能源'), ('sh', '601186', '中国铁建'), ('sh', '601899', '紫金矿业'), ('sz', '000728', '国元证券'), ('sz', '000783', '长江证券'), ('sz', '002202', '金风科技'), ('sh', '601390', '中国中铁'), ('sh', '601601', '中国太保'), ('sh', '601939', '建设银行'), ('sh', '601169', '北京银行'), ('sh', '601009', '南京银行'), ('sh', '600111', '包钢稀土'), ('sh', '600089', '特变电工'), ('sz', '002142', '宁波银行'), ('sz', '000895', '双汇发展'), ('sz', '000423', '东阿阿胶'), ('sz', '000338', '潍柴动力'), ('sh', '600109', '国金证券'), ('sh', '601857', '中国石油'), ('sh', '601088', '中国神华'), ('sh', '601333', '广深铁路'), ('sz', '000876', '新希望'), ('sh', '600837', '海通证券'), ('sh', '600208', '新湖中宝'), ('sh', '601328', '交通银行'), 
#     ('sh', '601998', '中信银行'), ('sh', '601600', '中国铝业'), ('sh', '601318', '中国平安'), ('sh', '601166', '兴业银行'), ('sh', '601628', '中国人寿'), ('sh', '600066', '宇通客车'), ('sh', '600118', '中国卫星'), ('sh', '600489', '中金黄金'), ('sh', '600048', '保利地产'), ('sh', '600068', '葛洲坝'), ('sh', '601111', '中国国航'), ('sh', '600547', '山东黄金'), ('sh', '601398', '工商银行'), ('sh', '601006', '大秦铁路'), ('sh', '601988', '中国银行'), ('sh', '600415', '小商品城'), ('sh', '600271', '航天信息'), ('sh', '600383', '金地集团'), ('sz', '000768', '西飞国际'), ('sz', '002024', '苏宁电器'), ('sz', '000538', '云南白药'), ('sz', '000157', '中联重科'), ('sz', '000425', '徐工科技'), ('sz', '000568', '泸州老窖'), ('sh', '600019', '宝钢股份'), ('sz', '000630', '铜陵有色'), ('sz', '000651', '格力电器'), ('sz', '000625', '长安汽车'), ('sz', '000709', '唐钢股份'), ('sz', '000792', '盐湖钾肥'), ('sz', '000063', '中兴通讯'), ('sz', '000402', '金融街'), ('sh', '600050', '中国联通'), 
#     ('sh', '600036', '招商银行'), ('sh', '600031', '三一重工'), ('sh', '600030', '中信证券'), ('sh', '600029', '南方航空'), ('sh', '600015', '华夏银行'), ('sh', '600028', '中国石化'), ('sh', '600016', '民生银行'), ('sh', '600010', '包钢股份'), ('sh', '600009', '上海机场'), ('sh', '600900', '长江电力'), ('sh', '600795', '国电电力'), ('sh', '600739', '辽宁成大'), ('sh', '600741', '巴士股份'), ('sh', '600690', '青岛海尔'), ('sh', '600221', '海南航空'), ('sh', '600583', '海油工程'), ('sh', '600585', '海螺水泥'), ('sh', '600519', '贵州茅台'), ('sz', '000858', '五粮液'), ('sh', '600309', '烟台万华'), ('sh', '600196', '复星医药'), ('sh', '600000', '浦发银行'), ('sh', '600660', '福耀玻璃'), ('sh', '600085', '同仁堂'), ('sh', '600100', '同方股份'), ('sh', '600104', '上海汽车'), ('sh', '600153', '建发股份'), ('sh', '600188', '兖州煤业'), ('sh', '600177', '雅戈尔'), ('sh', '600170', '上海建工'), ('sh', '600362', '江西铜业')
# ]
hs300_stocks = [
    ('sh', '603156', '养元饮品'), ('sh', '601138', '工业富联'), ('sz', '002001', '新和成'), ('sz', '000661', '长春高新'), ('sh', '600998', '九州通'), ('sz', '002179', '中航光电'), ('sh', '600004', '白云机场'), ('sz', '300296', '利亚德'), ('sh', '603986', '兆易创新'), ('sz', '002120', '韵达股份'), ('sz', '002311', '海大集团'), ('sz', '002422', '科伦药业'), ('sz', '002773', '康弘药业'), ('sh', '603259', '药明康德'), ('sh', '600027', '华电国际') 
]


startdate = '20070101'
enddate = '20190101'
start_date = date2num(dt.datetime.strptime(startdate, '%Y%m%d'))
end_date = date2num(dt.datetime.strptime(enddate, '%Y%m%d'))

loss_unit = 0.01
append = 1
stop_loss = 3
long_cycle = 55
short_cycle= 20
strong_cycle=120

def InputArgs():
    parser = argparse.ArgumentParser(description="show example")
    # parser.add_argument('hs300_stocks', default=['000300.sh'], nargs='*')
    parser.add_argument("-s", "--start_date", default='20130101', help="start date")
    parser.add_argument("-e", "--end_date", default='20190101', help="end date")
    parser.add_argument("-a", "--append", default=0.01, help="append")
    parser.add_argument("-l", "--stop_loss", default=1, help="stop loss")
    parser.add_argument("-u", "--loss_unit", default=3, help="loss unit")

    ARGS = parser.parse_args()
    if ARGS.start_date:
        startdate = str(ARGS.start_date)
    if ARGS.end_date:
        enddate = str(ARGS.end_date)

    if ARGS.loss_unit:
        loss_unit = float(ARGS.loss_unit)
    if ARGS.append:
        append = float(ARGS.append)
    if ARGS.stop_loss:
        stop_loss = float(ARGS.stop_loss)

    # if ARGS.hs300_stocks:
    #     hs300_stocks = ARGS.hs300_stocks

    _date = dt.datetime.strptime(startdate, '%Y%m%d')
    start_date = date2num(_date)
    _date = dt.datetime.strptime(enddate, '%Y%m%d')
    end_date = date2num(_date)
    # print( type(start_date) )


def loaddata(dataset, start_index, end_index):
    for i in range(start_index, end_index): # stock in stocks:
        stock = hs300_stocks[i]
        code = stock[1] + '.' + stock[0]
        dataset.load(code, startdate, enddate, 'stock', 'daily')
        print("load", str(i), "stocks.")
    
if __name__ == "__main__":
    InputArgs()
    dataset = StockDataSet()

    codes = []
    date_vecs = {}
    data_indexs = {}

    closes = {}
    long_indexs = {}
    turtles = {}

    # data_lists = {}
    # dataset.load(hs300, startdate, enddate, 'index', 'daily')
    # data_lists[hs300] = _list
    # turtles[hs300] = TurTleIndex(_list, long_cycle, short_cycle, append, stop_loss)

    dataset.read(hs300, 'daily')
    index_dates, hs300_list, ave_price, volumes = dataset.parse_data(hs300)

    turtles[hs300] = TurTleIndex(hs300_list)
    turtles[hs300].price_wave(long_cycle, short_cycle)
    turtles[hs300].long_trade(long_cycle, short_cycle, append, stop_loss)

    closes[hs300] = turtles[hs300].data['close']
    hs300_states = turtles[hs300].data['state']
    # keyprice = turtles[hs300].data['key_prices']
    # Nl = turtles[hs300].data['long_wave']

    for stock in hs300_stocks:
        code = stock[1] + '.' + stock[0]
        codes.append(code)
        
        # dataset.load(code, startdate, enddate, 'stock', 'daily')
        # data_lists[code] = _list
        # turtles[code] = TurTleIndex(_list, long_cycle, short_cycle, append, stop_loss)

        dataset.read(code, 'daily')
        _dates, _list, ave_price, volumes = dataset.parse_data(code)
        date_vecs[code] = _dates

        turtles[code] = TurTleIndex(_list)
        long_indexs[code] = turtles[code].long_index(120)
        data_indexs[code] = 0
        closes[code] = turtles[code].data['close']

    # print ( closes[hs300] )
    # print ( closes[codes[0]] )

    account = StockAccount(100000, 0)
    count = 0
    cash_unit = account.cash

    market_values = []
    market_values.append(account.market_value)
    account.ProfitDaily()
    # print( codes )

    for _idx in range(len(index_dates)-1, len(index_dates)):
        account.ProfitDaily()
        _date = index_dates[_idx]
        _close = {}
        _curr_stocks = []

        if _date < start_date or _date > end_date:
            market_values.append(account.market_value)
            continue

        if count < hs300_states[_idx] and count < 4:
            count = hs300_states[_idx]
            # if count == 1:
            #     cash_unit = account.cash * loss_unit * keyprice[i] / Nl[i]
            # volume = cash_unit / kp
            # if volume >= 100: 
            #     account.Order(code, kp, volume, dates[i])

        elif count and not hs300_states[_idx]:
            count = hs300_states[_idx]
            # volume = account.stocks.at[code, 'volume']
            # account.Order(code, kp, -volume, dates[i])

        for code in codes:
            dates = date_vecs[code]
            while data_indexs[code] < len(dates) and dates[data_indexs[code]] < _date:
                data_indexs[code] += 1
            if data_indexs[code] >= len(dates) or dates[data_indexs[code]] > _date: 
                continue
            _close[code] = closes[code][data_indexs[code]]
            _curr_stocks.append({'code': code, 'close': _close[code], 'strong': long_indexs[code][data_indexs[code]]})
        _sorted_stocks = sorted(_curr_stocks, key = lambda stock: stock['strong'], reverse = True)

        account.UpdateValue(_close)
        market_values.append(account.market_value)

    # plot = StockDisp(hs300)
    # plot.LogKDisp(plot.ax1, hs300_list)
    # plot.LogPlot(plot.ax1, index_dates, market_values, 'r', 4)
    # # plot.LogPlot(plot.ax2, index_dates, Nl, 'r')
    # plot.Plot(plot.ax2, index_dates, long_counts, 'B')
    # plot.show()

    account.status_info()
    # account.save_records('./data', 'tt-first')
    # print( account.get_records() )


    # loaddata(dataset, 290, 294)
    # print( StockDataSet.float_date('20190104') )
    # print( StockDataSet.datetime('20190104') )
    

    # index_data = dataset.load(hs300, startdate, enddate, 'index', 'daily')
    # for stock in stocks:
        # code = stock[1] + '.' + stock[0]
        # stock_data = dataset.load(code, startdate, enddate, 'stock', 'daily')

