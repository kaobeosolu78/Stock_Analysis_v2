import pickle
import os.path
import numpy as np
from pytrends.request import TrendReq
import pytrends
import pandas as pd
import plotly.plotly as py
from plotly import tools
import plotly.graph_objs as goo
import plotly.offline
from datetime import date,datetime
import operator
from pytrendsdaily import dailydata

def load_obj(datatype):
    with open("{}".format(datatype) + '.pkl', 'rb') as f:
        return pickle.load(f)

def get_google_trends(trends):
    prods = []
    for trend in trends:
        alll = {}
        cruc = ["all","today 5-y","today 3-m"]
        for k in range(3):
            if k == 2:
                dub = dailydata.getDailyData(trend, 2014, 2019)
            else:
                pytrends = TrendReq(hl='en-US', tz=360)
                pytrends.build_payload([trend], cat=0, timeframe=cruc[k], geo='', gprop='')
                dub = pytrends.interest_over_time()
            alll[cruc[k]] = dub
        prods.append(alll)
    return prods

def get_trends(trendname,trendprods):
    if trendname[0] != "":
        tname = trendname
        count = -1
        # for ind in tname:
        #     count += 1
        #     if ind in list(trendprods.keys()):
        #         del(trendname[count])
        # if len(trendname) == 0:
        #     return trendprods

        trend = (get_google_trends(trendname))
        tp = ["all", "today 5-y", "today 3-m"]
        count = -1
        for tren in trend:
            count += 1
            full = []
            for k in range(3):
                values = [[],[]]
                [(values[0].append(t[0]),values[1].append(ind)) for ind,t in tren[tp[k]].iterrows()]
                full.append(singlegtrend(trendname,values[1],values[0]))

            trendprods[trendname[count]] = gtrend(full[0],full[1],full[2])
        pick_out = open("trendprods.pkl","wb")
        pickle.dump(trendprods,pick_out,pickle.HIGHEST_PROTOCOL)
        pick_out.close()
    return trendprods

class singlegtrend:
    def __init__(self,name,times,values):
        self.name = name
        self.times = times
        self.values = values

    def average(self):
        self.average = sum(self.values)/len(self.values)
        return self.average

    def __add__(self,trend_list):
        final_list = self.values
        if type(trend_list) != list:
            trend_list = [trend_list]
        for ob in trend_list:
            for i in range(len(self.values)):
                final_list[i] += ob.values[i]
        return [val/(len(trend_list)+1) for val in final_list]

class gtrend:
    def __init__(self,all=None,fiveyear=None,threemonth=None):
        self.all = all
        self.fiveyear = fiveyear
        self.threemonth = threemonth

    def week_avg(self):
        dates = self.threemonth.times
        vals = self.threemonth.values
        while dates[0].weekday() != 6:
            dates = dates[1:]
            vals = vals[1:]
        while dates[len(dates)-1].weekday() != 6:
            dates = dates[:(len(dates)-1)]
            vals = vals[:len(vals)-1]
        endd = dates[-7:]#sorted(dates[-7:], key=operator.methodcaller('weekday'))
        endv = [0,0,0,0,0,0,0]
        count = 0
        for k in range(len(dates)):
            if count == 7:
                count = 0
            endv[count] += vals[k]
            count += 1
        return [[ending.strftime("%A") for ending in endd],[end/(len(dates)/7) for end in endv]]

    def update(self,name):
        trendprods = load_obj("trendprods")
        return get_trends([name], trendprods)