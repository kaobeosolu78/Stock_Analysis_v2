import bs4,requests
import re
import pickle
import difflib
from smain import graph
from datetime import datetime


class fundamentals:
    def __init__(self, raw_data, ticker):
        self.raw_data = raw_data
        self.ticker = ticker

    def process(self):
        prods = linearize_data(self)
        self.data = prods
        return prods

    def get_indexes(self,year="2019"):
        return list(self.raw_data[year].keys()),list(self.raw_data.keys())

    def update(self,up_ticker=None):
        if ticker:
            return get_sheets(up_ticker)
        return get_sheets(self.ticker)

    def compare(self,comp):
        fundone = []
        fundtwo = []

        print(list(self.data.keys()))
        sheet1 = input("Choose a sheet for {}: ".format(self.ticker))
        print(list(comp.data.keys()))
        sheet2 = input("Choose a sheet for {}: ".format(comp.ticker))

        minimum = min([comp.data[sheet2]],self.data[sheet1])

        print(list(self.data[sheet1][1].keys()))
        fundnameone = list(input("Choose fundamental data to compare for {}: ".format(self.ticker)))
        [fundone.append(self.data[sheet1][1][fundname][:minimum]) for fundname1 in fundnameone]
        print(list(comp.data[sheet2][1].keys()))
        fundnameone = list(input("Choose fundamental data to compare for {}: ".format(comp.ticker)))
        [fundone.append(comp.data[sheet2][1][fundname][:minimum]) for fundname2 in fundnametwo]

        print(list(comp.data[sheet1][1].keys()))

def load_obj(datatype):
    with open("{}".format(datatype) + '.pkl', 'rb') as f:
        return pickle.load(f)

def get_10k(tickers,filecodes=""):
    if type(tickers) != list:
        tickers = [tickers]
    for ticker in tickers:
        rawcik = requests.get(
            ("https://www.sec.gov/cgi-bin/browse-edgar?CIK={}&owner=exclude&action=getcompany").format(ticker))
        ciksoup = bs4.BeautifulSoup(rawcik.text, "html.parser")
        try:
            filecodes[ticker] = {"CIK":(((ciksoup.find(text="CIK").findNext("a")).text)[3:-26]),"FileCodes":""}
        except:
            tickers.remove(tick)
            continue

        filecode = {}
        raw10k = requests.get((
            "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={}&type=10-K&dateb=&owner=exclude&count=80").format(
            filecodes[ticker]["CIK"]))
        ksoup = bs4.BeautifulSoup(raw10k.text, "html.parser")

        tr = (((ksoup.find(class_="tableFile2"))).findAll("tr"))
        for k in range(len(tr)):
            if ((tr[k]).find(class_="small")) != None:
                temp = ((((tr[k]).find(class_="small")).text))
                filecode_re = re.compile(r'\d\d\d\d\d\d\d\d\d\d-\d\d-\d\d\d\d\d\d')
                rawfc = filecode_re.search(temp).group()
                if int(rawfc[11:13]) < 20:
                    filecode["20" + rawfc[11:13]] = rawfc.replace("-", "")
                else:
                    filecode["19" + rawfc[11:13]] = rawfc.replace("-","")

        filecodes[ticker]["FileCodes"] = filecode

    pick_out = open("filecodes.pkl", "wb")
    pickle.dump(filecodes, pick_out, pickle.HIGHEST_PROTOCOL)
    pick_out.close()
    return filecodes


