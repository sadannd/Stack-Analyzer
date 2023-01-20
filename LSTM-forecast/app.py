'''
Goal of LSTM microservice:
1. LSTM microservice will accept the GitHub data from Flask microservice and will forecast the data for next 1 year based on past 30 days
2. It will also plot three different graph (i.e.  "Model Loss", "LSTM Generated Data", "All Issues Data") using matplot lib 
3. This graph will be stored as image in Google Cloud Storage.
4. The image URL are then returned back to Flask microservice.
'''
# Import all the required packages
from flask import Flask, jsonify, request, make_response
import os
from dateutil import *
from datetime import timedelta
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import time
from flask_cors import CORS
import datetime
import statsmodels.api as sm
import math
import prophet
from prophet import Prophet
# Tensorflow (Keras & LSTM) related packages
import tensorflow as tf
from tensorflow.python.keras import Sequential
from tensorflow.python.keras.layers import Input, Dense, LSTM, Dropout
from tensorflow.python.keras.callbacks import EarlyStopping
from sklearn.preprocessing import MinMaxScaler
from prophet.diagnostics import cross_validation, performance_metrics
from prophet.plot import plot_cross_validation_metric


# Import required storage package from Google Cloud Storage
from google.cloud import storage


# Initilize flask app
app = Flask(__name__)
# Handles CORS (cross-origin resource sharing)
CORS(app)
# Initlize Google cloud storage client
client = storage.Client()

# Add response headers to accept all types of  requests

def build_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type")
    response.headers.add("Access-Control-Allow-Methods",
                         "PUT, GET, POST, DELETE, OPTIONS")
    return response

#  Modify response headers when returning to the origin

def build_actual_response(response):
    response.headers.set("Access-Control-Allow-Origin", "*")
    response.headers.set("Access-Control-Allow-Methods",
                         "PUT, GET, POST, DELETE, OPTIONS")
    return response

'''
API route path is  "/api/forecast"
This API will accept only POST request
'''
max_issues_created_day='Monday'

