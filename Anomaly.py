import numpy as np
import pandas as pd
from tensorflow import keras
from tensorflow.keras import layers
from matplotlib import pyplot as plt
import datetime
import DB
import DB_csv
import os

path = os.getcwd()
now = datetime.datetime.now() + datetime.timedelta(hours=-1)
time = now.strftime("%Y-%m-%d %H")
score_time = now.strftime("%H")
user_size = DB.user_size()
TIME_STEPS = 1
DB_csv.DB_Data_Csv_Save()
pd.options.display.float_format = '{:.5f}'.format


# TIME_STEPS훈련 데이터에서 연속 된 데이터 값을 결합하는 시퀀스를 만듭니다 .
def create_sequences(values, time_steps=TIME_STEPS):
    output = []
    for i in range(len(values)):
        output.append(values[i : (i + time_steps)])
    return np.stack(output)


def traning():
    # 학습데이터
    # index_col = CSV 데이터가 Index_col 을 기준으로 정렬됨
    Traning_data = pd.read_csv(
        f'{path}/Treaning/Time_Serial_Anomaly_Data.csv', parse_dates=True, index_col="timestamp"
        , usecols=['timestamp', 'temp', 'humidity', 'gas', 'water', 'volt'])

    # LOAD_DATA head print
    Traning_data[Traning_data < 0] = -Traning_data  # 음수 값을 양수로 변환
    # print(Traning_data.head())

    # 학습 데이터 정규화
    training_mean = Traning_data.mean()  # 평균값
    # print(f"Training_data.mean : {training_mean}")
    training_std = Traning_data.std()  # 표준편차
    # print(f"Training_std : {training_std}")
    Traning_data_value = (Traning_data - training_mean) / training_std  # Data - 평균 / 편차
    # print("Number of training samples:", len(Traning_data_value))
    Traning_data_value = Traning_data_value.fillna(0)  # NAN 값 0으로 변환
    # print(f"Training_data_value : {Traning_data_value}")

    # TIME_STEPS = 288

    # create_sequenses 함수를 호출해 연속된 시퀀스 값을 만듬
    x_train = create_sequences(Traning_data_value.values)
    # print("Training input shape: ", x_train.shape) #행, 열
    # print("x_train.shape: ", x_train.shape[0])
    x_train = x_train.astype(float)
    # print(f"x_train : {x_train}")

    ##CNN 모델구축
    model = keras.Sequential(  # 순차 모델
        [
            # Input 텐서를 인스턴스화 한다 (sharp(24,1)) == 이는 배치크기가 24인  Layer 가 하나 생성된다.
            layers.Input(shape=(x_train.shape[1], x_train.shape[2])),
            layers.Conv1D(
                filters=32, kernel_size=7, padding="same", strides=2, activation="relu"
            ),
            layers.Dropout(rate=0.2),
            layers.Conv1D(
                filters=16, kernel_size=7, padding="same", strides=2, activation="relu"
            ),
            layers.Conv1DTranspose(
                filters=16, kernel_size=7, padding="same", strides=2, activation="relu"
            ),
            layers.Dropout(rate=0.2),
            layers.Conv1DTranspose(
                filters=32, kernel_size=7, padding="same", strides=2, activation="relu"
            ),
            layers.Conv1DTranspose(filters=1, kernel_size=7, padding="same"),
        ]
    )
    model.compile(optimizer=keras.optimizers.Adam(learning_rate=0.001), loss="mse")
    model.summary()

    # 모델 훈련

    history = model.fit(
        x_train,
        x_train,
        epochs=5,
        batch_size=100,
        validation_split=0.1,
        callbacks=[
            keras.callbacks.EarlyStopping(monitor="val_loss", patience=5, mode="min")
        ],
    )
    return model, x_train, training_mean, training_std


