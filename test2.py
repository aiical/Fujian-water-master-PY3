from keras.models import Sequential

# 3. 训练模型
import os
import pandas as pd
from sklearn.model_selection import train_test_split
import numpy as np
import tensorflow as tf

data = pd.read_csv(r'C:\Users\41634\Desktop\Drybeach\second\finaldrop-2.csv',index_col=0)
data=data.dropna()
##打乱顺序
from sklearn.utils import shuffle



Y=data.loc[:, ['label']]
X=data.iloc[:,0:27]

from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
#X=scaler.fit_transform(X) 


# batch_size=100
# n_batch=len(data)//batch_size


X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2)


from keras.layers.core import Dense, Activation, Flatten
from keras import optimizers
from keras.optimizers import rmsprop
import keras as K


SGD = optimizers.SGD(lr=0.01, clipnorm=1.)
# 2. 定义模型
init = K.initializers.glorot_uniform(seed=1)
simple_adam = K.optimizers.Adam()
model = K.models.Sequential()
model.add(K.layers.Dense(units=5, input_dim=27, kernel_initializer=init, activation='relu'))
model.add(K.layers.Dense(units=6, kernel_initializer=init, activation='relu'))
model.add(K.layers.Dense(units=1, kernel_initializer=init, activation='sigmoid'))
model.compile(loss='sparse_categorical_crossentropy', optimizer=simple_adam, metrics=['accuracy'])


b_size = 100
max_epochs = 10
print("Starting training ")
h = model.fit(X_train, Y_train, batch_size=b_size, epochs=max_epochs, verbose=1)
print("Training finished \n")

# verbose = 0，在控制台没有任何输出
# verbose = 1 ：显示进度条
# verbose =2：为每个epoch输出一行记录
eval = model.evaluate(X_test, Y_test, verbose=0)
print("Evaluation on test data: loss = %0.6f accuracy = %0.2f%% \n" \
          % (eval[0], eval[1] * 100) )
