import Temp_Anomaly
import Humidity_Anomaly
import DB
import Delete_old
user_size = DB.user_size()

# old file delete
Delete_old.delete_old_files()

# result Data list
temp = []
humidity = []
gas = []
water = []
volt = []
# Anomaly Detection
temp_anomaly = Temp_Anomaly.Temp()

# Data
temp.append(temp_anomaly)

for i in range(user_size) :
    DB.anomaly(i, temp[0][i], humidity[0][i], gas[0][i], water[0][i], volt[0][i])

