import requests
import csv
from bs4 import BeautifulSoup
import time
import pandas as pd
import numpy as np

def scrape(idx):
    '''
    returns the soup form the url
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

def check_idxs(page_idxs, lower_bound, upper_bound):
    '''
    returns a list of the incident indices between the bounds
    '''
    for idx in range(lower_bound, upper_bound):
        if idx % 100 == 0:
            time.sleep(1)
            print(idx - lower_bound, len(page_idxs), time.time() - start)
        soup = scrape(idx)
        if soup.h1.text != '\nPage not found\n':
            page_idxs.append(idx)
    return page_idxs

if __name__ == '__main__':
    start = time.time()
    page_idxs = []
    page_idxs = check_idxs(page_idxs, 130000, 140000)
    print(len(page_idxs), time.time() - start)
