from sklearn.preprocessing import LabelEncoder, MinMaxScaler
import tensorflow as tf
import pandas as pd
from numpy import concatenate
import matplotlib.pyplot as pyplot
import pandas as pd
from sklearn.preprocessing import LabelEncoder, MinMaxScaler

import matplotlib.pyplot as pyplot
from numpy import concatenate
from math import sqrt
model = tf.keras.models.load_model('air_analysis.model')

dataset =pd.read_excel('202201.xls',header=0,index_col=0)
dataset = dataset.drop(['质量等级','当天AQI排名'],axis=1)
#dataset = pd.read_excel('t.xlsx',header=0, index_col=0)
# 数据预处理：
values = dataset.values
# ensure all data is float
values = values.astype('float32')
print(values)
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

inv_y = scaler.inverse_transform(test_X)


pyplot.plot(inv_y[:,0], label='true')
pyplot.plot(inv_yhat, label='predict')
# 显示图例：
pyplot.legend()
pyplot.show()
