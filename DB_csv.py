import pandas as pd
import DB
import datetime
import time
import os


path = os.getcwd()
now = datetime.datetime.now() + datetime.timedelta( hours=-1)
time = now.strftime("%Y-%m-%d %H")
user_size = DB.user_size()


def DB_Data_Csv_Save():
    timestamp = []
    temp = []
    humidity =[]
    gas =[]
    water = []
    volt = []

    for i in range(user_size):
        data = DB.select_data(i)
        water_data =DB.select_water(i)
        gas_data =DB.select_gas(i)
        volt_data =DB.select_volt(i)

        for j in range(len(data)):
            timestamp.append(data[j][0])
            temp.append(data[j][1])
            humidity.append(data[j][2])
            gas.append(gas_data[j][0])
            water.append(water_data[j][0])
            volt.append(volt_data[j][0])

        label = {'timestamp' :  timestamp, 'temp' : temp ,'humidity':humidity , 'gas' : gas, 'water' : water, 'volt': volt}

        dataframe = pd.DataFrame(label)
        dataframe.to_csv(f'{path}\Data\Time_Serial_Anomaly{time}_{i}.csv',index=False,header=True )

        #list clear
        timestamp.clear()
        temp.clear()
        humidity.clear()
        gas.clear()
        water.clear()
        volt.clear()
