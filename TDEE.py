#you may need to pip install myfitnesspal and pandas
#before you use this script

#no, I don't know how to set up a dependency file or 
#a package. If you want fancy features like that, send 
#me a tutorial 

import myfitnesspal
import datetime
import pandas as pd 


###VARIABLES###

##input your username and password here ('username', 'password')

username = 'your_username_here'
password = 'your_password_here'

##these are the date operators (year, month, day) format


start_date = datetime.date(2021, 6, 1)
end_date = datetime.date(2021, 9, 16)

##start_date is the lower bound backward, 
# IE "how far back do I want to pull data for?"
##the initial query takes a long time since each date obeject 
##(below) takes a long time to pull data for, and it has to loop 
## since date objects from the myfitnesspal only return one date 
# at a time. Which is a super bummer.  

##no I haven't gotten the end date to change dynamically yet. 
# check back next week maybe
##script starts here

client = myfitnesspal.Client(username, password)

#delta iterates through the loop, don't change this unless you don't
##want daily data

delta = datetime.timedelta(days=1)

#this returns your daily weight in one query and returns a data frame, fat
def return_weight(start_date, end_date):
    fat = client.get_measurements('Weight', start_date, end_date )
    df = pd.DataFrame(fat.values(), fat.keys())
    df = df.reset_index()
    df = df.rename(columns={"index": "Date", 0: "Weight"})
    return df
fat = return_weight(start_date, end_date)

#this is the long loop it returns the marcos data in a dataframe called df
def get_records(start_date, end_date):
    df = pd.DataFrame()
    while start_date <= end_date:
        data ={}
        macros = client.get_date(start_date)
        if bool(macros): 
            data = macros.totals
        else: 
            data = None
        data['date'] = start_date
        print (start_date)
        df = df.append(data, ignore_index = True)
        start_date += delta
    return df

df = get_records(start_date, end_date)


def join_and_clean(df, fat):
    df_merged = pd.merge(df, fat, left_on=  ['date'],
                       right_on= ['Date'], 
                       how = 'left')
    df_merged = df_merged.drop(columns = ['Date'])
    df_merged['date'] = pd.to_datetime(df['date'])
    df_merged['week'] = df_merged['date'].dt.isocalendar().week
    df_merged['year'] = df_merged['date'].dt.isocalendar().year
    df_merged['Weight'] = pd.to_numeric(df_merged['Weight'])
    return df_merged

df = join_and_clean(df, fat)

#gets weekly averages of calories and weight and returns a weekly dataframe
#with some averages, changes and a weekly TDEE estimate
def TDEE(df): 
    df_avgcal = df.groupby(['week', 'year'])['calories'].mean()
    df_avgcal = df_avgcal.to_frame()
    df_avgcal = df_avgcal.sort_values(by=['year','week'])
    df_avgweight = df.groupby(['week', 'year'])['Weight'].mean()
    df_avgweight.to_frame()
    result = pd.concat([df_avgcal, df_avgweight], axis=1, join="inner")
    result = result.reset_index()
    result['avg_cals'] = result['calories'].diff()
    result['avg_weight'] = result['Weight'].diff()
    result['TDEE'] = (result['calories']*7+result['avg_weight']*-1*3500)/7
    return result

result = TDEE(df)

##merges and saves to a csv for later
##future todo is to check for this csv and load the data from it 
##instead of the query that takes forever 
def merge(dataframe1, dataframe2): 
    merged = pd.merge(dataframe1, dataframe2, on=['week', 'year'])
    merged = merged.rename(columns={"calories_x": "calories", "Weight_x": "Weight", "calories_y":"avg_calories", "Weight_y":"Average Weight", "avg_cals" : "delta_cals" , "avg_weight" :"delta_weight" })
    merged.to_csv(r'myfitnesspalfinal.csv')
    return merged

merged = merge(df, result)

print("last 2 weeks of data:\n")
print(merged.tail(14))


most_recent = merged[merged['date'] == (merged['date'].max())]
x = most_recent['TDEE']
y = most_recent['avg_calories']

x = int(x.item())
y = int(y.item())
print("TDEE: " +str(x) +"\n" + "Avg Calories: "+ str(y)) 