## 이상 감지
# 샘플의 성능 저하가 '임계 값보다 큰 경우'
# 그럼 모델이있는 패턴을보고 추론 할 수 있습니다.
# 샘플을 '이상'으로 분류합니다.
def prediction():
    model, x_train, training_mean, training_std = traning()
    # print(f"model : {model}")
    x_train_pred = model.predict(x_train)
    # print(f"x_train_pred :  {x_train_pred}")
    # print(f"x_train : {x_train}")

    train_mae_loss = np.mean(np.abs(x_train_pred - x_train), axis=1)
    # print(f"train_mae_loss : {train_mae_loss}")
    # 성능 임계 값을 가져옵니다.

    train_temp, train_humidity, train_gas, train_water, train_volt = np.split(train_mae_loss, 5, axis=1)
    threshold_temp = np.max(train_temp)
    threshold_humidity = np.max(train_humidity)
    threshold_gas = np.max(train_gas)
    threshold_water = np.max(train_water)
    threshold_volt = np.max(train_volt)

    # threshold = np.max(train_mae_loss)
    print("Reconstruction error threshold 'temp', 'humidity', 'gas', 'water', 'volt' : ", threshold_temp, threshold_humidity,
          threshold_gas, threshold_water, threshold_volt)

    Temp_Status = []
    Humidity_Status = []
    Gas_Status = []
    Water_Status = []
    Volt_Status = []


    for i in range(user_size):
        # 테스트 데이터
        print(f'{path}/Data/Time_Serial_Anomaly{time}_{i}.csv')
        Test_data = pd.read_csv(
            f'{path}/Data/Time_Serial_Anomaly{time}_{i}.csv', parse_dates=True, index_col="timestamp"
            , usecols=['timestamp', 'temp', 'humidity', 'gas', 'water', 'volt'])

        Test_data[Test_data < 0] = -Test_data
        # print(Test_data.head())

        df_test_value = (Test_data - training_mean) / training_std
        df_test_value = df_test_value.fillna(0)

        # 테스트 값에서 시퀀스를 만듭니다.
        x_test = create_sequences(df_test_value.values)

        # print(f"Test input shape:  {x_test.shape}")
        # 테스트 성능을 가져옵니다.
        x_test_pred = model.predict(x_test)

        test_mae_loss = np.mean(np.abs(x_test_pred - x_test), axis=1)

        #where_are_NaNs = np.isnan(test_mae_loss)  # NAN 값 0으로 변환
        #test_mae_loss[where_are_NaNs] = 0  # NAN 값 0으로 변환


        #test_mae_loss = test_mae_loss.reshape((-1))
        #print(f"test_mae_loss : {test_mae_loss}")

        #train_temp, train_humidity, train_gas, train_water, train_volt = np.split(train_mae_loss, 5, axis=1)
        test_temp, test_humidity, test_gas, test_water, test_volt = np.split(test_mae_loss, 5,axis=1)
        #print(test_temp)

        model, x_train, training_mean, training_std = traning()
        # print(f"model : {model}")

        # 이상이있는 모든 샘플을 감지합니다.
        anomalies_temp = test_temp > threshold_temp
        anomalies_humidity = test_humidity > threshold_humidity
        anomalies_gas = test_gas > threshold_gas
        anomalies_water = test_water > threshold_water
        anomalies_volt = test_volt > threshold_volt
        # print("Anomaly data(count) : ", np.sum(anomalies))
        # print("Indices of anomaly samples: ", np.where(anomalies))
        # print(f"test_mae_loss : {type(test_mae_loss)}")


        #Anomaly_Score Status
        if np.sum(anomalies_temp) == 0:
            Temp_Status.append(0)

        elif np.sum(anomalies_temp) != 0:
            Temp_Status.append(1)

        if np.sum(anomalies_humidity) == 0:
            Humidity_Status.append(0)

        elif np.sum(anomalies_humidity) != 0:
            Humidity_Status.append(1)

        if np.sum(anomalies_gas) == 0:
            Gas_Status.append(0)

        elif np.sum(anomalies_gas) != 0:
            Gas_Status.append(1)


        if np.sum(anomalies_water) == 0:
            Water_Status.append(0)

        elif np.sum(anomalies_water) != 0:
            Water_Status.append(1)


        if np.sum(anomalies_volt) == 0:
            Volt_Status.append(0)

        elif np.sum(anomalies_volt) != 0:
            Volt_Status.append(1)

        DB.anomaly(i,Temp_Status[i] , Humidity_Status[i],Gas_Status[i],Water_Status[i],Volt_Status[i])
        DB.anomaly_score(i, test_temp, test_humidity, test_gas, test_water, test_volt, score_time)
        DB.threshold(i, threshold_temp, threshold_humidity, threshold_gas, threshold_water, threshold_volt)



    return