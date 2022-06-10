from sklearn.preprocessing import LabelEncoder, MinMaxScaler
import tensorflow as tf
import pandas as pd
from numpy import concatenate


model = tf.keras.models.load_model('air_analysis.model')

#dataset = pd.read_csv('data1.csv', header=0, index_col=0,nrows=10)
dataset = pd.read_excel('Data.xls', header=0,index_col=0)
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

print(inv_yhat)