def get_sheets(tickers,end_year=2012):
    sheets_dict = {1: "Document and Entity Information", 2: r"CONSOLIDATED STATEMENTS OF OPERATION(S)?",
              3: "CONSOLIDATED STATEMENTS OF (COMPREHENSIVE )?LOSS",
              4: "CONSOLIDATED STATEMENTS OF (COMPREHENSIVE )?INCOME", 5: "CONSOLIDATED BALANCE SHEETS",
              6: "CONSOLIDATED STATEMENTS OF \D\D\D\D\DHOLDERS' EQUITY",7:"CONSOLIDATED STATEMENTS OF CASH FLOWS"}
    print(sheets_dict)
    sheets_temp = (input("Choose sheets: ")).split(",")
    sheets=[]
    [sheets.append(sheets_dict[int(sheet)]) for sheet in sheets_temp]

    products_tick = load_obj("fundamentals")
    all_filecodes = load_obj("filecodes")
    for ticker in [tickers]:
        try:
            filecodes = all_filecodes[ticker]
        except:
            filecodes = get_10k(ticker,all_filecodes)[ticker]
        print(ticker)
        try:
            products_year = products_tick[ticker]
        except:
            products_year = {}
        tickcodes,CIK = filecodes["FileCodes"],filecodes["CIK"]
        years = list(tickcodes.keys())

        for year in years:
            sheet_index = 0
            try:
                products_sheet = products_year[year]
            except:
                products_sheet = {}
            print (year)
            count = 0
            while count < len(sheets) and sheet_index < 10:
                sheet_index += 1
                products = []
                rawincome = requests.get(
                    "https://www.sec.gov/Archives/edgar/data/{}/{}/R{}.htm".format(CIK, tickcodes[year],sheet_index))
                incomesoup = bs4.BeautifulSoup(rawincome.text, "html.parser")
                tr = (incomesoup.find(class_="report").findAll("tr"))
                document = tr[0].text.replace("\n","")
                for k in range(len(document)-1):
                    if document[k] == "-" or document[k] == "(":
                        document = document[:k-1].upper()
                        break
                check = [x for x in sheets if re.compile(x).match(document)]

                if check != []:
                    print(document)
                    count += 1
                    for t in tr:
                        products.append([x for x in t.text.split("\n") if x != "" and x != "\xa0"])
                        print([x for x in t.text.split("\n") if x != "" and x != "\xa0"])
                    products_sheet.update({check[0]:products})
            products_year.update({year:products_sheet})
            if year == str(end_year):
                break
        products_tick.update({ticker:fundamentals(products_year,ticker)})

        pick_out = open("fundamentals.pkl", "wb")
        pickle.dump(products_tick, pick_out, pickle.HIGHEST_PROTOCOL)
        pick_out.close()
    return products_tick

def linearize_data(fund_data):
    def get_labels(sheet, data, current_labels):
        try:
            current_labels[sheetind]
        except:
            current_labels[sheetind] = []
        for q in range(len(data)):
            if len(data[q]) == 4 or len(data[q]) == 3:
                current_labels[sheetind].append(data[q][0])
        return current_labels
    data = fund_data.raw_data
    sheet_index,date_index = fund_data.get_indexes()

    final_products = {}
    for sheetind in sheet_index:
        dates, products, current_labels = [], {}, {}
        current_labels = get_labels(sheetind, data[date_index[0]][sheetind], current_labels)
        label_check = current_labels[sheetind]
        for dateind in date_index:
            balance = False
            try:
                data[dateind][sheetind]
            except:
                continue
            for k in range(len(data[dateind][sheetind])):
                if k == 0 and len(data[dateind][sheetind][k]) == 3:
                    try:
                        dates.append(datetime.strptime(data[dateind][sheetind][k][1],"%b. %d, %Y"))
                        balance = True
                    except:
                        pass
                if k == 1 and balance != True:
                    if len(data[dateind][sheetind][k]) == 14:
                        if data[dateind][sheetind][k][8] not in dates:
                            dates.append(datetime.strptime(data[dateind][sheetind][k][8],"%b. %d, %Y"))
                    else:
                        if data[dateind][sheetind][k][0] not in dates:
                            dates.append(datetime.strptime(data[dateind][sheetind][k][0],"%b. %d, %Y"))
                elif k != 0:
                    try:
                        title = data[dateind][sheetind][k][0]
                        if data[dateind][sheetind][k][1] == " ":
                            continue
                    except:
                        continue
                    temp = 0
                    for check in label_check:
                        seq = difflib.SequenceMatcher(isjunk=None,a=check.replace(" (loss)",""),b=title.replace(" (loss)",""))
                        diff_score = seq.ratio()
                        if temp < diff_score and diff_score > 0.9:
                            temp = diff_score
                            temp_prod = (check.replace(" (loss)",""),data[dateind][sheetind][k][1:])
                        if diff_score == 1:
                            temp_prod = (check.replace(" (loss)",""),data[dateind][sheetind][k][1:])
                            break

                    try:
                        temp_prod[1][0]
                    except:
                        continue
                    try:
                        products[temp_prod[0]]
                    except:
                        products[temp_prod[0]] = []
                    fix_data = temp_prod[1][0].replace("-","")
                    if "(" in fix_data:
                        fix_data = "-"+fix_data
                    try:
                        fix_data = float("".join([char for char in fix_data if char in "0123456789-. "]))
                    except:
                        pass
                    if fix_data not in products[temp_prod[0]]:
                        products[temp_prod[0]].append(fix_data)
        for key in list(products.keys()):
            print(key)
            print(len(products[key]))
            products[key] = products[key][::-1]
            if len(products[key]) != len(dates):
                del products[key]
        final_products[sheetind] = [dates[::-1],products]

    print(len(dates))
    return final_products
temp = (load_obj("fundamentals")["intc"].process())
print("")
graph(list(temp["CONSOLIDATED BALANCE SHEETS"][0]),list(temp["CONSOLIDATED BALANCE SHEETS"][1].values()))
