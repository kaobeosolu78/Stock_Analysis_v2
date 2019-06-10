import alpha_vantage
import pickle
import requests
import datetime
from datetime import timedelta
import plotly.plotly as py
from plotly import tools
import plotly.graph_objs as goo
import plotly.offline
from dateutil.relativedelta import relativedelta
import numpy as np
from pandas import to_datetime
import math


def date_range(start, end, delta):
    current = start
    if not isinstance(delta, timedelta):
        delta = relativedelta(**delta)
    while current < end:
        yield current
        current += delta


def load_obj(datatype):
    with open("{}".format(datatype) + '.pkl', 'rb') as f:
        return pickle.load(f)


def get(index, mode):
    API_URL = "https://www.alphavantage.co/query"
    help = ["Monthly Time Series", "Weekly Time Series", "Time Series (Daily)"]
    help2 = ["TIME_SERIES_MONTHLY", "TIME_SERIES_WEEKLY", "TIME_SERIES_DAILY"]
    dates = []
    close = []
    volume = []
    ope = []
    high = []
    low = []
    data = {
        "function": help2[mode],
        "symbol": "{}".format(index),
        # "interval": "60min",
        "outputsize": "full",
        "datatype": "json",
        "apikey": "4PONUNLFLKWOK7UU",
        "retries": 10
    }

    try:
        dub = ((requests.get(API_URL, params=data)).json())
        datees = ((dub[help[mode]]).keys())
    except:
        dub = ((requests.get(API_URL, params=data)).json())
        datees = ((dub[help[mode]]).keys())

    for key in datees:
        close.append(((dub[help[mode]])[key])["4. close"])
        volume.append(((dub[help[mode]])[key])["5. volume"])
        ope.append(((dub[help[mode]])[key])["1. open"])
        high.append(((dub[help[mode]])[key])["2. high"])
        low.append(((dub[help[mode]])[key])["3. low"])

    for key in (datees):
        dates.append((key))

    dat = stock([dates, close, volume, ope, high, low], index, help2[mode])
    return dat


def fix_dates(dates, values, tf="days"):
    wekday = timedelta(days=0)
    dub = timedelta(days=0)

    if tf == "weeks":
        wekday = timedelta(days=(dates[len(dates) - 1]).weekday())
    elif tf == "days":
        dub = timedelta(days=1)

    actual_dates = list(date_range(datetime.datetime.strptime(dates[0], "%Y-%m-%d") + wekday,
                                   datetime.datetime.strptime(dates[len(dates) - 1], "%Y-%m-%d") + dub, {tf: 1}))[::-1]

    if tf != "days":
        return values, actual_dates

    products = []
    for value in values:
        counter = 0
        counter2 = 0
        prods = []
        while counter < len(actual_dates):
            if datetime.datetime.strftime(actual_dates[counter], "%Y-%m-%d") not in dates:
                prods.append(0)
            else:
                prods.append(value[counter2])
                counter2 += 1
            counter += 1
        products.append(prods)

    return [products, actual_dates]

