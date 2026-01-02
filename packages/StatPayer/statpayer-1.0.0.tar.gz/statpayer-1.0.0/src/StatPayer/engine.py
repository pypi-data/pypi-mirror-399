import logging
lg = logging.getLogger(__name__)

import pandas as pd

def read_timesheet(filepath):
    '''Returns a Timesheet object'''

    df = pd.read_excel(filepath, sheet_name='Summary By User', usecols=['First Name', 'Last Name', 'Regular', 'Position'])

    totals = df[df['Position'] == 'Total']
    return totals

def generate_statsheet(timesheet_df):
    df = timesheet_df.copy()

    df['Average Daily Hours'] = df['Regular']/20.0
    df = df.round(decimals={'Average Daily Hours': 2})

    df['Name'] = df['Last Name'] + ', ' + df['First Name']

    df=df.drop(columns='First Name')
    df=df.drop(columns='Last Name')
    df=df.drop(columns='Position')
    df=df.rename(mapper={'Regular': 'Total (4 weeks)'}, axis=1)

    df = df[['Name', 'Total (4 weeks)', 'Average Daily Hours']]
    print(df)

    return df

def write_timesheet(filepath, statsheet_df):
    statsheet_df.to_excel(filepath, columns=['Name', 'Total (4 weeks)', 'Average Daily Hours'], index=False)
