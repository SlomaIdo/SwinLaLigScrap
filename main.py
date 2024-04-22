from classes import *
import pandas as pd

base_url = 'https://isr.org.il/'
url = 'https://isr.org.il/competitions.asp?cYear=2024&cMonth=0&cType=1&cMode=0&isFinish=true'
comp = CompetitionScraper(url)
comp_names = comp.get_competition_names()

year_comps = []
for i in comp_names:
    url = base_url + i['competition_link']
    comp_info = \
    SingleCompPage(url=url).get_competition_info()
    for item in comp_info:    
        year_comps.append({**i, 'discipline_link': item})
events_lst = []
for i in year_comps:
    url = i['discipline_link']
    discipline_info = \
    AthleticsDisciplines(url=url).extract_main_table()
    for item in discipline_info:
        full_dict = {**i, **item}
        events_lst.append(full_dict)
        
events_lst
#year_comps_df = pd.DataFrame(year_comps)
#year_comps_df