class stock:
    def __init__(self,data,name,type):
        if type == "TIME_SERIES_DAILY":
            temp = fix_dates(data[0][::-1],data[1:])
            self.dates = temp[1]
            self.close = temp[0][0]
            self.volume = temp[0][1]
            self.open = temp[0][2]
            self.high = temp[0][3]
            self.low = temp[0][4]
            self.pv_delta = [float(self.close[k]) - float(self.open[k]) for k in range(len(self.dates))]

        else:
            if type == "TIME_SERIES_MONTHLY":
                self.dates = [(datetime.datetime.strptime(date, "%Y-%m-%d")).replace(day=1) for date in data[0]][::-1]
            else:
                self.dates = [datetime.datetime.strptime(date, "%Y-%m-%d") for date in data[0]][::-1]
            self.close = [float(c) for c in data[1]][::-1]
            self.volume = [float(v) for v in data[2]][::-1]
            self.open = [float(o) for o in data[3]][::-1]
            self.high = [float(h) for h in data[4]][::-1]
            self.low = [float(l) for l in data[5]][::-1]
        self.dtype = type
        self.name = name

    def match_dates(self,trend_dates,trend_data,dataattr):
        stock_dates = self.dates
        stock_data = getattr(self,dataattr)#greaterThan(t)
        # trend_dates = match.times
        # trend_data = match.values

        for k in range(len(stock_dates)):
            if stock_dates[k] in trend_dates:
                stock_dates = stock_dates[k:]
                stock_data = stock_data[k:]
                break
        for i in range(1,len(stock_dates)):
            if stock_dates[-i] in trend_dates:
                if i == 1:
                    pass
                else:
                    stock_dates = stock_dates[:-i]
                    stock_data = stock_data[:-i]
                break

        for j in range(len(trend_dates)):
            if trend_dates[j] in stock_dates:
                trend_dates = trend_dates[j:]
                trend_data = trend_data[j:]
                break
        for h in range(1,len(trend_dates)):
            if trend_dates[-h] in stock_dates:
                if h == 1:
                    pass
                else:
                    trend_dates = trend_dates[:-h]
                    trend_data = trend_data[:-h]
                break
        return {"trend dates":trend_dates,"trend data":trend_data,"stock dates":stock_dates[::-1],"stock data":[float(f) for f in stock_data[::-1]]}

    def backtester(self,trendsobj,averages=[1 for j in range(2000)],std=[1 for j in range(2000)],lookahead=7,timeframe="all"):
        start = datetime.datetime.strptime("1-01-2018", "%d-%m-%Y")
        end = datetime.datetime.strptime("1-01-2019", "%d-%m-%Y")
        date_generated = [start + datetime.timedelta(days=x) for x in range(0, (end - start).days)]
        date_gen = {}
        t = -1
        for date in date_generated:
            t += 1
            date_gen[date] = t
        try:
            temp = self.match_dates(trendsobj.times, trendsobj.values, "pv_delta")
            trends,prices,dates = temp["trend data"],temp["stock data"],temp["trend dates"]
        except:
            trends = [1 for j in range(2000)]
            prices,dates = self.pv_delta,self.dates
        steps,lim = [5,5,5],[]
        for i in range(3):
            if [averages,trends,std][i] == [1 for j in range(2000)]:
                steps[i] = 1

        if timeframe == "past year":
            for y in range(len(dates)):
                if dates[y].year == 2019 or dates[y].year == 2018:
                    current_dates = dates[y:]
                    current_prices = prices[y:]
                    current_trends = trends[y:]
                    dates = dates[:y]
                    prices = prices[:y]
                    trends = trends[:y]
                    break
        best_setup = {"Profit":0,"Total Days":0,"Total Days In":len(prices),"Down Days":0,"After":0,"Progress":[[],[]],"Progress Control":[[],[]],"Values":{"Average":0,"STD":0,"Trend":0}}
        price_control = 0
        for p2 in range(len(prices)):
            if 0+p2 < len(prices)-1:
                price_control += prices[p2]
                best_setup["Progress Control"][0].append(dates[p2])
                best_setup["Progress Control"][1].append(price_control)
        for l in range(lookahead):
            for a in np.linspace(min(averages),max(averages),steps[0]):
                for t in np.linspace(min(trends), max(trends), steps[1]):
                    for s in np.linspace(min(std),max(std),steps[2]):
                        year,price,count,sign = 0,0,0,0
                        progress = [[],[]]
                        for p in range(len(prices)):
                            try:
                                # year = date_generated.index((dates[p].replace(year=2018)))
                                year = date_gen[dates[p].replace(year = 2018)]
                                avg_t = averages[year]
                                std_t = std[year]
                            except:
                                avg_t = a
                                std_t = s
                            if l+p < len(prices)-1 and avg_t >= a and trends[p] >= t and std_t >= s:
                                count += 1
                                price += prices[p+l]
                                progress[0].append(dates[p+l])
                                progress[1].append(price)
                                if prices[p+l] < 0:
                                    sign += 1
                            elif l+p < len(prices)-1:
                                progress[0].append(dates[p + l])
                                progress[1].append(price)
                        if best_setup["Profit"] < price-sum(prices):
                            print(price)
                            best_setup = {"Profit":price-sum(prices),"Total Days":len(prices),"Total Days In":count,"Down Days":sign,"After":l,"Progress":progress,"Progress Control":best_setup["Progress Control"],"Values":{"Average":a,"STD":s,"Trend":t}}


        if timeframe == "past year":
            current_price, count, sign = 0, 0, 0
            best_setup["Progress"] = [[],[]]
            trends = trends[y:]

            for p in range(len(current_dates)):
                if best_setup["After"] + p < len(current_prices)-1 and averages[p] >= best_setup["Values"]["Average"] and current_trends[p] >= best_setup["Values"]["Trend"] and std[p] >= best_setup["Values"]["STD"]:
                    count += 1
                    current_price += current_prices[p+best_setup["After"]]
                    if prices[p + best_setup["After"]] < 0:
                        sign += 1
                if best_setup["After"]+p<len(current_prices)-1:
                    best_setup["Progress"][0].append(current_dates[p + best_setup["After"]])
                    best_setup["Progress"][1].append(current_price)
            best_setup["Profit"],best_setup["Total Days"],best_setup["Total Days In"],best_setup["Down Days"] = current_price-sum(current_prices),len(current_dates),count,sign
            prices,dates = current_prices,current_dates
        best_setup["Progress Control"] = [[],[]]
        price_control = 0
        for p2 in range(len(prices)):
            # if best_setup["After"]+p2 < len(prices)-1:
                price_control += prices[p2]
                best_setup["Progress Control"][0].append(dates[p2])
                best_setup["Progress Control"][1].append(price_control)

        return best_setup

class stock_store:
    dtypes = ["TIME_SERIES_MONTHLY","TIME_SERIES_WEEKLY","TIME_SERIES_DAILY"]
    def __init__(self,month=None,week=None,day=None):
        self.month_ts = month
        self.week_ts = week
        self.day_ts = day

    def update(self,name):
        stock_data = load_obj("stock_data")
        month_ts = 0
        week_ts = 0
        day_ts = 0
        for k in range(3):
            newnew = get(name,k)
            if newnew.dtype == self.dtypes[0]:
                month_ts = newnew
            if newnew.dtype == self.dtypes[1]:
                week_ts = newnew
            if newnew.dtype == self.dtypes[2]:
                day_ts = newnew

        stock_data[name] = stock_store(month_ts,week_ts,day_ts)
        pick_out = open("stock_data.pkl", "wb")
        pickle.dump(stock_data, pick_out, pickle.HIGHEST_PROTOCOL)
        pick_out.close()
        return stock_data[name]

    def return_unk(self):
        return_v = []
        for ts in [self.month_ts,self.week_ts,self.day_ts]:
            try:
                return_v.append(ts.dtype)
            except:
                pass
        return return_v