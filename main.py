from classes import *
import pandas as pd
from database import Database
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

base_url = 'https://isr.org.il/'
loglig_url = 'https://loglig.com:2053/'

# Load links from JSON file
with open('links.json', 'r') as f:
    links_data = json.load(f)

# Select year - change this to switch between years
SELECTED_YEAR = "2024"

# Get URL for selected year
url = None
for link in links_data['links']:
    if link['year'] == SELECTED_YEAR:
        url = link['url']
        break

if url is None:
    raise ValueError(f"Year {SELECTED_YEAR} not found in links.json")

logging.info(f"Processing year: {SELECTED_YEAR}")
logging.info(f"URL: {url}")

comp = CompetitionScraper(url)
comp_names = comp.get_competition_names()

#Init Database
swim_database = Database(file='swim_database_2.sqlite3')

# Get existing discipline_links from ingest_events to skip duplicates
try:
    existing_query = 'SELECT DISTINCT discipline_link FROM ingest_events'
    existing_df = pd.read_sql_query(existing_query, swim_database.conn)
    existing_discipline_links = set(existing_df['discipline_link'].tolist())
    logging.info(f'Found {len(existing_discipline_links)} existing discipline links in database')
except Exception as e:
    logging.warning(f'Could not fetch existing discipline links (table may not exist yet): {e}')
    existing_discipline_links = set()

year_comps = []
for i in comp_names:
    url = base_url + i['competition_link']
    comp_info = \
    SingleCompPage(url=url).get_competition_info()
    for item in comp_info:
        # Skip if this discipline_link already exists in the database
        if item in existing_discipline_links:
            logging.debug(f'Skipping existing discipline link: {item}')
            continue
        year_comps.append({**i, 'discipline_link': item})

logging.info(f'Found {len(year_comps)} new competitions to process (skipped {len([i for comp in comp_names for item in SingleCompPage(base_url + comp["competition_link"]).get_competition_info()]) - len(year_comps)} existing)')

events_lst = []
for i in year_comps:
    #TODO: #10 fix error that some links are not working
    url = i['discipline_link']
    try:
        discipline_info = \
        AthleticsDisciplines(url=url).extract_main_table()
        for item in discipline_info:
            full_dict = {**i, **item}
            events_lst.append(full_dict)
    except Exception as e:
        logging.error(f'Error processing {url}: {e}')
        continue
        
logging.info(f'Extracted {len(events_lst)} events from new competitions')

# filter events so there is more than 0 participants in the event
# filter events so there is a link to the results

if len(events_lst) > 0:
    events_df = pd.DataFrame(events_lst)
    swim_database.insert_dataframe_into_table(events_df, 'ingest_events', if_exists='append')
    logging.info(f'Inserted {len(events_df)} events into ingest_events table')
    swim_database.process_ingest_comp()
else:
    logging.info('No new events to process')
#swim_database