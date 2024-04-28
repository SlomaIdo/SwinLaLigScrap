import sqlite3
import pandas as pd
import sqlalchemy
import numpy as np

class Database:
    """Database from the swimming results
    """
    def __init__(self, file='database.db')-> None:    
        self.file = file
        self.conn = sqlite3.connect(file)
    def insert_dataframe_into_table(self, df, table_name, if_exists='append'):
        df.to_sql(table_name, self.conn, if_exists=if_exists)
        return df.shape[0]
        #return the number of rows from the table in the database
        if if_exists == 'replace':
            c = self.conn.cursor()
            c.execute('SELECT COUNT(*) FROM %s' % table_name)
            num_rows = c.fetchone()[0]
            if num_rows == df.shape[0]:
                print(f'All rows were inserted correctly into {table_name}')
            else:
                print(f'Not all rows were inserted correctly into {table_name}')
            return num_rows

        

    #create a method to transfer from ingest to production tables
    def process_ingest_comp(self):
        # since the comp table is not so big we will download all of the data
        # and process it in memory.
        # Obviously this is not the best way to do it, but it is the simplest         
        df = pd.read_sql('SELECT * FROM ingest_events', self.conn)
        df_passed, df_failed = process_ingest(df)
        passed_rows = self.insert_dataframe_into_table(df_passed, 'production_events', if_exists='replace')
        failed_rows = self.insert_dataframe_into_table(df_failed, 'failed_events', if_exists='replace')
        print(f'Number of rows inserted into production table: {passed_rows}')
        print(f'Number of rows inserted into failed table: {failed_rows}')
        if passed_rows == df_passed.shape[0]:
            print('Production:All rows were inserted correctly')
        if failed_rows == df_failed.shape[0]:
            print('Failed: All rows were inserted correctly')

        # Get confirmation that the data was inserted correctly
        # by getting the count of the rows in the production table and make sure it is the same as the original table
        

def process_ingest(df):
    """This function clean the first ingest table and insert the data into the production table.

    Args:
        df (_type_): pandas DataFrame with the data from the ingest table.
    """
    df_copy = df.copy()
    #clean the data
    #competition_name is the name of the competition in Hebrew    
    # Check the the link is by the template 'comp.asp?compID=\\d+$'
    #Add that to a new column called 'competition_id_check'
    df_copy['competition_link_check'] = df_copy['competition_link'].str.contains('comp\\.asp\\?compID=\\d*')
    df_copy['results_link_check'] = df_copy['results_link'].notna()
    df_passed = \
        df_copy[((df_copy['competition_link_check'] == True) & \
                (df_copy['results_link_check'] == True))]
    df_failed = \
        df_copy[~((df_copy['competition_link_check'] == True) & \
                (df_copy['results_link_check'] == True))]
    # filter events so there is more than 0 participants in the event
    # filter events so there is a link to the results
    #move Total Participants to an inetger column
    df_passed['TotalParticipantsInt'] = pd.to_numeric(df_passed['Total Participants']).astype(int)
    # move these row to df_failed from df_passed
    zero_part_event = df_passed[df_passed['TotalParticipantsInt'] == 0]
    df_failed = pd.concat([df_failed, zero_part_event[df_failed.columns]])
    df_passed = df_passed[df_passed['TotalParticipantsInt'] > 0]
    # Convert to Date and Time for example: 06/10/2023 09:00 should be:
    # Date: 2023-10-06 
    # Time: 09:00
    #First we see which rows have the correct format
    time_pattern = '\\d{2}/\\d{2}/\\d{4} \\d{2}:\\d{2}'
    time_pass =np.where(~df_passed['Start Time'].str.contains(time_pattern))
    if len(time_pass[0]) > 0:
        print(f'The following rows do not have the correct format for Start Time: {time_pass[0]}')
        raise ValueError('The Start Time column does not have the correct format')
    else:    
        df_passed['Date'] = df_passed['Start Time'].str.split(' ').str[0]
        df_passed['Date'] = pd.to_datetime(df_passed['Date'], dayfirst=True)
        df_passed['Year'] = df_passed['Date'].dt.year   
        df_passed['Time'] = df_passed['Start Time'].str.split(' ').str[1]
    df_passed['Status'] = 'Passed'
    df_failed['Status'] = 'Failed'
    #insert the data into the production table
    return df_passed, df_failed

