import json
import csv
import numpy as np
from pprint import pprint
import datetime

def formatdate(s, n):
    s = datetime.datetime.strptime(s, "%Y/%m/%d")
    s += datetime.timedelta(days=n)
    return s.strftime("%Y/%m/%d")

# @param: csv.getvalue()したやつ
# @return: 
def csv2json(csv_s, date):
    data = []
    reader = csv.reader(csv_s.strip().splitlines())
    for row in reader:
        data.append(row)

    data = np.array(data)
    data = data.T.tolist()

    # morning: 0~10
    # lunch: 11~18
    # dinner: 19~28

    ranges = [(0, 10), (11, 18), (19, 28)]
    menu = []
    for row in data:
        # 各範囲ごとに配列を取得して追加
        split_row = [row[start:end + 1] for start, end in ranges]
        menu.append(split_row)

    item_doc = {0:"morning", 1:"lunch", 2:"dinner"}
    # variation = ["[  全部  ]", "[  Ａ  ]", "[  Ｂ  ]"]
    objjson = {}
    objjson["start"] = date[0]
    objjson["end"] = date[1]
    objjson["menu"] = []
    for day in range(len(menu)):
        dayobj = {}
        dayobj["isNone"] = False
        item = {
            "morning": {},
            "lunch": {},
            "dinner": {}
        }
        for meal in range(len(menu[day])):
            item[item_doc[meal]]["common"] = []
            item[item_doc[meal]]["A"] = []
            item[item_doc[meal]]["B"] = []
            switch = "common"
            isnone = False
            for rice in range(len(menu[day][meal])):
                i = menu[day][meal][rice]
                if isnone:
                    break
                elif i == "[  Ａ  ]":
                    switch = "A"
                    continue
                elif i == "[  Ｂ  ]":
                    switch = "B"
                    continue
                elif i == "[  全部  ]":
                    switch = "common"
                    continue
                elif i == "":
                    break
                elif "休" in i:
                    dayobj["isNone"] = True
                    isnone = True

                item[item_doc[meal]][switch].append(i)

        dayobj["item"] = item
        dayobj["date"] = formatdate(date[0], day)
        dayobj["week"] = day
        objjson["menu"].append(dayobj)
        # objjson["menu"].append(item)

    # with open("kondate.json", "w", encoding="utf-8") as f:
    #     json.dump(objjson, f,indent=4, ensure_ascii=False)

    s = json.dumps(objjson)

    return s 