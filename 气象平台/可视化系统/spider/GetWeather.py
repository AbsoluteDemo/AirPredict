import json
import requests
import xlwt
import datetime
import os
import time
from utils import dbUtil
import pandas as pd
import re
import urllib.request
import urllib.error
from bs4 import BeautifulSoup
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
import tensorflow as tf
from numpy import concatenate
import pymysql

class GetWeather:



    def __init__(self):
        self.baseUrl = r"http://d1.weather.com.cn/sk_2d/"
        self.headers = {'Accept': "*/*",
                        'Accept-Encoding': 'gzip, deflate',
                        'Accept-Language': 'keep-alive',
                        'Connection': '',
                        'Cookie': 'f_city=北京|101010100|; Hm_lvt_080dabacb001ad3dc8b9b9049b36d43b=1637305568,1637734650,1639644011,1639710627; Hm_lpvt_080dabacb001ad3dc8b9b9049b36d43b=1639723697'.encode(
                            "utf-8").decode("latin1"),
                        'Host': 'd1.weather.com.cn',
                        'Referer': 'http://www.weather.com.cn/',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36', }
        self.loadList = []
        self.cityList = []  # 格式为：列表里面的子列表都是一个省份的所有城市，子列表里所有元素都是字典，每个字典有两项
        self.cityDict = {}
        self.result = xlwt.Workbook(encoding='utf-8', style_compression=0)
        self.sheet = self.result.add_sheet('result', cell_overwrite_ok=True)
        self.cityRow = 0
        self.totalGet = 0

        current_path = os.path.dirname(__file__)
        with open(current_path + "/CITY.txt", 'r', encoding='UTF-8') as load_f:
            loadList = json.load(load_f)  # 34个省份
            for i in range(0, 4):
                self.cityList.append(loadList[i])
            for i in range(4, 34):
                for j in loadList[i]['cityList']:
                    self.cityList.append(j)
            for i in self.cityList:
                if 'districtList' in i.keys():
                    self.cityDict.setdefault(i['cityName'], i['cityId'] + "01")  # 省
                else:
                    self.cityDict.setdefault(i['provinceName'], i['id'] + "0100")  # 直辖市
        print(len(self.cityDict))

    def __getWeatherInfo__(self):
        db = dbUtil()
        count = 0
        for city, id in self.cityDict.items():
            try:
                self.totalGet = self.totalGet + 1
                self.sheet.write(self.cityRow, 0, city)  # 写当前城市名
                PageUrl = self.baseUrl + id + ".html?_" + str(int(time.time() * 1000))
                response = requests.get(PageUrl, headers=self.headers, allow_redirects=False)
                response.encoding = "utf-8"
                self.htmlResult = response.text
                data = json.loads(self.htmlResult.replace("var dataSK=", ""))
                nameen = data["nameen"]  # 城市拼音
                cityname = data["cityname"]  # 城市名称
                temp = data["temp"]  # 当前温度
                WD = data["WD"]  # 风向
                WS = data["WS"].replace("级", "")  # 风力
                wse = data["wse"].replace("km/h", "")  # 风速
                sd = data["sd"].replace("%", "")  # 湿度
                weather = data["weather"]  # 天气
                record_date = data["date"]  # 时间
                record_time = data["time"]  # 时分
                aqi = data["aqi"]  # 时分
                judge_sql = "select count(id) from `weather` where nameen = '" + nameen + "' and cityname='" + cityname + "' and record_date='" + record_date + "' and record_time='" + record_time + "'";
                sql = "INSERT INTO `weather` VALUES (null, '" + nameen + "', '" + cityname + "', '" + record_date + "', '" + record_time + "', " + str(
                    temp) + ", '" + WD + "', " + WS + ", " + wse + ", " + sd + ", '" + weather + "', " + aqi + ", '" + time.strftime(
                    "%Y-%m-%d %H:%M:%S", time.localtime()) + "',0);"
                i = db.query_noargs(judge_sql)[0][0]
                if int(i) > 0:
                    print("跳过：", judge_sql)
                    continue
                update_sql = "update `weather` set is_old=1 where nameen = '" + nameen + "' and cityname='" + cityname + "'";
                print("插入：", sql)
                count += 1
                db.query_noargs(update_sql)
                db.query_noargs(sql)
            except Exception as e:
                print(e)
                continue
        t = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sql = "insert into slog VALUES (NULL, \"【爬虫启动】爬取数据全国天气数据运行成功,获取数据：" + str(count) + "条\",\"" + t + "\")"
        db.query_noargs(sql)
        db.close_commit()

    def __main__(self):

        conn = pymysql.connect(host="localhost", user="root", password="123456", db="weather1", charset="utf8")

        cursor = conn.cursor()


        sql0 = "DROP TABLE IF EXISTS hangzhouAQIdata;"
        cursor.execute(sql0)

        sql1 = "create table hangzhouAQIdata(id int,name varchar(50),data float);"
        cursor.execute(sql1)



        url = "http://www.tianqihoubao.com/aqi/hangzhou.html"
        head = {
            "User-Agent": "Mozilla / 5.0(Windows NT 10.0;Win64; x64) AppleWebKit / 537.36(KHTML, like Gecko) Chrome / 98.0.4758.102 Safari / 537.36"
        }
        datalist = []
        request = urllib.request.Request(url, headers=head)
        html = ""
        try:
                response = urllib.request.urlopen(request)
                html = response.read().decode("GBK")
        except urllib.error.URLError as e:
                if hasattr(e, "code"):
                    print(e.code)
                if hasattr(e, "reason"):
                    print(e.reason)

        soup = BeautifulSoup(html, "html.parser")

        aqi_lv = soup.find('div', class_="status")
        aqi_lv = aqi_lv.text.replace(' ', '').replace('\n', '').replace('\r', '')
        datalist.append(aqi_lv)
        aqi = soup.find('div', class_="num")
        aqi = aqi.text.replace(' ', '').replace('\n', '').replace('\r', '')
        datalist.append(aqi)
        PM25 = re.findall('(?<=PM2.5：).[0-9_]*', html)
        datalist.append(PM25[0])
        PM10 = re.findall('(?<=PM10 ：).[0-9_]*', html)
        datalist.append(PM10[0])
        So2 = re.findall('(?<=二氧化硫：).[0-9_]*', html)
        datalist.append(So2[0])
        No2 = re.findall('(?<=二氧化氮：).[0-9_]*', html)
        datalist.append(No2[0])
        Co = re.findall('(?<=一氧化碳：).[0-9_]*', html)
        datalist.append(Co[0])
        O3 = re.findall('(?<=臭氧：).[0-9_]*', html)
        datalist.append(O3[0])





        book = xlwt.Workbook(encoding='utf-8', style_compression=0)
        sheet = book.add_sheet("空气质量", cell_overwrite_ok=True)
        col = ("质量等级", "AQI指数", "PM2.5", "PM10", "So2", "No2", "Co", "O3")
        for i in range(0, 8):
            sheet.write(0, i, col[i])
        for j in range(0, 8):
            sheet.write(1, j, datalist[j])
        book.save(".\\Data.xls")



        dataset = pd.read_excel('Data.xls', header=0, index_col=0)

        values = dataset.values

        model = tf.keras.models.load_model('air_analysis.model')

        # dataset = pd.read_csv('data1.csv', header=0, index_col=0,nrows=10)

        # 数据预处理：

        # ensure all data is float
        values = values.astype('float32')
        # 数据归一化：此时已经去掉时间值，第一列为污染指数PM2.5:
        scaler = MinMaxScaler(feature_range=(0, 1))
        values = scaler.fit_transform(values)
        train_X = values.reshape((values.shape[0], 1, values.shape[1]))
        # 数据预测：
        yhat = model.predict(train_X)
        # 数据还原：
        test_X = train_X.reshape((train_X.shape[0], train_X.shape[2]))
        # invert scaling for forecast concatenate：数据拼接
        inv_yhat = concatenate((yhat, test_X[:, 1:]), axis=1)
        # 3、是将标准化后的数据转换为原始数据：
        inv_yhat = scaler.inverse_transform(inv_yhat)
        inv_yhat = inv_yhat[:, 0]


        datalist.append(int(inv_yhat))


        name = ["aqi", "PM2.5", "PM10", "So2", "No2", "Co", "O3", "futheraqi"]



        for i in range(8):
            sql = 'insert into hangzhouAQIdata(id,name,data) values (%s,%s,%s)'
            cursor.execute(sql, (i + 1, name[i], datalist[i+1]))





        conn.commit()
        cursor.close()
        conn.close
        print(datetime.datetime.now())
        self.__getWeatherInfo__()
        print(datetime.datetime.now())


# 后台调用爬虫
def online():
    weather = GetWeather()
    weather.__main__()
    return 200
