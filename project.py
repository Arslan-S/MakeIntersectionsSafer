#Name: Arslan Sajid
#Email: arslan.sajid89@myhunter.cuny.edu
#URL: https://arslansajid527.wixsite.com/proj39542
#Title: Make Intersections Safer
#Resources: https://www.consumerreports.org/car-safety/chevy-silverado-toyota-highlander-and-other-popular-cars-lack-standard-safety-features/, https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95, https://kpattorney.com/vehicle-safety-features-make-driving-safer/

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pandasql as psql
import folium

#This function creates a categorical bar chart from seaborn which compares if popular vehicles have blind-spot warnings and pedestrian detection (standard, optional, not available)
#Data is read in as a dataframe from manually created csv, computed percent of vehicles with the safety features, either standard, optional, or not available, and plotted it as a categorical bar chart
#Source: https://www.consumerreports.org/car-safety/chevy-silverado-toyota-highlander-and-other-popular-cars-lack-standard-safety-features/
def safety_features():
    data = pd.read_csv('Project/bs.csv')

    pct_op_bs = 0
    pct_st_bs = 0
    pct_na_bs = 0
    pct_op_pd = 0
    pct_st_pd = 0
    pct_na_pd = 0

    #compute percent of of cars with blind-spot warnings and pedestrian destection (standard, optional, not available)
    for i in range(len(data)):
        if(data['BLIND SPOT WARNING'][i] == 'Optional'):
            pct_op_bs += 1/len(data)
        elif(data['BLIND SPOT WARNING'][i] == 'Standard'):
            pct_st_bs += 1/len(data)
        else:
            pct_na_bs += 1/len(data)
        
        if(data['PEDESTRIAN DETECTION'][i] == 'Optional'):
            pct_op_pd += 1/len(data)
        elif(data['PEDESTRIAN DETECTION'][i] == 'Standard'):
            pct_st_pd += 1/len(data)
        else:
            pct_na_pd += 1/len(data)

    #prepping data before cleaning for plotting
    st = []
    st.append(pct_st_bs)
    st.append(pct_st_pd)
    op = []
    op.append(pct_op_bs)
    op.append(pct_op_pd)
    na = []
    na.append(pct_na_bs)
    na.append(pct_na_pd)

    #clean data for plotting
    mydata = pd.DataFrame()
    mydata['Option'] = ['Blind-Spot Warning', 'Blind-Spot Warning', 'Blind-Spot Warning', 'Person Detection', 'Person Detection', 'Person Detection']
    mydata['Percent'] = [pct_st_bs, pct_op_bs, pct_na_bs, pct_st_pd, pct_op_pd, pct_na_pd]
    mydata['Percent'] = mydata['Percent'] * 100
    mydata['Type'] = ['Standard', 'Optional', 'Not Available', 'Standard', 'Optional', 'Not Available']

    sns.catplot(kind='bar', x='Option', y='Percent', hue='Type', data=mydata)
    plt.title('Blind-Spot Warning vs. Person Detection Options in Popular Vehicles', y=1.08)
    plt.yticks([0,20,40,60,80,100])
    plt.savefig(r'Project\bs.png', bbox_inches='tight')

#This function creates a horizontal bar chart which show from least to greatest (top to bottom) the primary cause of a collision
#Data is read in as a dataframe from csv, finds the 20 most frequent cause of an accident by sql, and plotted it onto the chart
#Source: https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95
def caused_by():
    data = pd.read_csv('Project\Motor_Vehicle_Collisions_-_Crashes.csv')

    #count how many times each contributing factor occurred in a collision
    sql = 'SELECT "CONTRIBUTING FACTOR VEHICLE 1", count("CONTRIBUTING FACTOR VEHICLE 1") as AMOUNT FROM data GROUP BY "CONTRIBUTING FACTOR VEHICLE 1" ORDER BY AMOUNT DESC LIMIT 20'
    t = psql.sqldf(sql)
    df = pd.DataFrame(t)
    df = df.drop(0)

    plt.barh(df['CONTRIBUTING FACTOR VEHICLE 1'].astype(str), df['AMOUNT'])
    plt.xticks([0,250,500,750,1000,1250,1500,1750,2000,2250,2500])
    plt.ylabel('Causes')
    plt.xlabel('Amount for each Accident Cause')
    plt.title('Most Common Accident Causes')
    plt.savefig('Project\cause.png', bbox_inches='tight')

