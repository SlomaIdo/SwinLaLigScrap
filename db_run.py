from classes import *
import pandas as pd
from database import Database

base_url = 'https://isr.org.il/'
loglig_url = 'https://loglig.com:2053/'

swim_database = Database(file='swim_database_2.sqlite3')


def main():
    #df = pd.read_sql_query('SELECT * FROM production_events', swim_database.conn)
    df = pd.read_sql_query('SELECT * FROM links_check', swim_database.conn)
    #swim_database.conn.execute('DROP TABLE IF EXISTS discipline_results_ingest')

    for i,row in df.iterrows():
        url = loglig_url + row['results_link']
        try:
            example = AthleticsDisciplineResults(url=url).extract_results_table()
        except requests.exceptions.ReadTimeout or requests.exceptions.ConnectionError:
            print('The request timed out', url)
            continue
        discpline_results = []
        for item in example:
            full_dict = {**row, **item}
            discpline_results.append(full_dict)
        dis_re_df = pd.DataFrame(discpline_results)    
        #drop this level_0 column
        dis_re_df.rename(columns={'level_0':'level_0_production'}, inplace=True)
        # test dis_re_df here
        try:
            dis_re_df.drop(columns=['Personal Points'], inplace=True)
        except KeyError:
            pass
        #drop the table if it exists
        swim_database.insert_dataframe_into_table(dis_re_df,
                                                   'discipline_results_ingest',
                                                     if_exists='append')

if __name__ == '__main__':
    #main()
    # check that all of the links in production_events['results_link] apears
    #   in discipline_results_ingest['results_link]
    
    #swim_database.check_production_links()
    #try:
     #   main()
    #except Exception as e:
     #   swim_database.check_production_links()
    #swim_database.check_production_links()
    c = swim_database.conn.cursor()
    c.execute('SELECT DISTINCT Club FROM discipline_results_ingest')
    distinct_clubs = [row[0] for row in c.fetchall()]
    wis_df = \
    pd.read_sql_query('SELECT * FROM discipline_results_ingest where Club = "Maccabbi Weisgal"',
                       swim_database.conn)
    wis_df
    #distinct_clubs
                               
