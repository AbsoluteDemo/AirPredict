import pandas as pd
import re
import urllib.request
import urllib.error
import xlwt
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
import tensorflow as tf
import pandas as pd
from numpy import concatenate


def askURL(url):
    head ={
        "User-Agent":"Mozilla / 5.0(Windows NT 10.0;Win64; x64) AppleWebKit / 537.36(KHTML, like Gecko) Chrome / 98.0.4758.102 Safari / 537.36"
    }
    request = urllib.request.Request(url,headers=head)
    html = ""
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode("GBK")
        print(html)
    except urllib.error.URLError as e:
        if hasattr(e,"code"):
            print(e.code)
        if hasattr(e,"reason"):
            print(e.reason)
    return html


def getdata():
    url ="http://www.tianqihoubao.com/aqi/hangzhou.html" 

    datalist = []
    html = askURL(url)
    soup = BeautifulSoup(html, "html.parser")

    aqi_lv=soup.find('div',class_="status")
    aqi_lv=aqi_lv.text.replace(' ','').replace('\n','').replace('\r','')
    datalist.append(aqi_lv)
    aqi=soup.find('div',class_="num")
    aqi=aqi.text.replace(' ','').replace('\n','').replace('\r','')
    datalist.append(aqi)
    PM25=re.findall('(?<=PM2.5：).[0-9_]*',html)
    datalist.append(PM25[0])
    PM10=re.findall('(?<=PM10 ：).[0-9_]*',html)
    datalist.append(PM10[0])
    So2=re.findall('(?<=二氧化硫：).[0-9_]*',html)
    datalist.append(So2[0])
    No2=re.findall('(?<=二氧化氮：).[0-9_]*',html)
    datalist.append(No2[0])
    Co=re.findall('(?<=一氧化碳：).[0-9_]*',html)
    datalist.append(Co[0])
    O3=re.findall('(?<=臭氧：).[0-9_]*',html)
    datalist.append(O3[0])

    book = xlwt.Workbook(encoding='utf-8', style_compression=0)
    sheet = book.add_sheet("空气质量", cell_overwrite_ok=True)
    col = ("质量等级", "AQI指数", "PM2.5", "PM10", "So2", "No2", "Co", "O3")
    for i in range(0, 8):
        sheet.write(0, i, col[i])
    for j in range(0, 8):
        sheet.write(1, j, datalist[j])
    book.save(".\\Data.xls")



def predict():
    model = tf.keras.models.load_model('air_analysis.model')

    #dataset = pd.read_csv('data1.csv', header=0, index_col=0,nrows=10)
    dataset = pd.read_excel('Data.xls',header=0, index_col=0)
    # 数据预处理：
    values = dataset.values
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
    return inv_yhat


def online2():
    weather = GetWeather()
    weather.__main__()
    return 200