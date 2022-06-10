import xlrd
import pandas as pd

df = pd.read_excel('weatherData.xls')

df = df.dropna(how='all')

df = df.drop(['质量等级','当天AQI排名'],axis=1)

df.to_csv("data1.csv",encoding="utf_8_sig",index=0)
df.to_csv("data.csv",encoding="utf_8_sig",header=0,index=0)

df = df.drop(['日期'],axis=1)

df.to_csv("data2.csv",encoding="utf_8_sig",index=0)