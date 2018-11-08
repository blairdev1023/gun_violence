import requests
import csv
from bs4 import BeautifulSoup
import time
import pandas as pd
import numpy as np

def scrape(idx):
    '''
    returns the soup from the indexed url
    '''

    url = f'https://www.gunviolencearchive.org/incident/{idx}'
    try:
        page = requests.get(url)
        return BeautifulSoup(page.text, 'html.parser')
    except requests.exceptions.SSLError:
        print(f'SSLError on {idx}, trying again...', time.time() - start)
        return scrape(idx)
    except requests.exceptions.ChunkedEncodingError:
        print(f'ChunkedEncodingError on {idx}, waiting 10 seconds...')
        print(time.time() - start)
        time.sleep(10)
        print('Starting Again!')
        return scrape(idx)
    except requests.exceptions.ConnectionError:
        print(f'Oops! Lost Connection on {idx}, waiting 10 seconds...')
        print(time.time() - start)
        time.sleep(10)
        print('Starting Again!')
        return scrape(idx)

def save(page_idxs, idx):
    '''
    simple save
    '''
    thousand = str(idx)[:3]
    pathname = f'../data/known_ids/scrape_{thousand}.csv'
    series = pd.Series(page_idxs, name='ids')
    series.to_csv(pathname, index=False, header='ids')

def check_idxs(lower_bound, upper_bound):
    '''
    returns a list of the incident indices between the bounds
    '''

    start = time.time()
    page_idxs = []
    for idx in range(lower_bound, upper_bound):
        if idx % 100 == 0:
            print(idx - lower_bound, len(page_idxs), time.time() - start)
        soup = scrape(idx)
        if soup.h1.text != '\nPage not found\n':
            page_idxs.append(idx)
        # Save every 1000
        if (idx % 1000 == 0) & (idx != lower_bound):
            save(page_idxs, idx)
            page_idxs = []
    save(page_idxs, upper_bound)
    print(len(page_idxs), time.time() - start)

if __name__ == '__main__':
    check_idxs(200000, 250000)
