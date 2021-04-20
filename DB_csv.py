import pandas as pd
import DB
import datetime
import time
import os
from IPython.display import display


path = os.getcwd()
now = datetime.datetime.now() + datetime.timedelta( hours=-1)
time = now.strftime("%Y-%m-%d %H")
user_size = DB.user_size()


def DB_Data_Csv_Save():
    timestamp = []
    temp = []
    humidity =[]

    for i in range(user_size):
        data = DB.select_data(i)
        for j in range(len(data)):
            timestamp.append(data[j][0])
            temp.append(data[j][1])
            humidity.append(data[j][2])

        label = {'timestamp' :  timestamp, 'temp' : temp ,'humidity':humidity }

        dataframe = pd.DataFrame(label)
        dataframe.to_csv(f'{path}\Data\Time_Serial_Anomaly{time}_{i}.csv',index=False,header=True )

        #list clear
        timestamp.clear()
        temp.clear()
        humidity.clear()
