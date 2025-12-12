from classes import *
import pandas as pd
from database import Database
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

base_url = 'https://isr.org.il/'
loglig_url = 'https://loglig.com:2053/'

swim_database = Database(file='swim_database_2.sqlite3')


def main():
    logging.info('Starting event processing')
    df = pd.read_sql_query('SELECT * FROM production_events', swim_database.conn)
    logging.info(f'Found {len(df)} events in production_events')
    
    # Get already processed results_links from discipline_results_ingest
    try:
        processed_links_query = 'SELECT DISTINCT results_link FROM discipline_results_ingest'
        processed_links_df = pd.read_sql_query(processed_links_query, swim_database.conn)
        processed_links = set(processed_links_df['results_link'].tolist())
        logging.info(f'Found {len(processed_links)} already processed events')
    except Exception as e:
        logging.warning(f'Could not fetch processed links (table may not exist yet): {e}')
        processed_links = set()
    
    events_processed = 0
    events_skipped = 0
    events_failed = 0
    
    for i, row in df.iterrows():
        results_link = row['results_link']
        
        # Skip already processed events
        if results_link in processed_links:
            events_skipped += 1
            if events_skipped % 100 == 0:
                logging.info(f'Skipped {events_skipped} already processed events')
            continue
        
        url = loglig_url + results_link
        
        try:
            example = AthleticsDisciplineResults(url=url).extract_results_table()
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:
            logging.warning(f'Request timed out for {url}')
            events_failed += 1
            continue
        except Exception as e:
            logging.error(f'Unexpected error processing {url}: {e}')
            events_failed += 1
            continue
        
        if not example:
            logging.debug(f'No results found for {url}')
            continue
        
        discpline_results = []
        for item in example:
            full_dict = {**row, **item}
            discpline_results.append(full_dict)
        
        dis_re_df = pd.DataFrame(discpline_results)
        
        # Rename level_0 column
        if 'level_0' in dis_re_df.columns:
            dis_re_df.rename(columns={'level_0': 'level_0_production'}, inplace=True)
        
        # Drop all variable point columns that are not needed
        columns_to_drop = ['Personal Points', 'Club Points']
        dropped_cols = []
        for col in columns_to_drop:
            if col in dis_re_df.columns:
                dis_re_df.drop(columns=[col], inplace=True)
                dropped_cols.append(col)
        
        if dropped_cols:
            logging.debug(f'Dropped columns: {", ".join(dropped_cols)}')
        
        # Insert into database
        try:
            swim_database.insert_dataframe_into_table(
                dis_re_df,
                'discipline_results_ingest',
                if_exists='append'
            )
            events_processed += 1
            processed_links.add(results_link)  # Add to set to avoid reprocessing in same run
            
            if events_processed % 10 == 0:
                logging.info(f'Progress: {events_processed} events processed, {events_skipped} skipped, {events_failed} failed')
        except Exception as e:
            logging.error(f'Failed to insert data for {url}: {e}')
            events_failed += 1
    
    logging.info(f'Processing complete: {events_processed} events processed, {events_skipped} skipped, {events_failed} failed')

def verify_all_events_processed():
    """Verify that all events from production_events have been processed.
    
    Returns:
        tuple: (bool, int, list) - (all_processed, missing_count, missing_links)
    """
    logging.info('Verifying all events have been processed...')
    
    # Get all results_links from production_events
    production_query = 'SELECT DISTINCT results_link FROM production_events'
    production_df = pd.read_sql_query(production_query, swim_database.conn)
    production_links = set(production_df['results_link'].tolist())
    
    # Get all results_links from discipline_results_ingest
    try:
        ingest_query = 'SELECT DISTINCT results_link FROM discipline_results_ingest'
        ingest_df = pd.read_sql_query(ingest_query, swim_database.conn)
        ingest_links = set(ingest_df['results_link'].tolist())
    except Exception as e:
        logging.error(f'Could not fetch from discipline_results_ingest: {e}')
        return False, len(production_links), list(production_links)
    
    # Find missing links
    missing_links = production_links - ingest_links
    
    if missing_links:
        logging.warning(f'Found {len(missing_links)} events not yet processed out of {len(production_links)} total')
        logging.info(f'Coverage: {len(ingest_links)}/{len(production_links)} ({len(ingest_links)/len(production_links)*100:.1f}%)')
        logging.debug(f'Missing links sample (first 5): {list(missing_links)[:5]}')
        return False, len(missing_links), list(missing_links)
    else:
        logging.info(f'✓ All {len(production_links)} events have been processed!')
        return True, 0, []

if __name__ == '__main__':
    main()
    
    # Verify all events have been processed
    all_processed, missing_count, missing_links = verify_all_events_processed()
    
    if not all_processed:
        logging.warning(f'{missing_count} events still need processing. Run the script again to process them.')
                           
