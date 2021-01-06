#!/sur/bin/env python
#-*- coding: utf-8 -*-


import pandas as pd

import pyodbc
import sys

reload(sys)
sys.setdefaultencoding('utf8')



cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER=172.19.3.121;PORT=1433;DATABASE=prj_fj_env;UID=sa;PWD=sa123123')
dts_cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER=172.19.3.121;PORT=1433;DATABASE=prj_fj_env_dts;UID=sa;PWD=sa123123')

cursor = cnxn.cursor()
dts_cursor=dts_cnxn.cursor()

# 1. query sites

SITES=[]

# target water area

CODE_WSYSTEM='2c938239477b7c8f01477ba676ed0002'
SQL="SELECT ID FROM WMS_WATER_SITE WHERE CODE_WSYSTEM='{0}'".format(CODE_WSYSTEM)

cursor.execute(SQL)

while 1:
    row = cursor.fetchone()
    if not row:
        break
    SITES.append(row.ID)
    print (row.ID)

print ("total count:{0}".format(len(SITES)))

# 2. get factors

FACTORS=[]

# water monitor factors

MONITOR_TYPE="WMS"
SQL="SELECT ID,COLUMNCODE,PRECISION FROM BASE_DATAITEM WHERE MONITORTYPE='{0}'".format(MONITOR_TYPE)

cursor.execute(SQL)

while 1:
    row = cursor.fetchone()
    if not row:
        break
    FACTORS.append({
        "id":row.ID,
        "code":row.COLUMNCODE,
        "column":"F_"+row.COLUMNCODE
    })

print ("total factors count:{0}").format(len(FACTORS))

# 3. get data

DATAS=[]
DATE_INDEXS=[]

# 用于预测的历史记录
RECORD_COUNT=20








for siteId in SITES:
    for factor in FACTORS:
        column=factor['column']
        sql="select top {0} {1},DATETIME from WMS_1440".format(RECORD_COUNT,column)+ \
            " WHERE NODEID='{0}' AND {1} IS NOT NULL ".format(siteId,column)+ \
            "AND DATETIME > '{0}'".format(START_DATETIME) +\
            "AND DATETIME <= '{0}' ORDER  BY DATETIME DESC".format(END_DATETIME)

        print (sql)

        dts_cursor.execute(sql)

        date=None

        # 标示数据是否成功
        flag = True

        while 1:
            row = dts_cursor.fetchone()
            if not row:
                break

            current_date = row[1].split(" ")[0]

            # current_date=datetime.datetime.strptime(row[1].split(" "),'%Y-%m-%d')

            if date is None:
                if current_date == YESTERDAY:
                    DATE_INDEXS.append(pd.Timestamp(row[1].split(" ")[0]))
                    DATAS.append(row[0])
                    date = current_date
                else:
                    print ("model date don't have data.")
                    flag=False
                    break
            elif dateshift(current_date,2) < date: # 时间不连续,数据中断，最多允许3天连续没有数据
                print ("data is not avaliable.")
                flag=False
                break
            else:
                DATE_INDEXS.append(pd.Timestamp(row[1].split(" ")[0]))
                DATAS.append(row[0])
                date = current_date
        # 由于数据可能会有缺失，因此需要对数据进行校验

        if flag == True:
            df=pd.DataFrame(data=DATAS,index=DATE_INDEXS,columns=[column])
            df.interpolate()



# query data according site id and factor id

# 4. model

# 5. save data to database


cnxn.close()
dts_cnxn.close()