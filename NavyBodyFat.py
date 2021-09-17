import myfitnesspal
import datetime
import pandas as pd 
import numpy as np

##input your username and password here ('username', 'password')
username = 'your_user_name'
password = 'your_password'

client = myfitnesspal.Client(username, password)

start_date = datetime.date(2014, 6, 1)
end_date = datetime.date(2021, 9, 16)
delta = datetime.timedelta(days=1)

#in inches
height = 68

waist = client.get_measurements('Waist', start_date, end_date )
neck = client.get_measurements('Neck', start_date, end_date )

def BFP(waist, neck, height_in): 
    BFP = (86.010*np.log10(waist-neck)) - (70.041*np.log10(height_in)) + 36.76
    return BFP 

def body_fat(start_date, end_date):
    waist = client.get_measurements('Waist', start_date, end_date )
    neck = client.get_measurements('Neck', start_date, end_date )
    waist = pd.DataFrame(waist.values(), waist.keys())
    neck = pd.DataFrame(neck.values(), neck.keys())
    waist = waist.reset_index()
    neck = neck.reset_index()
    waist['index'] = pd.to_datetime(waist['index'])
    neck['index'] = pd.to_datetime(neck['index'])
    waist = waist.rename(columns={"index": "Date", 0: "Waist"})
    neck = neck.rename(columns={"index": "Date", 0: "Neck"})
    x = pd.merge(waist, neck, left_on=  ['Date'],
                   right_on= ['Date'], 
                   how = 'left')
    x['Body Fat %'] = round(BFP(x['Waist'], x['Neck'], height),1)
    x['Date'] = pd.to_datetime(x['Date'])
    x = x.sort_values(by=['Date'])
    x = x.reset_index()
    x = x.drop(columns = 'index')
    return x

x = body_fat(start_date, end_date)
print(x)
