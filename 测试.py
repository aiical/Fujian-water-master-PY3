# -*- coding:utf-8 -*-
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import pearsonr

dt_test = pd.read_csv(r'E:/MyFpi/corelation/section_1_day_data.csv',index_col=0)
dt_test=dt_test.dropna()

print(pearsonr(dt_test['Cond'],dt_test['P'])[0])

sns.heatmap(dt_test.corr())   #vmin=0, vmax=1
plt.show()
score=dt_test.corr()
#print(score[abs(score)>0.5])


print(round(score,3))
# file=round(score,3)
# file.to_csv('E:\MyFpi\PPT\pearsonr.csv')

import time
while True:
  time_now = time.strftime("%H:%M:%S", time.localtime()) # 刷新
  if time_now == "15:02:10": #此处设置每天定时的时间

    # 此处3行替换为需要执行的动作
    print("hello")
    subject = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + " 定时发送测试"
    print(subject)

    time.sleep(2) # 因为以秒定时，所以暂停2秒，使之不会在1秒内执行多次