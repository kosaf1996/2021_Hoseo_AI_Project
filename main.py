import Temp_Anomaly
import Humidity_Anomaly
import DB
user_size = DB.user_size()


#result Data list
temp = []
humidity = []

#Anomaly Detection
temp_anomaly = Temp_Anomaly.Temp()
humidity_anomaly = Humidity_Anomaly.Humidity()

#Data
temp.append(temp_anomaly)
humidity.append(humidity_anomaly)

for i in range(user_size) :
    DB.anomaly(i,temp[0][i],humidity[0][i])