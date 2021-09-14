import pandas as pd
import DB
import datetime
import time
import os


path = os.getcwd()
now = datetime.datetime.now() + datetime.timedelta(hours=-1)
time = now.strftime("%Y-%m-%d %H")
user_size = DB.user_size()


def DB_Data_Csv_Save():
    timestamp = []
    temp = []
    humidity =[]
    gas = []
    water = []
    for i in range(user_size):
        data = DB.select_data(i)
        for j in range(len(data)):
            timestamp.append(data[j][0])
            temp.append(data[j][1])
            humidity.append(data[j][2])
            gas.append(data[j][3])
            water.append(data[j][4])

        label = {'timestamp': timestamp, 'temp': temp, 'humidity': humidity, 'carbon_monoxide': gas, 'wateruse': water}

        dataframe = pd.DataFrame(label)
        dataframe.to_csv(f'{path}\Data\Time_Serial_Anomaly{time}_{i}.csv', index=False, header=True)
        #list clear
        timestamp.clear()
        temp.clear()
        humidity.clear()

DB_Data_Csv_Save()