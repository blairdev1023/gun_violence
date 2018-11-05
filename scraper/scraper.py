import requests
import csv
from bs4 import BeautifulSoup
import time
import pandas as pd
import numpy as np

def check_idxs(lower_bound, upper_bound):
    '''
    returns a list of the incident indices between the bounds
    '''
    page_idxs = []
    for idx in range(lower_bound, upper_bound):
        if idx % 100 == 0:
            time.sleep(1)
            print(idx - lower_bound, len(page_idxs))
        url = f'https://www.gunviolencearchive.org/incident/{idx}'
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        if soup.h1.text != '\nPage not found\n':
            page_idxs.append(idx)
    return page_idxs

if __name__ == '__main__':
    start = time.time()
    page_idxs = check_idxs(130000, 140000)
    print(time.time() - start)
