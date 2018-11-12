import os
import csv
import sys
import time
import requests
from bs4 import BeautifulSoup
from multiprocessing import Pool, cpu_count

def open_soup(url):
    '''
    returns the soup from the url
    '''
    idx = int(url[-6:])
    try:
        printout(f'Trying a request on {idx}')
        page = requests.get(url, timeout=2)
        return BeautifulSoup(page.text, 'html.parser')
    except requests.exceptions.SSLError:
        now = round(time.time() - start)
        print(f'SSLError on {idx}, trying again......', now)
        return open_soup(url)
    except requests.exceptions.ChunkedEncodingError:
        now = round(time.time() - start)
        print(f'ChunkedEncodingError on {idx}, trying again...', now)
        return open_soup(url)
    except requests.exceptions.ConnectionError:
        now = round(time.time() - start)
        print(f'Oops! Lost Connection on {idx}, trying again...', now)
        return open_soup(url)
    except requests.exceptions.ReadTimeout:
        return open_soup(url)

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

def save(idx):
    '''
    simple save
    '''
    pathname = '../data/known_ids/'
    filename = 'scraped.csv'
    # checks if the csv exists
    if 'scraped.csv' not in os.listdir(pathname):
        with open(pathname+filename, 'w') as f:
            f.write('ids')
            f.write('\n')
    # this is the save
    with open(pathname+filename, 'a') as f:
        f.write(str(idx))
        f.write('\n')

def check_idx(url):
    '''
    main function, saves the index if it finds a page
    '''
    idx = int(url[-6:])
    soup = open_soup(url)
    if soup.h1.text == '\nIncident\n':
        save(idx)
    elif soup.h1.text == '\nPage not found\n':
        pass
    else:
        check_idx(url)

if __name__ == '__main__':
    start = time.time()
    urls = []
    for idx in range(200000, 202000):
        urls.append(f'https://www.gunviolencearchive.org/incident/{idx}')
    with Pool(cpu_count()) as p:
        p.map(check_idx, urls)
