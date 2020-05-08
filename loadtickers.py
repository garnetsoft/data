import pandas as pd
import requests
from bs4 import BeautifulSoup

def parse_html_table(table):
    n_columns = 0
    n_rows=0
    column_names = []

    # Find number of rows and columns
    # we also find the column titles if we can
    for row in table.find_all('tr'):
        
        # Determine the number of rows in the table
        td_tags = row.find_all('td')
        if len(td_tags) > 0:
            n_rows+=1
            if n_columns == 0:
                # Set the number of columns for our table
                n_columns = len(td_tags)
                
        # Handle column names if we find them
        th_tags = row.find_all('th') 
        if len(th_tags) > 0 and len(column_names) == 0:
            for th in th_tags:
                column_names.append(th.get_text().strip())

    # Safeguard on Column Titles
    if len(column_names) > 0 and len(column_names) != n_columns:
        raise Exception("Column titles do not match the number of columns")

    columns = column_names if len(column_names) > 0 else range(0,n_columns)
    df = pd.DataFrame(columns = columns,
                      index= range(0,n_rows))
    row_marker = 0
    for row in table.find_all('tr'):
        column_marker = 0
        columns = row.find_all('td')
        for column in columns:
            df.iat[row_marker,column_marker] = column.get_text().strip()
            column_marker += 1
        if len(columns) > 0:
            row_marker += 1
            
    # Convert to float if possible
    for col in df:
        try:
            df[col] = df[col].astype(float)
        except ValueError:
            pass
    
    return df

def getTickers(url, class_attr, id_attr):
    r = requests.get(url)
    # Extract the content
    c = r.content
    #print(c)

    # Create a soup object
    soup = BeautifulSoup(c, 'lxml')

    # Find the element on the webpage
    htable = soup.find('table', {'class': class_attr, 'id': id_attr})
    #print(htable)

    df = parse_html_table(htable)
    print(df.head())

    #df = df.sort_values(column_name)
    # add ticker column on the table
    #df['ticker'] = df[column_name]
    #df.insert(0, 'ticker', df[column_name])
    #dfcsv = df.iloc[:,[0,1,2]]
    #df.to_csv(fname, index=True)

    return df


# Make the GET request to a url
DOW30 = "https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average"
SP500 = "http://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
SP100 = "https://en.wikipedia.org/wiki/S%26P_100"
NDX100 = "https://en.wikipedia.org/wiki/NASDAQ-100"

dow = getTickers(DOW30, 'wikitable sortable', 'constituents')
sp500 = getTickers(SP500, 'wikitable sortable', 'constituents')
sp100 = getTickers(SP100, 'wikitable sortable', 'constituents')
ndx100 = getTickers(NDX100, 'wikitable sortable', 'constituents')

dow['ticker'] = dow['Symbol'].apply(lambda x: x.split(":")[-1].replace("\xa0",""))
sp500['ticker'] = sp500['Symbol']
sp100['ticker'] = sp100['Symbol']
ndx100['ticker'] = ndx100['Ticker']

# save files
dow.to_csv('dow30.csv', index=True)
sp500.to_csv('sp500.csv', index=True)
sp100.to_csv('sp100.csv', index=True)
ndx100.to_csv('ndx100.csv', index=True)

