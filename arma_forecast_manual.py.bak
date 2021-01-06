#!/sur/bin/env python
#-*- coding: utf-8 -*-

import datetime
import pandas as pd
from database.base_env_repository import getFactors,getSites
from database.dts_env_repository import getSiteData,save_daily_forecast_data
from utils import dateshift
from model import  arma,lstm

import warnings
warnings.filterwarnings("ignore")

# 用于预测的历史记录

# 用于预测最大记录数
RECORD_COUNT_MAX=60

# 用于预测最小记录数
RECORD_COUNT_MIN=12

# 预测时长
RUN_LEN = 4

def getTime(date):

    # 当天
    # date = '2017-07-15'
    TODAY = date

    # TODAY=datetime.datetime.now().strftime('%Y-%m-%d')
    #TODAY = '2015-07-31'

    # 前一天
    YESTERDAY = dateshift(TODAY,-1)

    # 数据结束日期
    END_DATETIME=YESTERDAY

    # 数据开始日期
    START_DATETIME = dateshift(END_DATETIME,-RECORD_COUNT_MAX)

    # 预测日期
    FORECAST_START_DATETIME=TODAY
    FORECAST_END_DATETIME=dateshift(TODAY,RUN_LEN-1)

    return START_DATETIME,END_DATETIME,FORECAST_START_DATETIME,FORECAST_END_DATETIME

def reindex_dataframe(df,start_time=None,end_time=None,freq='1D'):
    if start_time is None:
        start_time = df.index.min()
    if end_time is None:
        end_time = df.index.max()
   
    df = df.reindex(pd.date_range(start=start_time,end=end_time,freq=freq))
 
    return df

def check_dataset(dataset):
    if dataset is None:
        print "Data Frame is None."
        return False
    elif len(dataset) < RECORD_COUNT_MIN:
        print "Data Frame count:{0} is less than minimal required:{1}".format(len(dataset),RECORD_COUNT_MIN)
        return False
    else:
        return True 

def arma_forecast(dataset,column):
    datas = arma.forecast(dataset,delta=3,freq='D')
    if datas is None:
        return datas
    values = datas.values
    index = datas.index
    datas = datas = pd.DataFrame(data=values,index=index,columns=[column])    
    return datas

def forecast(site,factor,start_time,end_time):

    siteId=site['id']
    column=factor['column']

    df = getSiteData(siteId=siteId,factorColumn=column,start_time=start_time,end_time=end_time)

    #print df

    if check_dataset(df):
 
        df = reindex_dataframe(df,end_time = end_time)
        df = df.interpolate('linear')

        dataset = df[column]

        arma_datas = arma_forecast(dataset,column)

        return arma_datas     

    else:
        print "Data Frame Error."
        return None


 
if __name__ == '__main__':
    
    # print ("Start day:"+START_DATETIME+","+"End day:"+END_DATETIME)

    sites =getSites()
    factors=getFactors()    

    #sites=[{'id':'402882a1535f6e4c01544d90d19f002d','name':'NH4+'}]
    #factors=[{"id":"000684a34567bc1a014124c9243432cc","column":"F_311",'code':311}]
	
    BEGIN_TIME = '2017-07-14'
    
    length = 15
    for x in range(0,length):
    
        today = dateshift(BEGIN_TIME,x)

        start_time,end_time,forecast_start_time,forecast_end_time = getTime(today)
        
        print ("Start day:"+start_time+","+"End day:"+end_time)

        continue

        for site in sites:
            for factor in factors:
                    
                print "----------------------------------------------------------------"
                print "Predict Site:[{0}],Factor:{1}".format(site['id'],factor['code'])                    
                arma_datas = forecast(site,factor,start_time,end_time)
                       
                if arma_datas is not None:
		    if arma_datas.values[0] is not None:
                        save_daily_forecast_data(forecast_start_time,site['id'],arma_datas.values,factor['code'],model="ARMA")
                else:
                    print "[ARMA]: forecast site:{0},factor:{1} failed.".format(site['id'],factor['code'])
    

                print "-------------------------------------"
                print "ARMA Forecast Result :"
                print arma_datas 
