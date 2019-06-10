from trends import singlegtrend,gtrend,load_obj
from stocks import stock,stock_store
import plotly.plotly as py
import numpy as np
from plotly import tools
import plotly.graph_objs as goo
import plotly.offline
from operator import itemgetter
import pickle
import math
from sklearn.linear_model import LinearRegression


def graph(x,y,name="",sep=False,header=""):
    if sep == True:
        j = k
        fig = tools.make_subplots(rows=len(x), cols=1, shared_xaxes=True, shared_yaxes=True)
    else:
        j = 0
        fig = tools.make_subplots(rows=1, cols=1, shared_xaxes=True, shared_yaxes=True)

    if type(y[0]) == list and type(x[0]) == list:
        for k in range(len(y)):
            fig.append_trace(goo.Scatter(x=x[k],y=y[k],name = name[k]),j+1,1)
    elif type(y[0]) == list and type(x[0]) != list:
        for k in range(len(y)):
            fig.append_trace(goo.Scatter(x=x,y=y[k],name = name),j+1,1)
    else:
        fig.append_trace(goo.Scatter(x=x,y=y,name=name),1,1)
    fig["layout"].update(title=header)
    plotly.offline.plot({"data": fig, "layout": goo.Layout(title=header)})
    return

def compartment(stock_tick,trendss,timeframe):
    if type(trendss) != list:
        trendss = [trendss]
    for trends in trendss:
        tf = {"day":["threemonth","day_ts"],"month":["all","month_ts"]}
        finaltrendprods = 0
        sprod = 0
        tprods = []
        if type(trends) == str:
            trends = [trends]
        for trend in trends:
            try:
                tprods.append(getattr(load_obj("trendprods")[trend],tf[timeframe][0]))
            except:
                gtrend().update(trend)
                trends.append(trend)
        if len(tprods) != 1:
            finaltrendprods = tprods[0] + tprods[1:]
        else:
            finaltrendprods = tprods[0].values
        sprod = getattr(load_obj("stock_data")[stock_tick.upper()],tf[timeframe][1])

        prods = sprod.match_dates(tprods[0].times, finaltrendprods, "pv_delta")
        print(backtester(prods["trend data"], prods["stock data"],"trend"))

    return

def trend_rms(trends,prices):
    rmsdiff = 0
    prices = [float(price) for price in prices]
    for (x, y) in zip(np.array(trends),np.array(prices)):
        rmsdiff += (x - y) ** 2  # NOTE: overflow danger if the vectors are long!
    rmsdiff = math.sqrt(rmsdiff / min(len(trends), len(prices)))
    return rmsdiff




