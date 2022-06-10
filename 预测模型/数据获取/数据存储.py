import pymysql
import pandas as pd


data = pd.read_excel('weatherData.xls',header=0)

data =data.values

conn = pymysql.connect(host="localhost", user="root", password="123456", db="weather1", charset="utf8")

cursor = conn.cursor()

sql0 = "DROP TABLE IF EXISTS AQIdata;"
cursor.execute(sql0)

sql1 = "create table AQIdata(id int,collectdata varchar(50),aqi_lv varchar(50),aqi int,PM25 int,PM10 int,So2 int,No2 int,Co float,O3 int);"
cursor.execute(sql1)

for i in range(len(data)):
    a = data[i,]
    sql ='insert into AQIdata(id,collectdata,aqi_lv,aqi,PM25,PM10,So2,No2,Co,O3) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
    cursor.execute(sql,(i+1,a[0],a[1],a[2],a[4],a[5],a[6],a[7],a[8],a[9]))
    conn.commit()

cursor.close()
conn.close