import pymysql as db
import datetime

now = datetime.datetime.now()+ datetime.timedelta( hours=-1)
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

def anomaly(uscd, temp,humidity):
    conn = getConnection()
    cursor = conn.cursor()
    sql = f"SELECT * FROM raspi_db.Anomaly where uscd = {uscd}"
    cursor.execute(sql)
    existence = cursor.fetchall()

    if len(existence) == 0 :
        sql1 = f"INSERT INTO `raspi_db`.`Anomaly`(`uscd`, `temp`, `humidity`) VALUES ('{uscd}','{temp}',{humidity})"
        cursor.execute(sql1)
        conn.commit()

    elif len(existence) == 1 :
        sql2 =f"UPDATE raspi_db.Anomaly SET `temp` = {temp},  `humidity` = {humidity} WHERE uscd = {uscd};"
        cursor.execute(sql2)
        conn.commit()



