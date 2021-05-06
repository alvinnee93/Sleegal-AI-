#exec(open("task.py", errors='ignore').read())

import pandas as pd

trips=pd.read_csv('Divvy_Trips_2014-Q4.csv')
stations=pd.read_csv('Divvy_Stations_2014-Q3Q4.csv')

d={i:[stations[stations.id==i]['dpcapacity'].iloc[0]] for i in set(stations.id)}

minmax={i:(0,0) for i in d}
  
for id in d.keys(): #for each station
    df_from=trips[trips['from_station_id']==id]['starttime'].to_frame() #we get all departures from that station
    df_from['effect']=-1 #add the effect of the departure on stock
    df_to=trips[trips['to_station_id']==id]['stoptime'].to_frame() #we get all arrivals to that station
    df_to['effect']=1 #add the effect of the arrival on stock
    df_from.columns=['time', 'effect'] 
    df_to.columns=['time', 'effect']
    res=pd.concat([df_from, df_to]) #merge departures and arrivals
    res['new']=pd.to_datetime(res.time) 
    res['date']=res['new'].apply(lambda x: x.date()) #get the date of timestamps
    res.sort_values('new', inplace=True) #sort by time
    p=pd.concat([res[['date', 'effect']], res.groupby('date')['effect'].cumsum()], axis=1) #calculate effect of each record on stock for this specific date
    p.columns=['date', 'effect', 'cumsum']
    p['stock']=p['cumsum']+d[id][0] #get the stock considering that we begun with stock=full capacity
    minmax[id] = (p['stock'].min(), p['stock'].max()) #get the overall min and max of stock for this station
        
for k,v in minmax.items(): #create a dictionary with mins and maxes for all stations
    minmax[k]=list(v)+[d[k][0]]

#create the final dataset and save it to excel file
result=pd.DataFrame.from_dict(minmax, orient='index') 
result.reset_index(inplace=True)
result.columns=['id', 'min', 'max', 'capacity']
result.sort_values('min', inplace=True)

result.to_excel('result.xlsx', index=False)