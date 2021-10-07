import pymysql as db
import datetime


now = datetime.datetime.now()+ datetime.timedelta(hours=-1)
time = now.strftime("%Y-%m-%d %H")


def getConnection():
    con = db.connect ()
    return con

def user_size():
    conn = getConnection()
    cursor = conn.cursor()
    sql = "SELECT count(*) FROM raspi_db.User"
    cursor.execute(sql)
    user = cursor.fetchone()
    user_result = user[0]
    return user_result


def select_data(uscd):
    conn = getConnection()
    cursor = conn.cursor()

    #sql = f"select temp from raspi_db.collect_data_dht11 where uscd=0 and timestamp =DATE_ADD(NOW(), INTERVAL -1 SECOND)"
    sql = f"select timestamp,temp,humidity from raspi_db.collect_data_dht11 where uscd={uscd} and timestamp BETWEEN '{time}:00:00' AND '{time}:59:59'"
    cursor.execute(sql)
    temp = cursor.fetchall()

    return temp


def select_gas(uscd):
    conn = getConnection()
    cursor = conn.cursor()


    sql = f"select carbon_monoxide from raspi_db.collect_data_gsms61_p110 where uscd={uscd} and timestamp BETWEEN '{time}:00:00' AND '{time}:59:59'"
    cursor.execute(sql)
    gas = cursor.fetchall()

    return gas


def select_water(uscd):
    conn = getConnection()
    cursor = conn.cursor()

    sql = f"select wateruse from raspi_db.collect_data_yf_s201 where uscd={uscd} and timestamp BETWEEN '{time}:00:00' AND '{time}:59:59'"
    cursor.execute(sql)
    water = cursor.fetchall()

    return water

def select_volt(uscd):
    conn = getConnection()
    cursor = conn.cursor()

    sql = f"select voltage from raspi_db.collect_data_acs712 where uscd={uscd} and timestamp BETWEEN '{time}:00:00' AND '{time}:59:59'"
    cursor.execute(sql)
    volt = cursor.fetchall()
    return volt


def anomaly(uscd, temp, humidity,gas,water,volt):
    conn = getConnection()
    cursor = conn.cursor()
    sql = f"SELECT * FROM raspi_db.Anomaly where uscd = {uscd}"
    cursor.execute(sql)
    existence = cursor.fetchall()

    if len(existence) == 0 :
        sql1 = f"INSERT INTO `raspi_db`.`Anomaly`(`uscd`,`temp`,`humidity`,`wateruse`,`carbon_monoxide`,`voltage` ) VALUES ('{uscd}','{temp}','{humidity}','{water}','{gas}','{volt}')"
        cursor.execute(sql1)
        conn.commit()

    elif len(existence) == 1 :
        sql2 =f"UPDATE raspi_db.Anomaly SET `temp` ={temp},`humidity` ={humidity},`wateruse` ={water},`carbon_monoxide` ={gas},`voltage` ={volt} WHERE uscd = {uscd};"
        cursor.execute(sql2)
        conn.commit()

def anomaly_score(uscd, temp, humidity, gas, water, volt, time):
    conn = getConnection()
    cursor = conn.cursor()
    sql = f"SELECT * FROM raspi_db.Anomaly_Score where time = {time} AND uscd ={uscd}"
    cursor.execute(sql)
    existence = cursor.fetchall()


    if len(existence) == 0:
        count = 0
        for i in range(len(temp)):
            sql1 = f"INSERT INTO `raspi_db`.`Anomaly_Score` (`uscd`, `time`, `count`, `temp`, `humidity`, `wateruse`, `carbon_monxide`, `voltare`) VALUES ('{uscd}', '{time}','{count}' ,'{temp[i][0]}','{humidity[i][0]}','{water[i][0]}','{gas[i][0]}','{volt[i][0]}')"
            count = count + 1
            cursor.execute(sql1)
            conn.commit()

    elif len(existence) != 0:
        for i in range(len(temp)):
            sql2 = f"UPDATE `raspi_db`.`Anomaly_Score` SET `temp` ={temp[i][0]},`humidity` ={humidity[i][0]},`wateruse` ={water[i][0]},`carbon_monxide`={gas[i][0]},`voltare` ={volt[i][0]} WHERE uscd ={uscd} AND time ={time} AND count ={i} "
            cursor.execute(sql2)
            conn.commit()



def threshold(uscd,temp,humidity,gas,water,volt):
    conn = getConnection()
    cursor = conn.cursor()
    sql = f"SELECT * FROM raspi_db.threshold where  uscd ={uscd}"
    cursor.execute(sql)
    existence = cursor.fetchall()

    if len(existence) == 0:

        sql1 = f"INSERT INTO `raspi_db`.`threshold` (`uscd`, `temp`, `humidity`, `wateruse`, `carbon_monxide`, `voltare`) VALUES ('{uscd}', '{temp}', '{humidity}', '{gas}', '{water}', '{volt}')"
        cursor.execute(sql1)
        conn.commit()

    elif len(existence) != 0:

        sql2 = f"UPDATE `raspi_db`.`threshold` SET `temp` ={temp}, `humidity`={humidity}, `wateruse`={water}, `carbon_monxide`={gas}, `voltare`={volt} WHERE uscd ={uscd} "
        cursor.execute(sql2)
        conn.commit()


