""" mk_events.py

Utilities to create events from recommendations
"""
import pandas as pd

import event_study.config as cfg


def mk_event_df(tic):
    """ Subsets and processes recommendations given a ticker and return a data
    frame with all events in the sample.

    Parameters
    ----------
    tic : str
        Ticker

    Returns
    -------
    pandas dataframe

        The columns are:
        * event_date : string
            Date string with format 'YYYY-MM-DD'
        * firm : string
            Name of the firm (upper case)
        * event_type : string
            Either "downgrade" or "upgrade"

        index: integer
            Index named 'event_id' starting at 1

    Notes
    -----
    This function will perform the following actions:

    1. Read the appropriate CSV file with recommendations into a data frame
    2. Create variables identifying the firm and the event date
    3. Deal with multiple recommendations
    4. Create a table with all relevant events

    """

    # Step 1
    pth = cfg.csv_locs(tic)['rec_csv']
    df = pd.read_csv(pth, index_col='Date', parse_dates=['Date'])
    # Standardise column names
    cols = ['firm', 'action']
    df = cfg.standardise_colnames(df)[cols]

    # Step 2
    df.loc[:, 'firm'] = df.loc[:, 'firm'].str.upper()
    df.loc[:, 'event_date'] = df.index.strftime('%Y-%m-%d')

    # Step 3
    df.sort_index(inplace=True)
    groups = df.groupby(['event_date', 'firm'])
    df = groups.last().reset_index()

    # Step 4
    # 4.1: Subset the "action" column
    cond = df.loc[:, 'action'].str.contains('up|down')
    df = df.loc[cond]

    # 4.2: Create a column with the event type ("downgrade" or "upgrade")
    def _mk_et(value):
        """ Converts the string `value` as follows:
            - "down" --> "downgrade"
            - "up" --> "upgrade"
        and raise an exception if value is not "up" or "down"
        """
        if value == 'down':
            return 'downgrade'
        elif value == 'up':
            return 'upgrade'
        else:
            raise Exception(f'Unknown value for column `action`: {value}')

    df.loc[:, 'event_type'] = df['action'].apply(_mk_et)

    # 4.3 Create the event id index:
    df.reset_index(inplace=True)
    df.index = df.index + 1
    df.index.name = 'event_id'

    # 4.4: Reorganise the columns
    cols = ['firm', 'event_date', 'event_type']
    df = df[cols]

    return df


if __name__ == "__main__":
    tic = 'TSLA'
    df = mk_event_df(tic)
    print(df)
    df.info()
