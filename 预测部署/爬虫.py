import pandas as pd
import re
import urllib.request
import urllib.error
from bs4 import BeautifulSoup
import xlwt
import csv





def askURL(url):
    head ={
        "User-Agent":"Mozilla / 5.0(Windows NT 10.0;Win64; x64) AppleWebKit / 537.36(KHTML, like Gecko) Chrome / 98.0.4758.102 Safari / 537.36"
    }
    request = urllib.request.Request(url,headers=head)
    html = ""
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode("GBK")
    except urllib.error.URLError as e:
        if hasattr(e,"code"):
            print(e.code)
        if hasattr(e,"reason"):
            print(e.reason)
    return html


def getData(baseurl):
    datalist = []


    html = askURL(baseurl)
    row_list = re.findall(r"<tr>(.*?)</tr>", html, re.S)
    for k in row_list[1:]:
                aqi_data = re.findall(r"<td.*?>\s*(.*?)\s*</td>", k, re.S)
                datalist.append(aqi_data)
    
    print(datalist)

    return datalist



def saveData(savepath,datalist):
    book = xlwt.Workbook(encoding='utf-8', style_compression=0)
    sheet = book.add_sheet("空气质量", cell_overwrite_ok=True)
    col = ("日期", "质量等级", "AQI指数", "当天AQI排名", "PM2.5	", "PM10", "So2", "No2", "Co", "O3")
    for i in range(0, 10):
        sheet.write(0, i, col[i])
    for i in range(0, len(datalist)):
        data = datalist[i]
        for j in range(0, 10):
            sheet.write(i + 1, j, data[j])
    book.save(savepath)
    return 0

print("start.....")
baseurl = "http://www.tianqihoubao.com/aqi/hangzhou-202201.html"
datalist = getData(baseurl)
savepath = ".\\weatherData.xls"