#This function creates a folium map that shows the top 30 intersections with the most crashes
#Data is read in as dataframe from csv, uses sql to join two dataframes to eliminate duplicate intersections, and plots the resulting dataframe
#Source: https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95
def intersections():
    #data cleaning
    data = pd.read_csv('Project\Motor_Vehicle_Collisions_-_Crashes.csv')
    data = data[data['ON STREET NAME'].notnull()]
    data['ON STREET NAME'] = data['ON STREET NAME'].str.upper()
    data['ON STREET NAME'] = data['ON STREET NAME'].str.strip()
    data['CROSS STREET NAME'] = data['CROSS STREET NAME'].str.upper()
    data['CROSS STREET NAME'] = data['CROSS STREET NAME'].str.strip()

    sql = 'SELECT "ON STREET NAME" as ON_STREET_NAME, "CROSS STREET NAME" as CROSS_STREET_NAME, COUNT(*) as ACCIDENTS, LATITUDE, LONGITUDE FROM data GROUP BY "ON STREET NAME", "CROSS STREET NAME" ORDER BY ACCIDENTS DESC LIMIT 35'
    t = psql.sqldf(sql)

    #clean data that has duplicate intersections written in reverse
    #add those accidents to the first unique intersection
    inter = []
    crash = []
    for i in range(len(t)):
        if([t['ON_STREET_NAME'][i], t['CROSS_STREET_NAME'][i]] in inter):
            index = inter.index([t['ON_STREET_NAME'][i], t['CROSS_STREET_NAME'][i]])
            crash[index] += t['ACCIDENTS'][i]
        elif([t['CROSS_STREET_NAME'][i], t['ON_STREET_NAME'][i]] in inter):
            index = inter.index([t['CROSS_STREET_NAME'][i], t['ON_STREET_NAME'][i]])
            crash[index] += t['ACCIDENTS'][i]
        if([t['ON_STREET_NAME'][i], t['CROSS_STREET_NAME'][i]] not in inter and [t['CROSS_STREET_NAME'][i], t['ON_STREET_NAME'][i]] not in inter):
            inter.append([t['ON_STREET_NAME'][i], t['CROSS_STREET_NAME'][i]])
            crash.append(t['ACCIDENTS'][i])

    #create new df with unique intersections
    newdf = pd.DataFrame(columns=['ON_STREET_NAME', 'CROSS_STREET_NAME', 'ACCIDENTS'])
    for i in range(len(inter)):
        da = {'ON_STREET_NAME':inter[i][0], 'CROSS_STREET_NAME':inter[i][1], 'ACCIDENTS':crash[i]}
        newdf = newdf.append(da, ignore_index=True)

    #join unique intersections and accidents with the original sql query to have latitude and logitude alongside it
    sql2 = 'SELECT A.ON_STREET_NAME, A.CROSS_STREET_NAME, A.ACCIDENTS, B.LATITUDE, B.LONGITUDE FROM newdf A JOIN t B ON A.ON_STREET_NAME = B.ON_STREET_NAME AND A.CROSS_STREET_NAME = B.CROSS_STREET_NAME'
    t2 = psql.sqldf(sql2)

    fol = t2
    fol = fol.dropna()
    map = folium.Map(location=[fol.LATITUDE.mean(), fol.LONGITUDE.mean()])

    str = []
    #popup string to display
    for i in range(len(fol)):
        string = f'{fol["ON_STREET_NAME"][i]} & {fol["CROSS_STREET_NAME"][i]}' + '\n' + f'(Crashes: {fol["ACCIDENTS"][i]})'
        str.append(string)

    #add markers
    for index, location_info in fol.iterrows():
        folium.Marker([location_info['LATITUDE'], location_info['LONGITUDE']], popup=str[index], icon=folium.Icon(color='red')).add_to(map)

    map.save('Project\index.html')

#This function creates two line graphs, one to compare the amount of crashes to the number of injuries and deaths, and the other to compare the same thing just with cars equipped with Collision Warning and Automatic Braking
#Data is read in as a dataframe from csv, finds the number of crashes, injured, and killed. Then uses sql to group it by year and plot it. 
#Source: https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95, https://kpattorney.com/vehicle-safety-features-make-driving-safer/
def injury_v_killed():
    #data cleanup
    data = pd.read_csv('Project\Motor_Vehicle_Collisions_-_Crashes.csv')
    data['YEAR'] = pd.DatetimeIndex(data['CRASH DATE']).year
    data['INJURED'] = data['NUMBER OF PERSONS INJURED'] + data['NUMBER OF PEDESTRIANS INJURED'] + data['NUMBER OF CYCLIST INJURED'] + data['NUMBER OF MOTORIST INJURED']
    data['KILLED'] = data['NUMBER OF PERSONS KILLED'] + data['NUMBER OF PEDESTRIANS KILLED'] + data['NUMBER OF CYCLIST KILLED'] + data['NUMBER OF MOTORIST KILLED']

    #without all cars having safety features
    sql = 'SELECT YEAR, count(COLLISION_ID) as CRASHES, sum(INJURED) as INJURED, sum(KILLED) as KILLED FROM data GROUP BY YEAR'
    t = psql.sqldf(sql)

    #with all cars having safety features
    #multiplied collisions by 0.89 because the data from kpattorney states an 11% decrease in collisions
    #multiplied collisions with an injury by 0.79 because the data from kpattorney states a 21% decrease in collisions with an injury
    #nothing multiplied sum(KILLED) because no data found
    sql2 = 'SELECT YEAR, ROUND(count(COLLISION_ID) *0.89, 0) as CRASHES, ROUND(sum(INJURED) * 0.79, 0) as INJURED, sum(KILLED) as KILLED FROM data GROUP BY YEAR'
    t2 = psql.sqldf(sql2).astype(int)

    graph = t.plot('YEAR')
    plt.title('People Injured vs. Killed in Relation to Number of Crashes')
    plt.xlabel('Year')
    plt.yticks([0, 250, 500, 750, 1000, 1250, 1500, 1750, 2000])
    plt.ylabel('Occurrences')
    plt.legend()
    plt.savefig('Project\inj.png')

    graph2 = t2.plot('YEAR')
    plt.title('People Injured vs. Killed in Relation to Number of Crashes \n With Collision Warning and Automatic Braking')
    plt.xlabel('Year')
    plt.yticks([0, 250, 500, 750, 1000, 1250, 1500, 1750, 2000])
    plt.ylabel('Occurrences')
    plt.legend()
    plt.savefig('Project\inj2.png')
