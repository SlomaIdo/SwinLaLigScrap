import pandas as pd
import re
from functions import Rudolph,replace_event_to_Rudolph

mw_df = pd.read_csv('Maccabbi_Weisgal_2023_4.csv')

# replace to manual input
mw_df = mw_df[mw_df['Year Of Birth'].isin([2013, 2014])]
# manually switch so 2013 will be 11 and 2014 will be 10
# TODO: #12 make that as an argument
const_year = int(2024)
mw_df['Age'] = const_year - mw_df['Year Of Birth'] 

#add column Gender
mw_df.loc[mw_df['Category'].str.contains('boys|Men|Boys|men', na=False),'Gender'] = 'M'
mw_df.loc[mw_df['Category'].str.contains('Girls|Women', na=False),'Gender'] = 'F'

mw_df['RudolphEvent'] = mw_df['Event'].apply(replace_event_to_Rudolph)
mw_df[['RudolphEvent','Event']].value_counts()
mw_df = mw_df[mw_df['RudolphEvent'] != False]
# create a Rudolph object for each row
mw_df['RudolphScore'] = mw_df.apply(lambda x: Rudolph(year=str(const_year),
                                                      gender=x['Gender'],
                                                      age=int(x['Age']),
                                                      event=x['RudolphEvent'],
                                                      result=x['Results']),axis=1
                                    )
mw_df.to_csv('Maccabbi_Weisgal_2023_4_RudolphScore.csv', encoding='utf-8-sig')