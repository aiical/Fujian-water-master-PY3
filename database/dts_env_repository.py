#!/sur/bin/env python
#-*- coding: utf-8 -*-

import pandas as pd
import uuid
from .connection import getDtsConnection

connection = getDtsConnection()

DAILY_TABLE="WMS_1440"
MONTH_TABLE="WMS_MONTH"

DAILY_FORECAST_TABLE='T_DAILY_FORECAST_RESULT'
MONTH_FORECAST_TABLE='T_MONTH_FORECAST_RESULT'
# get site data according to site id and factor code.
# this method return dataframe of pandas type.

def getUUID(name):
    print("name: {0},length:{1}".format(name,len(name)))
    name = name.encode('utf-8')
 
    id=uuid.uuid5(namespace=uuid.NAMESPACE_DNS,name=name)

    id=str(id).replace('-','')
    return id


def getSiteData(siteId=None,factorCode=None,factorColumn=None,start_time=None,end_time=None,type=None):

    column = factorColumn

    if column is None and factorCode is not None:
        column = "F_"+str(factorCode)

    if column is None:
        print("get site data error: factor code or factor column must specified.")
        return None

    cursor = connection.cursor()

    time_index=[]
    datas=[]
    table = DAILY_TABLE
    if type == 'month':
        table = MONTH_TABLE
    sql="select {0},DATETIME from {1}".format(column,table)+ \
            " WHERE NODEID='{0}' AND {1} IS NOT NULL ".format(siteId,column)+ \
            "AND DATETIME > '{0}'".format(start_time) +\
            "AND DATETIME <= '{0}' ORDER  BY DATETIME DESC".format(end_time)

    cursor.execute(sql)
    
    while 1:
        row = cursor.fetchone()
        if not row:
            break
        time_index.append(pd.Timestamp(row[1].split(" ")[0]))
        datas.append(row[0])
    
    df=pd.DataFrame(data=datas,index=time_index,columns=[column])
    cursor.close()
    
    return df

# 站点id,因子编码,预测数据集,预测模型
# 预测第一天为当天,即为预测日期

# 代码重复,后续优化

def check_month_forecast_data(id):
    if id is not None:
        sql = "select ID from {0} where ID = '{1}'".format(MONTH_FORECAST_TABLE,str(id))
        cursor = connection.cursor()
        cursor.execute(sql)
        row = cursor.fetchone()
        if not row:
            return False
        else:
            return True
    else:
        return False

def check_daily_forecast_data(id):

    if id is not None:
        sql = "select ID from {0} where ID = '{1}'".format(DAILY_FORECAST_TABLE,str(id))
        cursor = connection.cursor()
        cursor.execute(sql)
        row = cursor.fetchone()
        if not row:
            return False
        else:
            return True
    else:
        return False

def save_month_forecast_data(forecast_date,siteId,dataset,dataCode,model):
    
    month1=dataset[0][0]
    month2=dataset[1][0]
    month3=dataset[2][0]
    month4=dataset[3][0]
    month5=dataset[4][0]
    month6=dataset[5][0]
    
    id = getUUID(str(forecast_date).replace('-','')+model+siteId+str(dataCode)+"month")
    cursor = connection.cursor() 
    if check_month_forecast_data(id) == True:
        print("Update record : site:{0},model:{1},factor:{2}".format(siteId,model,dataCode))
        sql = "UPDATE {0} SET Month1={1},Month2={2},Month3={3},".format(MONTH_FORECAST_TABLE,month1,month2,month3) + \
              "Month4={0},Month5={1},Month6={2}".format(month4,month5,month6)+ \
              " WHERE ID ='{0}'".format(id)
        print(sql)
        try:
            cursor.execute(sql)
        except Exception as e:
            print("update record error.")
    else:
        print("Insert record : site:{0},model:{1},factor:{2}".format(siteId,model,dataCode))
        sql = 'INSERT INTO {0} '.format(MONTH_FORECAST_TABLE) + \
              " (ID,ForecastDate,type,DataItemCode,NodeId,Month1,Month2,Month3,Month4,Month5,Month6)" + \
              " VALUES ('{0}','{1}','{2}','{3}','{4}'".format(id,forecast_date,model,dataCode,siteId) + \
              " ,{0},{1},{2},{3},{4},{5})".format(month1,month2,month3,month4,month5,month6)
        print(sql)

        cursor.execute(sql)

    connection.commit()

def save_daily_forecast_data(forecast_date,siteId,dataset,dataCode,model):

    first_day = dataset[1][0]                   #dataset[1]是什么  [1][0]是什么
    second_day = dataset[2][0]
    third_day = dataset[3][0]
    print(("{0},{1},{2}".format(first_day,second_day,third_day)))
    
    name = "{0}{1}{2}{3}daily".format(forecast_date,model,siteId,dataCode);
   
    print("uuid name : {0}".format(name))
    id = getUUID(name)    
    
    cursor = connection.cursor()
    
    if check_daily_forecast_data(id) == True:
        # record exsit.
        # update record.
        print("Update record : site:{0},model:{1},factor:{2}".format(siteId,model,dataCode))

        sql="UPDATE {0} SET FirstDay={1},SecondDay={2},ThirdDay={3} WHERE ID = '{4}'".format(DAILY_FORECAST_TABLE,first_day,second_day,third_day,id)
        print(sql)
        try:
            cursor.execute(sql)
        except Exception as e:
            print("update record error.")
    else:
        # insert new record.
        print("Insert record : site:{0},model:{1},factor:{2}".format(siteId,model,dataCode))
        sql="INSERT INTO {0} ".format(DAILY_FORECAST_TABLE)+ \
            "(ID,ForecastDate,FirstDay,SecondDay,ThirdDay,type,DataItemCode,NodeId)" + \
            " values ('{0}','{1}',{2},{3},{4},'{5}','{6}','{7}')".format(id,forecast_date,first_day,second_day,third_day,model,dataCode,siteId)
        print(sql)

        cursor.execute(sql)   
     
    connection.commit()
    
if __name__=='__main__':

    siteId='aa9384a34124bc1a014124c924340002'
    column='F_301'

    START_DATETIME='2015-11-01'
    END_DATETIME='2016-12-01'

    df=getSiteData(siteId=siteId,factorColumn=column,start_time=START_DATETIME,end_time=END_DATETIME,type="month")
    print("Original DataFrame:")
    print("data frame length:{0}".format(len(df)))
    print(df)
    if len(df) < 1:
        exit()
    print("----------------------------------------")
    print("dataframe after reindex.")
    df = df.reindex(pd.date_range(start=df.index.min(),end=END_DATETIME,freq='MS'))
    print(df)
    print("----------------------------------------")
    print("dataframe after interpolate.")
    df = df.interpolate('linear')
    print(df) 
