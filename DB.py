import pymysql as db
import datetime


now = datetime.datetime.now()+ datetime.timedelta(hours=-1)
time = now.strftime("%Y-%m-%d %H")


def getConnection():
    con = db.connect (host="221.145.148.151",port=8888, user="raspi_user",passwd="topad159@",db="raspi_db")
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
    print(volt)
    return volt








def anomaly(uscd, temp, humidity, gas, water, volt):
    conn = getConnection()
    cursor = conn.cursor()
    sql = f"SELECT * FROM raspi_db.Anomaly where uscd = {uscd}"
    cursor.execute(sql)
    existence = cursor.fetchall()

    if len(existence) == 0 :
        sql1 = f"INSERT INTO `raspi_db`.`Anomaly`(`uscd`, `temp`, `humidity`, 'gas', 'water', 'volt') VALUES " \
               f"('{uscd}','{temp}','{humidity}', '{gas}', '{water}', '{volt}')"
        cursor.execute(sql1)
        conn.commit()

    elif len(existence) == 1 :
        sql2 =f"UPDATE raspi_db.Anomaly SET `temp` = {temp},  `humidity` = {humidity}, 'gas' = {gas}, " \
              f"water' = {water}, 'volt' = {volt} WHERE uscd = {uscd};"
        cursor.execute(sql2)
        conn.commit()

def anomaly_score_temp(uscd, data,time):
    conn = getConnection()
    cursor = conn.cursor()
    sql = f"SELECT * FROM raspi_db.Anomaly_Score where time = {time} AND uscd ={uscd}"
    cursor.execute(sql)
    existence = cursor.fetchall()

    if len(existence) == 0:
        for i in range(len(data)):

            sql1 = f"INSERT INTO `raspi_db`.`Anomaly_Score` (`uscd`, `time`, `count`, `temp`) VALUES ('{uscd}', '{time}','{i}' ,'{data[i]}')"
            cursor.execute(sql1)
            conn.commit()
    elif len(existence) != 0:
        for i in range(len(data)):
            sql2 = f"UPDATE `raspi_db`.`Anomaly_Score` SET `temp` ={data[i]} WHERE uscd ={uscd} AND time ={time} AND count ={i} "
            cursor.execute(sql2)
            conn.commit()


def anomaly_score_humidity(uscd, data,time):
    conn = getConnection()
    cursor = conn.cursor()
    sql = f"SELECT * FROM raspi_db.Anomaly_Score where time = {time} AND uscd ={uscd}"
    cursor.execute(sql)
    existence = cursor.fetchall()

    if len(existence) == 0:
        for i in range(len(data)):
            sql1 = f"INSERT INTO `raspi_db`.`Anomaly_Score` (`uscd`, `time`, `count`, `humidity`) VALUES ('{uscd}', '{time}','{i}' ,'{data[i]}')"
            cursor.execute(sql1)
            conn.commit()

    elif len(existence) != 0:
        for i in range(len(data)):
            sql2 = f"UPDATE `raspi_db`.`Anomaly_Score` SET `humidity` ={data[i]} WHERE uscd ={uscd} AND time ={time} AND count ={i} "
            cursor.execute(sql2)
            conn.commit()


def threshold_temp(uscd,threshold):
    conn = getConnection()
    cursor = conn.cursor()
    sql = f"SELECT * FROM raspi_db.threshold where  uscd ={uscd}"
    cursor.execute(sql)
    existence = cursor.fetchall()

    if len(existence) == 0:

        sql1 = f"INSERT INTO `raspi_db`.`threshold` (`uscd`, `temp`) VALUES ('{uscd}', '{threshold}')"
        cursor.execute(sql1)
        conn.commit()

    elif len(existence) != 0:

        sql2 = f"UPDATE `raspi_db`.`threshold` SET `temp` ={threshold} WHERE uscd ={uscd} "
        cursor.execute(sql2)
        conn.commit()


def threshold_humidity(uscd,threshold):
    conn = getConnection()
    cursor = conn.cursor()
    sql = f"SELECT * FROM raspi_db.threshold where  uscd ={uscd}"
    cursor.execute(sql)
    existence = cursor.fetchall()

    if len(existence) == 0:

        sql1 = f"INSERT INTO `raspi_db`.`threshold` (`uscd`, `humidity`) VALUES ('{uscd}', '{threshold}')"
        cursor.execute(sql1)
        conn.commit()

    elif len(existence) != 0:

        sql2 = f"UPDATE `raspi_db`.`threshold` SET `humidity` ={threshold} WHERE uscd ={uscd} "
        cursor.execute(sql2)
        conn.commit()