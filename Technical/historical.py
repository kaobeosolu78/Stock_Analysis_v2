from trends import singlegtrend,gtrend,load_obj
from stocks import stock,stock_store
import pickle
import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from plotly import tools
import plotly.graph_objs as goo
import plotly.offline
import numpy as np
from smain import graph

def date_range(start, end, delta):
    current = start
    if not isinstance(delta, timedelta):
        delta = relativedelta(**delta)
    while current < end:
        yield current
        current += delta

def find_historical_trends(timeseries,window="days"):
    dates,values = timeseries[0],timeseries[1]
    values = [float(vall) for vall in values]
    final_dates = list(date_range(datetime.date(2018,1,1),datetime.date(2019,1,1),{window:1}))[::-1]

    if dates[0].day != final_dates[0].day or dates[0].month != final_dates[0].month:
        for k in range(len(dates)):
            if dates[k].year != dates[0].year:
                dates = dates[k:]
                values = values[k:]
                break

    if dates[len(dates)-1].day != final_dates[len(final_dates)-1].day or dates[len(dates)-1].month != final_dates[len(final_dates)-1].month:
        for i in range(1,len(dates)):
            if dates[-i].year != dates[len(dates)-1].year:
                dates = dates[:-i+1]
                values = values[:-i+1]
                break
    yes = []
    [yes.append(f) for f in range(len(dates)) if dates[f].month == 2 and dates[f].day == 29]
    for y in yes:
        del(dates[y])
        del(values[y])

    final_values = []
    for z in range(len(final_dates)):
        temp = []
        for j in range(int((len(dates) - 1) / 365)+1):
            temp.append(values[z+365*j])
        final_values.append(temp)
    averages = []
    std = []
    for val in final_values:
        averages.append(sum(val)/len(val))
        std.append(np.std(val))
    return [final_dates[::-1],averages[::-1],std[::-1]]




# gtrend().update("aurora cannabis")
# stock_store().update("ACB")



# t = (backtester([temp[1][::-1][1:],temp[2][::-1][1:],test.values[::-1]],values[1:],"hist"))

# fig = tools.make_subplots(rows=1, cols=1,shared_xaxes=True,shared_yaxes=True)
#
# stock = goo.Scatter(x = temp[0],y = temp[1],name="average")
# stock2 = goo.Scatter(x = temp[0],y = temp[2],name="std")
# one = goo.Scatter(x = temp[0],y=[t[0][1][0] for n in range(len(temp[0]))])
# two = goo.Scatter(x = temp[0],y=[t[0][1][1] for n in range(len(temp[0]))])
# # three = goo.Scatter(x = temp[0],y=[t[0][1][2] for n in range(len(temp[0]))])
# fig.append_trace(stock,1,1)
# fig.append_trace(stock2,1,1)
# fig.append_trace(one,1,1)
# fig.append_trace(two,1,1)
# # fig.append_trace(three,1,1)
#
# plotly.offline.plot({"data": fig, "layout": goo.Layout(title="")})

def compartment2(stock,trend):
    data = load_obj("stock_data")[stock.upper()]
    temp = find_historical_trends([data.day_ts.dates,data.day_ts.volume],"days")

    dates = data.day_ts.dates
    values = data.day_ts.pv_delta
    test = load_obj("trendprods")[trend].threemonth
    for y in range(len(dates)):
        if dates[y].year != 2019:
            dates = dates[:y]
            values = values[:y]
            break
    t = backtester([temp[1][::-1][:len(dates)][::-1], temp[2][::-1][:len(dates)][::-1], test.values[:len(dates)][::-1]], values[2:], "hist")
    return temp,t


# graph(z[0],[z[1],z[2]],"dub")
# gtrend().update("debt")
st = "AAPL"
trr = "aapl"


# trend = load_obj("trendprods")[trr]
stock = load_obj("stock_data")[st]

# z = find_historical_trends([trend.threemonth.times,trend.threemonth.values])
z2 = find_historical_trends([stock.day_ts.dates,stock.day_ts.pv_delta])
# graph(z[0],[z[1],z[2]],["avg","std"])
graph(z2[0],[z2[1],z2[2]],["avg","std"])

# t = (stock.day_ts.backtester(1,averages=z[1],std=z[2],lookahead=1,timeframe="all"))
# graph(t["Progress Control"][0],[t["Progress"][1],t["Progress Control"][1]],["gainz","control"],False,"Profit:{}. {} days in total after {} days. (Stock:{}, Trend:{})".format(t["Profit"],t["Total Days"]-t["Total Days In"],t["After"],st,trr))
# print(t)