max_issues_closed_day='Monday'
max_issues_closed_month='January'
@app.route('/api/forecast', methods=['POST'])
def forecast():
    print('----------------------------------------------');
    body = request.get_json()
    issues = body["issues"]
    type = body["type"]
    repo_name = body["repo"]
    data_frame = pd.DataFrame(issues)
    # with pd.ExcelWriter('dataframe.xlsx') as writer:  
    #     data_frame.to_excel(writer, sheet_name='Sheet_name_1')
    # print(data_frame)

    #   df = pd.read_excel()
    df=pd.DataFrame(data_frame,columns=['issue_number','created_at','closed_at'])
    df['closed_at'].replace('', np.nan, inplace=True)
    df.dropna(subset=['closed_at'], inplace=True)

    days_created=[]
    max_issues_closed_day='Monday'

    for i in df['created_at']:
        date_string=str(i)
        a=date_string.replace("-"," ")
        day_string=a[:10]
        # print(day_string)
        
        day_name= ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday','Sunday']
        day = datetime.datetime.strptime(day_string, '%Y %m %d').weekday()
        # print(day_name[day])
        days_created.append(day_name[day])


    df['days_created']=days_created


    # print(df['days'].value_counts())
    # print()
    create_count_monday=0
    create_count_tuesday=0
    create_count_wednesday=0
    create_count_thusday=0
    create_count_friday=0
    create_count_saturday=0
    create_count_sunday=0
    for i in df['days_created']:
        if i == 'Monday':
            create_count_monday+=1
        elif i == 'Tuesday':
            create_count_tuesday+=1
        elif i == 'Wednesday':
            create_count_wednesday+=1
        elif i == 'Thursday':
            create_count_thusday+=1
        elif i == 'Friday':
            create_count_friday+=1
        elif i == 'Saturday':
            create_count_saturday+=1
        elif i == 'Sunday':
            create_count_sunday+=1
        
    if create_count_monday>create_count_tuesday and create_count_monday>create_count_wednesday and create_count_monday>create_count_thusday and create_count_monday>create_count_friday and create_count_monday>create_count_saturday and create_count_monday>create_count_sunday:
        max_issues_created_day='Monday'

    elif create_count_tuesday>create_count_monday and create_count_tuesday>create_count_wednesday and create_count_tuesday>create_count_thusday and create_count_tuesday>create_count_friday and create_count_tuesday>create_count_saturday and create_count_tuesday>create_count_sunday:
        max_issues_created_day='Tuesday'

    elif create_count_wednesday>create_count_tuesday and create_count_wednesday>create_count_monday and create_count_wednesday>create_count_thusday and create_count_wednesday>create_count_friday and create_count_wednesday>create_count_saturday and create_count_wednesday>create_count_sunday:
        max_issues_created_day='Wednesday'

    elif create_count_thusday>create_count_tuesday and create_count_thusday>create_count_wednesday and create_count_thusday>create_count_monday and create_count_thusday>create_count_friday and create_count_thusday>create_count_saturday and create_count_thusday>create_count_sunday:
        max_issues_created_day='Thursday'

    elif create_count_friday>create_count_tuesday and create_count_friday>create_count_wednesday and create_count_friday>create_count_thusday and create_count_friday>create_count_monday and create_count_friday>create_count_saturday and create_count_friday>create_count_sunday:
        max_issues_created_day='Friday'

    elif create_count_saturday>create_count_tuesday and create_count_saturday>create_count_wednesday and create_count_saturday>create_count_thusday and create_count_saturday>create_count_friday and create_count_saturday>create_count_monday and create_count_saturday>create_count_sunday:
        max_issues_created_day='Saturday'

    elif create_count_sunday>create_count_tuesday and create_count_sunday>create_count_wednesday and create_count_sunday>create_count_thusday and create_count_sunday>create_count_friday and create_count_sunday>create_count_saturday and create_count_sunday>create_count_monday:
        max_issues_created_day='Sunday'
    days_closed=[]
    for i in df['closed_at']:
        date_string=str(i)
        a=date_string.replace("-"," ")
        day_string=a[:10]
        # print(day_string)
        
        day_name= ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday','Sunday']
        day = datetime.datetime.strptime(day_string, '%Y %m %d').weekday()
        # print(day_name[day])
        days_closed.append(day_name[day])

    # print(days)

    df['days_closed']=days_closed


    # print(df['days'].value_counts())
    # print()
    count_mon=0
    count_tue=0
    count_wed=0
    count_thu=0
    count_fri=0
    count_sat=0
    count_sun=0
    for i in df['days_closed']:
        if i == 'Monday':
            count_mon+=1
        elif i == 'Tuesday':
            count_tue+=1
        elif i == 'Wednesday':
            count_wed+=1
        elif i == 'Thursday':
            count_thu+=1
        elif i == 'Friday':
            count_fri+=1
        elif i == 'Saturday':
            count_sat+=1
        elif i == 'Sunday':
            count_sun+=1
        
    if count_mon>count_tue and count_mon>count_wed and count_mon>count_thu and count_mon>count_fri and count_mon>count_sat and count_mon>count_sun:
        max_issues_closed_day='Monday'

    elif count_tue>count_mon and count_tue>count_wed and count_tue>count_thu and count_tue>count_fri and count_tue>count_sat and count_tue>count_sun:
        max_issues_closed_day='Tuesday'

    elif count_wed>count_tue and count_wed>count_mon and count_wed>count_thu and count_wed>count_fri and count_wed>count_sat and count_wed>count_sun:
        max_issues_closed_day='Wednesday'

    elif count_thu>count_tue and count_thu>count_wed and count_thu>count_mon and count_thu>count_fri and count_thu>count_sat and count_thu>count_sun:
        max_issues_closed_day='Thursday'

    elif count_fri>count_tue and count_fri>count_wed and count_fri>count_thu and count_fri>count_mon and count_fri>count_sat and count_fri>count_sun:
        max_issues_closed_day='Friday'

    elif count_sat>count_tue and count_sat>count_wed and count_sat>count_thu and count_sat>count_fri and count_sat>count_mon and count_sat>count_sun:
        max_issues_closed_day='Saturday'

    elif count_sun>count_tue and count_sun>count_wed and count_sun>count_thu and count_sun>count_fri and count_sun>count_sat and count_sun>count_mon:
        max_issues_closed_day='Sunday'
    
    months=[]
    for i in df['created_at']:
        date_string=str(i)
        a=date_string.replace("-"," ")
        day_string=a[:10]
        # print(day_string)
        day = datetime.datetime.strptime(day_string, '%Y %m %d')
        month=day.month
        months.append(month)

    # print(days)

    df['month']=months
    # print(df['month'].value_counts())

    count_1=0
    count_2=0
    count_3=0
    count_4=0
    count_5=0
    count_6=0
    count_7=0
    count_8=0
    count_9=0
    count_10=0
    count_11=0
    count_12=0
    for i in df['month']:
        if i == 1:
            count_1+=1
        elif i == 2:
            count_2+=1
        elif i == 3:
            count_3+=1
        elif i == 4:
            count_4+=1
        elif i == 5:
            count_5+=1
        elif i == 6:
            count_6+=1
        elif i == 7:
            count_7+=1
        elif i == 8:
            count_8+=1
        elif i == 9:
            count_9+=1
        elif i == 10:
            count_10+=1
        elif i == 11:
            count_11+=1
        elif i == 12:
            count_12+=1

        
    if count_1>count_2 and count_1>count_3 and count_1>count_4 and count_1>count_5 and count_1>count_6 and count_1>count_7 and count_1>count_8 and count_1>count_9 and count_1>count_10 and count_1>count_11 and count_1>count_12:
        max_issues_closed_month='January';

    elif count_2>count_1 and count_2>count_3 and count_2>count_4 and count_2>count_5 and count_2>count_6 and count_2>count_7 and count_2>count_8 and count_2>count_9 and count_2>count_10 and count_2>count_11 and count_2>count_12:
        max_issues_closed_month='February'

    elif count_3>count_2 and count_3>count_1 and count_3>count_4 and count_3>count_5 and count_3>count_6 and count_3>count_7 and count_3>count_8 and count_3>count_9 and count_3>count_10 and count_3>count_11 and count_3>count_12:
        max_issues_closed_month='March'

    elif count_4>count_2 and count_4>count_3 and count_4>count_1 and count_4>count_5 and count_4>count_6 and count_4>count_7 and count_4>count_8 and count_4>count_9 and count_4>count_10 and count_4>count_11 and count_4>count_12:
        max_issues_closed_month='April'

    elif count_5>count_2 and count_5>count_3 and count_5>count_4 and count_5>count_1 and count_5>count_6 and count_5>count_7 and count_5>count_8 and count_5>count_9 and count_5>count_10 and count_5>count_11 and count_5>count_12:
        max_issues_closed_month='May'

    elif count_6>count_2 and count_6>count_3 and count_6>count_4 and count_6>count_5 and count_6>count_1 and count_6>count_7 and count_6>count_8 and count_6>count_9 and count_6>count_10 and count_6>count_11 and count_6>count_12:
        max_issues_closed_month='Jun'

    elif count_7>count_2 and count_7>count_3 and count_7>count_4 and count_7>count_5 and count_7>count_6 and count_7>count_1 and count_7>count_8 and count_7>count_9 and count_7>count_10 and count_7>count_11 and count_7>count_12:
        max_issues_closed_month='July'

    elif count_8>count_2 and count_8>count_3 and count_8>count_4 and count_8>count_5 and count_8>count_6 and count_8>count_1 and count_8>count_7 and count_8>count_9 and count_8>count_10 and count_8>count_11 and count_8>count_12:
        max_issues_closed_month='Augest'

    elif count_9>count_2 and count_9>count_3 and count_9>count_4 and count_9>count_5 and count_9>count_6 and count_9>count_1 and count_9>count_8 and count_9>count_7 and count_9>count_10 and count_9>count_11 and count_9>count_12:
        max_issues_closed_month='September'

    elif count_10>count_2 and count_10>count_3 and count_10>count_4 and count_10>count_5 and count_10>count_6 and count_10>count_1 and count_10>count_8 and count_10>count_9 and count_10>count_7 and count_10>count_11 and count_10>count_12:
        max_issues_closed_month='October'

    elif count_11>count_2 and count_11>count_3 and count_11>count_4 and count_11>count_5 and count_11>count_6 and count_11>count_1 and count_11>count_8 and count_11>count_9 and count_11>count_10 and count_11>count_7 and count_11>count_12:
        max_issues_closed_month='November'

    elif count_12>count_2 and count_12>count_3 and count_12>count_4 and count_12>count_5 and count_12>count_6 and count_12>count_1 and count_12>count_8 and count_12>count_9 and count_12>count_10 and count_12>count_11 and count_12>count_7:
        max_issues_closed_month='Dedember'

    df1 = data_frame.groupby([type], as_index=False).count()
    df = df1[[type, 'issue_number']]
    df.columns = ['ds', 'y']

    df['ds'] = df['ds'].astype('datetime64[ns]')
    array = df.to_numpy()
    x = np.array([time.mktime(i[0].timetuple()) for i in array])
    y = np.array([i[1] for i in array])

    lzip = lambda *x: list(zip(*x))

    days = df.groupby('ds')['ds'].value_counts()
    Y = df['y'].values
    X = lzip(*days.index.values)[0]
    firstDay = min(X)

    '''
    To achieve data consistancy with both actual data and predicted values, 
    add zeros to dates that do not have orders
    [firstDay + timedelta(days=day) for day in range((max(X) - firstDay).days + 1)]
    '''
    Ys = [0, ]*((max(X) - firstDay).days + 1)
    days = pd.Series([firstDay + timedelta(days=i)
                      for i in range(len(Ys))])
    for x, y in zip(X, Y):
        Ys[(x - firstDay).days] = y

    # Modify the data that is suitable for LSTM
    Ys = np.array(Ys)
    Ys = Ys.astype('float32')
    Ys = np.reshape(Ys, (-1, 1))
    # Apply min max scaler to transform the data
    scaler = MinMaxScaler(feature_range=(0, 1))
    Ys = scaler.fit_transform(Ys)
    # Divide training - test data with 80-20 split
    train_size = int(len(Ys) * 0.80)
    test_size = len(Ys) - train_size
    train, test = Ys[0:train_size, :], Ys[train_size:len(Ys), :]
    # print('train',train)
    # print('test',test)
    print('train size:', len(train), ", test size:", len(test))

    # Create the training and test dataset
    def create_dataset(dataset, look_back=1):
        X, Y = [], []
        for i in range(len(dataset)-look_back-1):
            a = dataset[i:(i+look_back), 0]
            X.append(a)
            Y.append(dataset[i + look_back, 0])
        return np.array(X), np.array(Y)
    '''
    Look back decides how many days of data the model looks at for prediction
    Here LSTM looks at approximately one month data
    '''
    look_back = 30
    X_train, Y_train = create_dataset(train, look_back)
    X_test, Y_test = create_dataset(test, look_back)

    # Reshape input to be [samples, time steps, features]
    X_train = np.reshape(X_train, (X_train.shape[0], 1, X_train.shape[1]))
    X_test = np.reshape(X_test, (X_test.shape[0], 1, X_test.shape[1]))

    # Verifying the shapes
    X_train.shape, X_test.shape, Y_train.shape, Y_test.shape

    # Model to forecast
    model = Sequential()
    model.add(LSTM(100, input_shape=(X_train.shape[1], X_train.shape[2])))
    model.add(Dropout(0.2))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer='adam')

    # Fit the model with training data and set appropriate hyper parameters
    history = model.fit(X_train, Y_train, epochs=20, batch_size=70, validation_data=(X_test, Y_test),
                        callbacks=[EarlyStopping(monitor='val_loss', patience=10)], verbose=1, shuffle=False)

    # df['closed_at'].replace('', np.nan, inplace=True)
    # df.dropna(subset=['closed_at'], inplace=True)
    # df1 = data_frame.groupby(['created_at'], as_index=False).count()
   
   
    ## StatsModel
    df_stat = data_frame[['created_at', 'issue_number']]
    x_stat = df_stat.columns = ['ds', 'y']
    df_stat['ds'] = df_stat['ds'].astype('datetime64[ns]')
    df_train_stat = df_stat.iloc[:math.ceil(len(df_stat)*0.8)]
    df_test_stat = df_stat.iloc[math.ceil(len(df_stat)*0.8):]

    array_stat = df_train_stat.to_numpy()
    x_stat = np.array([time.mktime(i[0].timetuple()) for i in array_stat])
    df_train_stat['x']=x_stat
    y_stat = np.array([i[1] for i in array_stat])
    df_train_stat['y']=y_stat

    x_stat = sm.add_constant(x_stat)
    model_stat = sm.OLS(y_stat, x_stat).fit()
    # print(model.summary())

    array1_stat = df_test_stat.to_numpy()
    x1_stat = np.array([time.mktime(i[0].timetuple()) for i in array1_stat])
    df_test_stat['x']=x1_stat
    y1_stat = np.array([i[1] for i in array1_stat])
    df_test_stat['y']=y1_stat
    df_test_stat.drop('ds', axis=1, inplace=True)
    # print(df_test)

    predict_stat = model_stat.predict(df_test_stat)
    df_test_stat['predict']=-predict_stat
    df_stat_crea = data_frame[['created_at', 'issue_number']]
    df_test_stat['created_at']=df_stat_crea['created_at']
    # print(df_test_stat)

    # df = pd.read_excel('./output.xlsx')
    # data_frame=pd.DataFrame(df,columns=['issue_number','created_at', 'closed_at'])
    
    #Prophet
    df_prophet = data_frame[[type, 'issue_number']]
    df_prophet[type].replace('', np.nan, inplace=True)
    df_prophet.dropna(subset=[type], inplace=True)
    # print(df_prophet)
    x = df_prophet.columns = ['ds', 'y']

    model_prophet = Prophet(interval_width= 0.95)
    model_prophet.fit(df_prophet)
    future = model_prophet.make_future_dataframe(periods=80, freq='M')
    forecast = model_prophet.predict(future)
    #fig1 = model_prophet.plot(forecast)
    fig2 = model_prophet.plot_components(forecast)
    df_cv = cross_validation(model_prophet, horizon='20 days')
    df_p = performance_metrics(df_cv)
    fig3 = plot_cross_validation_metric(df_cv, metric='mape')  

    


    # plt.show()

    '''
    Creating image URL
    BASE_IMAGE_PATH refers to Google Cloud Storage Bucket URL.Add your Base Image Path in line 145
    if you want to run the application local
    LOCAL_IMAGE_PATH refers local directory where the figures generated by matplotlib are stored
    These locally stored images will then be uploaded to Google Cloud Storage
    '''
    #BASE_IMAGE_PATH = os.environ.get(
        #'BASE_IMAGE_PATH', 'Your_Base_Image_path')
    BASE_IMAGE_PATH=   "https://storage.googleapis.com/lstm-forecast-bucket/"
    # DO NOT DELETE "static/images" FOLDER as it is used to store figures/images generated by matplotlib
    LOCAL_IMAGE_PATH = "static/images/"

    # Creating the image path for model loss, LSTM generated image and all issues data image
    MODEL_LOSS_IMAGE_NAME = "model_loss_" + type +"_"+ repo_name + ".png"
    MODEL_LOSS_URL = BASE_IMAGE_PATH + MODEL_LOSS_IMAGE_NAME

    LSTM_GENERATED_IMAGE_NAME = "lstm_generated_data_" + type +"_" + repo_name + ".png"
    LSTM_GENERATED_URL = BASE_IMAGE_PATH + LSTM_GENERATED_IMAGE_NAME

    ALL_ISSUES_DATA_IMAGE_NAME = "all_issues_data_" + type + "_"+ repo_name + ".png"
    ALL_ISSUES_DATA_URL = BASE_IMAGE_PATH + ALL_ISSUES_DATA_IMAGE_NAME
    
    STATS_GENERATED_IMAGE_NAME = "stats_generated_data_" + type +"_" + repo_name + ".png"
    STATS_GENERATED_URL = BASE_IMAGE_PATH + STATS_GENERATED_IMAGE_NAME

    PROPHET_GENERATED_IMAGE_NAME_PREDICTION = "prophet_generated_data_prediction" + type +"_" + repo_name + ".png"
    PROPHET_GENERATED_IMAGE_NAME_PREDICTION_URL = BASE_IMAGE_PATH + PROPHET_GENERATED_IMAGE_NAME_PREDICTION

    PROPHET_GENERATED_IMAGE_NAME_ERROR = "prophet_generated_data_error" + type +"_" + repo_name + ".png"
    PROPHET_GENERATED_IMAGE_NAME_ERROR_URL = BASE_IMAGE_PATH + PROPHET_GENERATED_IMAGE_NAME_ERROR


    # Add your unique Bucket Name if you want to run it local
    #BUCKET_NAME = os.environ.get(
     #   'BUCKET_NAME', 'Your_BUCKET_NAME')
    BUCKET_NAME="lstm-forecast-bucket";
    # Model summary()

    # Plot the model loss image
    plt.figure(figsize=(8, 4))
    plt.plot(history.history['loss'], label='Train Loss')
    plt.plot(history.history['val_loss'], label='Test Loss')
    plt.title('Model Loss For ' + type)
    plt.ylabel('Loss')
    plt.xlabel('Epochs')
    plt.legend(loc='upper right')
    # Save the figure in /static/images folder
    plt.savefig(LOCAL_IMAGE_PATH + MODEL_LOSS_IMAGE_NAME)

    # Predict issues for test data
    y_pred = model.predict(X_test)

    # Plot the LSTM Generated image
    fig, axs = plt.subplots(1, 1, figsize=(10, 4))
    X = mdates.date2num(days)
    axs.plot(np.arange(0, len(Y_train)), Y_train, 'g', label="history")
    axs.plot(np.arange(len(Y_train), len(Y_train) + len(Y_test)),
             Y_test, marker='.', label="true")
    axs.plot(np.arange(len(Y_train), len(Y_train) + len(Y_test)),
             y_pred, 'r', label="prediction")
    axs.legend()
    axs.set_title('LSTM Generated Data For ' + type)
    axs.set_xlabel('Time Steps')
    axs.set_ylabel('Issues')
    # Save the figure in /static/images folder
    plt.savefig(LOCAL_IMAGE_PATH + LSTM_GENERATED_IMAGE_NAME)

    # Plot the All Issues data images
    fig, axs = plt.subplots(1, 1, figsize=(10, 4))
    X = mdates.date2num(days)
    axs.plot(X, Ys, 'purple', marker='.')
    locator = mdates.AutoDateLocator()
    axs.xaxis.set_major_locator(locator)
    axs.xaxis.set_major_formatter(mdates.AutoDateFormatter(locator))
    axs.legend()
    axs.set_title('All Issues Data')
    axs.set_xlabel('Date')
    axs.set_ylabel('Issues')
    # Save the figure in /static/images folder
    plt.savefig(LOCAL_IMAGE_PATH + ALL_ISSUES_DATA_IMAGE_NAME)

    plt.clf()
    #StatsModel Graph
    x_stat = df_test_stat['x']
    y_stat = df_test_stat['created_at']
    plt.plot(y_stat, x_stat)
    # plt.show()
   
    x1_stat = df_test_stat['predict']
    y1_stat = df_test_stat['created_at']
    # second plot with x1 and y1 data
    plt.plot(y1_stat, x1_stat, '-.')
    
    plt.xlabel("X-axis data")
    plt.ylabel("Y-axis data")
    plt.title('Created using stats Model actual and predicted')
    # plt.show()
    plt.savefig(LOCAL_IMAGE_PATH + STATS_GENERATED_IMAGE_NAME)

    ####FbProphet Graphs
    fig2.savefig(LOCAL_IMAGE_PATH + PROPHET_GENERATED_IMAGE_NAME_PREDICTION)
    fig3.savefig(LOCAL_IMAGE_PATH + PROPHET_GENERATED_IMAGE_NAME_ERROR)




    # Uploads an images into the google cloud storage bucket
    bucket = client.get_bucket(BUCKET_NAME)
    new_blob = bucket.blob(MODEL_LOSS_IMAGE_NAME)
    new_blob.upload_from_filename(
        filename=LOCAL_IMAGE_PATH + MODEL_LOSS_IMAGE_NAME)
    new_blob = bucket.blob(ALL_ISSUES_DATA_IMAGE_NAME)
    new_blob.upload_from_filename(
        filename=LOCAL_IMAGE_PATH + ALL_ISSUES_DATA_IMAGE_NAME)
    new_blob = bucket.blob(LSTM_GENERATED_IMAGE_NAME)
    new_blob.upload_from_filename(
        filename=LOCAL_IMAGE_PATH + LSTM_GENERATED_IMAGE_NAME)
    new_blob = bucket.blob(STATS_GENERATED_IMAGE_NAME)
    new_blob.upload_from_filename(
        filename=LOCAL_IMAGE_PATH + STATS_GENERATED_IMAGE_NAME)

    new_blob = bucket.blob(PROPHET_GENERATED_IMAGE_NAME_PREDICTION)
    new_blob.upload_from_filename(
        filename=LOCAL_IMAGE_PATH + PROPHET_GENERATED_IMAGE_NAME_PREDICTION)
    new_blob = bucket.blob(PROPHET_GENERATED_IMAGE_NAME_ERROR)
    new_blob.upload_from_filename(
        filename=LOCAL_IMAGE_PATH + PROPHET_GENERATED_IMAGE_NAME_ERROR)            

    # Construct the response
    json_response = {
        "model_loss_image_url": MODEL_LOSS_URL,
        "lstm_generated_image_url": LSTM_GENERATED_URL,
        "all_issues_data_image": ALL_ISSUES_DATA_URL,
        "stats_generated_image_url": STATS_GENERATED_URL,
        "max_issues_created_day":max_issues_created_day,
        "max_issues_closed_day": max_issues_closed_day,
        "max_issues_closed_month": max_issues_closed_month,
        "prophet_generated_image_url":PROPHET_GENERATED_IMAGE_NAME_PREDICTION_URL,
        "prophet_generated_image_url1":PROPHET_GENERATED_IMAGE_NAME_ERROR_URL

    }
    # Returns image url back to flask microservice
    return jsonify(json_response)


# Run LSTM app server on port 8080
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
