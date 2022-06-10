import pandas as pd
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import explained_variance_score
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Dropout
import matplotlib.pyplot as pyplot
from numpy import concatenate
from math import sqrt


# 给定输入、输出序列的长度，它可以自动地将时间序列数据转型为适用于监督学习的数据
def series_to_supervised(data, n_in=3, n_out=1, dropnan=True):
    # n_vars为列数
    n_vars = 1 if type(data) is list else data.shape[1]
    df = pd.DataFrame(data)
    cols, names = list(), list()
    for i in range(n_in, 0, -1):
        cols.append(df.shift(i))
        names += [('var%d(t-%d)' % (j + 1, i)) for j in range(n_vars)]
    for i in range(0, n_out):
        cols.append(df.shift(-i))
        if i == 0:
            names += [('var%d(t)' % (j + 1)) for j in range(n_vars)]
        else:
            names += [('var%d(t+%d)' % (j + 1, i)) for j in range(n_vars)]
    # put it all together
    agg = pd.concat(cols, axis=1)
    agg.columns = names
    # drop rows with NaN values
    if dropnan:
        agg.dropna(inplace=True)
    # 它的返回值只有一个, 即转型后适用于监督学习的DataFrame
    return agg


# load dataset
dataset = pd.read_csv('data1.csv', header=0, index_col=0)
values = dataset.values
# ensure all data is float
values = values.astype('float32')
# 数据归一化：此时已经去掉时间值，第一列为污染指数PM2.5:
scaler = MinMaxScaler(feature_range=(0, 1))
scaled = scaler.fit_transform(values)
# 将数据规整成为可以放进神经网络的dataframe。
reframed = series_to_supervised(scaled, 1, 1)
# drop columns we don't want to predict
# reframed一共有16列，去除10——16列：经过这一变化，
# 数据集的最后一行表示下一刻空气的污染程度。第一行表示这一刻空气的污染程度
# 模型通过对前八行的数据，即这一刻的数据，预测第九行，即下一刻的污染程度。
reframed.drop(reframed.columns[[8,9,10,11,12,13]], axis=1, inplace=True)
# 整理好所需要的数据：


values = reframed.values
n_train_date = 365*6
train = values[:n_train_date, :]
test = values[n_train_date:, :]
print(train)
print(test)
# 取所有行，区分最后一列：[:, :-1]：不取最后一列；[:, -1]获取最后一列
# 经过上面的处理之后形成了新的数列，然后整理出y值
# X是前8行，Y是第9行。
train_X, train_y = train[:, :-1], train[:, -1]
test_X, test_y = test[:, :-1], test[:, -1]
# reshape input to be 3D [samples, timesteps, features]
train_X = train_X.reshape((train_X.shape[0], 1, train_X.shape[1]))
test_X = test_X.reshape((test_X.shape[0], 1, test_X.shape[1]))



model  = Sequential()
model.add(LSTM(128, return_sequences=True,input_shape=(train_X.shape[1], train_X.shape[2])))
model.add(Dropout(0.3))
model.add(LSTM(64,return_sequences=True))
model.add(Dropout(0.3))
model.add(LSTM(32))
model.add(Dense(1))
model.compile(loss='mae', optimizer='adam')
# fit network
history = model.fit(train_X, train_y, epochs=1000, batch_size=256, validation_data=(test_X, test_y),
                    verbose=2, shuffle=False)
model.save('predict.model')
# plot history
pyplot.plot(history.history['loss'], label='train')
pyplot.plot(history.history['val_loss'], label='test')
# 显示图例：
pyplot.legend()
pyplot.show()

# 测试
# 1、测试集是处理之后的数据：新的数据在输入模型之前需要进行一系列同上的操作，
# 所以需要实现数据的预处理模型，将其整理为一个对应的方法。
# 2、将整理好的数据放入模型中处理：
y = model.predict(test_X)
test_X = test_X.reshape((test_X.shape[0], test_X.shape[2]))
print(test_X)
# invert scaling for forecast concatenate：数据拼接
inv_yhat = concatenate((y, test_X[:, 1:]), axis=1)
print(inv_yhat)
# 3、是将标准化后的数据转换为原始数据：
inv_yhat = scaler.inverse_transform(inv_yhat)
inv_yhat = inv_yhat[:,0]


inv_y = scaler.inverse_transform(test_X)
inv_y = inv_y[:,0]


mse = mean_squared_error(inv_y,inv_yhat)
rmse = sqrt(mse)
mae = mean_absolute_error(inv_y,inv_yhat)
R2 = r2_score(inv_y,inv_yhat)
ex = explained_variance_score(inv_y,inv_yhat)
print('Test MSE: %.3f' % mse)
print('Test RMSE: %.3f' % rmse)
print('Test MAE: %.3f' % mae)
print('Test R2: %.3f' % R2)
print('Test EX: %.3f' % ex)