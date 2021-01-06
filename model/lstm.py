#!/usr/bin/env python
# -*- coding:utf-8 -*-

import pandas
import numpy
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from sklearn.preprocessing import MinMaxScaler,StandardScaler
import time

# look_back >= look_after
look_back = 4   

look_after = 1


scaler = StandardScaler()


#scaler = MinMaxScaler(feature_range=(0, 1))


def process_data(dataset): 
    #data = dataset.resample('D').fillna(method='ffill')
    data=dataset.dropna()
    dataset = data.astype('float32')
    #dataset = numpy.reshape(dataset, (dataset.shape[0], 1))        ###把数据转成 n行1列
    dataset=numpy.array(dataset)
    dataset = dataset.reshape(-1, 1)
    dataset = scaler.fit_transform(dataset)
    return dataset


# create data set which used for trainning and testing.
def create_dataset(dataset, look_back=1, look_after=1):                       ###train_split_traing test
    dataX, dataY = [], []
    for i in range(len(dataset) - look_back):
        x = dataset[i:(i+look_back), 0]
        y = dataset[(i+look_back):(i+ look_after+look_back), 0]                   
        dataX.append(x)
        dataY.append(y)
    return numpy.array(dataX), numpy.array(dataY)



def get_train_set(dataset, scale=1):
    train_size = int(len(dataset) * scale)
    train = dataset[0:train_size, :]
    trainX, trainY = create_dataset(train, look_back, look_after)
    trainX = numpy.reshape(trainX, (trainX.shape[0], 1, trainX.shape[1]))     ## ？？
    return trainX, trainY


def train(trainX, trainY, input_dim=1, output_dim=1, epoch=10):   #epoch=100  这里的epoch决定
    # put all data training model
    model = Sequential()
    model.add(LSTM(4, input_dim=input_dim))
    model.add(Dense(output_dim))
    model.compile(loss='mse', optimizer='rmsprop')                #(loss="mean_squared_error", optimizer="adam")
    model.fit(trainX, trainY, nb_epoch=epoch, batch_size=1, verbose=1)
    return model



def get_forecast_input(trainx, trainy):
    # trainx [[[1,2,3]],[[4,5,6]]]
    # trainy [[1,2,3],[4,5,6]]
    trainx = trainx[trainx.shape[0] - 1][trainx.shape[1] - 1]
    trainy = trainy[trainy.shape[0] - 1]
    input = []

    for i in range(look_after, look_back):
        input.append(trainx[i])
    for i in range(look_after):
        input.append(trainy[i])
    input = numpy.reshape(input, (1, 1, look_back))

    return input


def forecast(data, type='daily'):
    data = process_data(data)
    trainx, trainy = get_train_set(data)
    model = train(trainx, trainy, input_dim=look_back, output_dim=look_after, epoch=20)    #epoch=200
            #train(trainX, trainY, input_dim=1, output_dim=1, epoch=100):
    forecast_result = []

    first_day_input = get_forecast_input(trainx, trainy)
    print('first day input ', first_day_input)
    first_day_forecast = model.predict(first_day_input)
    print('first_day_forecast  ', first_day_forecast )
#The prediction value of the next day 
#depends on the day before and it's prediction
    second_day_input = get_forecast_input(first_day_input, first_day_forecast)
    print('second_day_input ', second_day_input)
    second_day_forecast = model.predict(second_day_input)
    print('second_day_forecast  ', second_day_forecast )
    third_day_input = get_forecast_input(second_day_input, second_day_forecast)
    third_day_forecast = model.predict(third_day_input)

    fouth_day_input = get_forecast_input(third_day_input, third_day_forecast)
    fouth_day_forecast = model.predict(fouth_day_input)

    if type == 'month':
        five_day_input = get_forecast_input(fouth_day_input, fouth_day_forecast)
        five_day_forecast = model.predict(five_day_input)

        six_day_input = get_forecast_input(five_day_input, five_day_forecast)
        six_day_forecast = model.predict(six_day_input)

        seven_day_input = get_forecast_input(six_day_input, six_day_forecast)
        seven_day_forecast = model.predict(seven_day_input)

    first_day_forecast = scaler.inverse_transform(first_day_forecast)
    second_day_forecast = scaler.inverse_transform(second_day_forecast)
    third_day_forecast = scaler.inverse_transform(third_day_forecast)
    fouth_day_forecast = scaler.inverse_transform(fouth_day_forecast)

    if type == 'month':
        five_day_forecast = scaler.inverse_transform(five_day_forecast)
        six_day_forecast = scaler.inverse_transform(six_day_forecast)
        seven_day_forecast = scaler.inverse_transform(seven_day_forecast)

    forecast_result.append(first_day_forecast)
    forecast_result.append(second_day_forecast)
    forecast_result.append(third_day_forecast)
    forecast_result.append(fouth_day_forecast)

    if type == 'month':
        forecast_result.append(five_day_forecast)
        forecast_result.append(six_day_forecast)
        forecast_result.append(seven_day_forecast)

    forecast_result = numpy.array(forecast_result)
    print(forecast_result.shape)
    count = 4

    if type == 'month':
        count = 7
    forecast_result = numpy.reshape(forecast_result, count)
    print('forecast_result.shape',forecast_result.shape)
    return forecast_result


# # create data set which used for trainning and testing.
# def create_dataset(dataset, look_back=1, look_after=1):                       ###train_split_traing test
#     dataX, dataY = [], []
#     for i in range(len(dataset) - look_back):
#         x = dataset[i:i + look_back, 0]
#         y = dataset[i + look_back:i + look_after + look_back, 0]
#         dataX.append(x)
#         dataY.append(y)
#     return numpy.array(dataX), numpy.array(dataY)


if __name__ == '__main__':
    section = "1"
    factor = 'DO'
    start=time.time()
    # fix random seed for reproducibility
    numpy.random.seed(0)

    dateparse = lambda dates: pandas.datetime.strptime(dates, '%m/%d/%Y')
    # # plot data set
    # dataframe = pandas.read_csv('./Data/section_' + section + '_day_data.csv',
    #                             parse_dates=['date'], index_col='date', date_parser=dateparse)
    dataframe = pandas.read_csv('E:/MyFpi/Project1/fushan/Data/section_' + section + '_day_data.csv',
                                parse_dates=['date'], index_col='date', date_parser=dateparse)
    data = dataframe[factor]
    data = data['2015-01-01':'2015-02-28'].interpolate()
    result = forecast(data)
    print(result)
    end=time.time()
    time_consuming=end-start
    print('time_consuming: %.3f'%time_consuming)
