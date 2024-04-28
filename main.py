from classes import *
import pandas as pd
from database import Database

base_url = 'https://isr.org.il/'
loglig_url = 'https://loglig.com:2053/'
url = 'https://isr.org.il/competitions.asp?cYear=2024&cMonth=0&cType=1&cMode=0&isFinish=true'
comp = CompetitionScraper(url)
comp_names = comp.get_competition_names()

#Init Database
swim_database = Database(file='swim_database.sqlite3')

year_comps = []
for i in comp_names:
    url = base_url + i['competition_link']
    comp_info = \
    SingleCompPage(url=url).get_competition_info()
    for item in comp_info:    
        year_comps.append({**i, 'discipline_link': item})
events_lst = []
for i in year_comps:
    #TODO: #10 fix error that some links are not working
    url = i['discipline_link']
    discipline_info = \
    AthleticsDisciplines(url=url).extract_main_table()
    for item in discipline_info:
        full_dict = {**i, **item}
        events_lst.append(full_dict)
        
events_lst
# filter events so there is more than 0 participants in the event
# filter events so there is a link to the results

events_df = pd.DataFrame(events_lst)

swim_database.insert_dataframe_into_table(events_df, 'ingest_events', if_exists='replace')
swim_database.process_ingest_comp()
swim_database