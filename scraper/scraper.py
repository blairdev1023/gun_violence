import requests
import csv
from bs4 import BeautifulSoup
import time
import pandas as pd
import numpy as np
import sys

def scrape(idx):
    '''
    returns the soup from the indexed url
    '''
    url = f'https://www.gunviolencearchive.org/incident/{idx}'
    try:
        printout(f'Trying a request on {idx}')
        page = requests.get(url, timeout=1)
        return BeautifulSoup(page.text, 'html.parser')
    except requests.exceptions.SSLError:
        now = round(time.time() - start)
        print(f'SSLError on {idx}, trying again......', now)
        return scrape(idx)
    except requests.exceptions.ChunkedEncodingError:
        now = round(time.time() - start)
        print(f'ChunkedEncodingError on {idx}, trying again...', now)
        return scrape(idx)
    except requests.exceptions.ConnectionError:
        now = round(time.time() - start)
        print(f'Oops! Lost Connection on {idx}, trying again...', now)
        return scrape(idx)
    except requests.exceptions.ReadTimeout:
        return scrape(idx)

def printout(message):
    '''
    Prints the message and the time. Carriage reset makes this line get
    overwritten when a normal 'print' is called. These messages are for
    the status of the scraper
    '''
    now = round(time.time() - start)
    message = ' ' + message + '\tTime: ' + str(now)
    sys.stdout.write(message)
    sys.stdout.flush()
    sys.stdout.write('\r')
    sys.stdout.flush()

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
    page_idxs = []
    for idx in range(lower_bound, upper_bound):
        if idx % 100 == 0:
            now = round(time.time() - start)
            print(str(idx)[:3], len(page_idxs), now, ' ' * 30)
            # extra spaces to overwrite the printout    ^^^^^
        soup = scrape(idx)
        page_found = (soup.h1.text != '\nPage not found\n')
        if page_found:
            page_idxs.append(idx)
        # Save every 1000
        if (idx % 1000 == 0) & (idx != lower_bound):
            save(page_idxs, idx)
            page_idxs = []
    save(page_idxs, upper_bound)
    print(len(page_idxs), time.time() - start, ' ' * 30)
    # extra spaces to overwrite the printout    ^^^^^

if __name__ == '__main__':
    start = time.time()
    check_idxs(318000, 350000)
