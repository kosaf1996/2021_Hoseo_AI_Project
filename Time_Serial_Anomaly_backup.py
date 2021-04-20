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
now = datetime.datetime.now() + datetime.timedelta( hours=-1)
time = now.strftime("%Y-%m-%d %H")
user_size = DB.user_size()
DB_csv.DB_Data_Csv_Save()

#학습데이터

#index_col = CSV 데이터가 Index_col 을 기준으로 정렬됨
Traning_data = pd.read_csv(
    f'{path}\Data\Time_Serial_Anomaly_Data.csv', parse_dates=True, index_col="timestamp"
)
#for i in range(user_size):
#    Test_data = pd.read_csv(
#        f'C:\\Users\GM\Desktop\Data\Time_Serial_Anomaly{time}_{i}.csv', parse_dates=True, index_col="timestamp"
#    )


#LOAD_DATA head print
print(Traning_data.head())

#이상없는 시계열 데이터 matplotlib 그래프 출력
#fig, ax = plt.subplots()
#Traning_data.plot(legend=False, ax=ax)
#plt.title('Traning_Data')
#plt.savefig(f'{path}/img/Traning_Data{time}.png')
#plt.show()

#이상 있는 시계열 데이터 matplotlib 그래프 출력
#fig, ax = plt.subplots()
#Test_data.plot(legend=False, ax=ax)
#plt.title('Anomaly')
#plt.show()

#학습 데이터 정규화
training_mean = Traning_data.mean() #평균값
training_std = Traning_data.std() #표준편차
Traning_data_value = (Traning_data - training_mean) / training_std #Data - 평균 / 편차
print("Number of training samples:", len(Traning_data_value))


#TIME_STEPS = 288
TIME_STEPS = 24

# TIME_STEPS훈련 데이터에서 연속 된 데이터 값을 결합하는 시퀀스를 만듭니다 .
def create_sequences(values, time_steps=TIME_STEPS):
    output = []
    for i in range(len(values) - time_steps):
        output.append(values[i : (i + time_steps)])
    return np.stack(output)


x_train = create_sequences(Traning_data_value.values)
print("Training input shape: ", x_train.shape) #행, 열
print("x_train.shape: ", x_train.shape[0])
##LSTM 모델구축
model = keras.Sequential(
    [
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


#모델 훈련

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

#훈련 성능 plt
#plt.plot(history.history["loss"], label="Training Loss")
#plt.plot(history.history["val_loss"], label="Validation Loss")
#plt.legend()
#plt.title('Traning_Performance')
#plt.savefig(f'{path}/img/Traning_Performance{time}.png')
#plt.show()

## 이상 감지
#샘플의 성능 저하가 '임계 값보다 큰 경우'
#그럼 모델이있는 패턴을보고 추론 할 수 있습니다.
#샘플을 '이상'으로 분류합니다.

x_train_pred = model.predict(x_train)
train_mae_loss = np.mean(np.abs(x_train_pred - x_train), axis=1)

#plt.hist(train_mae_loss, bins=50)
#plt.xlabel("Train loss")
#plt.ylabel("No of samples")
#plt.title('loss')
#plt.savefig(f'{path}/img/loss{time}.png')
#plt.show()

# 성능 임계 값을 가져옵니다.
threshold = np.max(train_mae_loss)
print("Reconstruction error threshold: ", threshold)


# 첫 번째 시퀀스 학습 방법 확인
#plt.plot(x_train[0])
#plt.plot(x_train_pred[0])
#plt.title('sequence')
#plt.savefig(f'{path}/img/sequence{time}.png')
#plt.show()

### 테스트 데이터 준비
#def normalize_test(values, mean, std):
#    values -= mean
#    values /= std
#    return values

for i in range(user_size):
    # 테스트 데이터
    print(f'{path}\Data\Time_Serial_Anomaly{time}_{i}.csv')
    Test_data = pd.read_csv(
        f'{path}\Data\Time_Serial_Anomaly{time}_{i}.csv', parse_dates=True, index_col="timestamp"
    )

    df_test_value = (Test_data - training_mean) / training_std
    #fig, ax = plt.subplots()
    #df_test_value.plot(legend=False, ax=ax)
    #plt.savefig(f'{path}/img/sequence{time}_{i}.png')
    #plt.show()

    # 테스트 값에서 시퀀스를 만듭니다.
    x_test = create_sequences(df_test_value.values)
    print("Test input shape: ", x_test.shape)

    # 테스트 성능을 가져옵니다.
    x_test_pred = model.predict(x_test)
    test_mae_loss = np.mean(np.abs(x_test_pred - x_test), axis=1)
    test_mae_loss = test_mae_loss.reshape((-1))

    #plt.hist(test_mae_loss, bins=50)
    #plt.xlabel("data_loss")
    #plt.ylabel("No of samples")
    #plt.title('data_perfomens')
    #plt.savefig(f'{path}/img/data_perfomens{time}_{i}.png')
    #plt.show()

    # 이상이있는 모든 샘플을 감지합니다.
    anomalies = test_mae_loss > threshold
    print("Anomaly data(count) : ", np.sum(anomalies))
    print("Indices of anomaly samples: ", np.where(anomalies))

    if np.sum(anomalies) == 0 :
        DB.anomaly(i,0)

    elif np.sum(anomalies) !=0 :
        DB.anomaly(i,1)

    #Anomaly Data RED
    # 데이터 i는 샘플 [(i-timesteps + 1) ~ (i)]이 이상이면 이상입니다.
    anomalous_data_indices = []
    for data_idx in range(TIME_STEPS - 1, len(df_test_value) - TIME_STEPS + 1):
        if np.all(anomalies[data_idx - TIME_STEPS + 1 : data_idx]):
           anomalous_data_indices.append(data_idx)

    df_subset = Test_data.iloc[anomalous_data_indices]
    fig, ax = plt.subplots()
    Test_data.plot(legend=False, ax=ax)
    df_subset.plot(legend=False, ax=ax, color="r")
    plt.title('Detection')
    plt.title('Detection')
    plt.savefig(f'{path}/img/Detection{time}_{i}.png')
    plt.show()