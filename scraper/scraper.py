import os
import csv
import sys
import time
import requests
from bs4 import BeautifulSoup
from multiprocessing import Pool, cpu_count

def open_soup(url):
    '''
    using the url requests the page and returns the soup and the status code
    '''
    idx = int(url.split('/')[-1])
    try:
        printout(f'Trying a request on {idx}')
        page = requests.get(url, timeout=10)
        return BeautifulSoup(page.text, 'html.parser'), page.status_code
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
    the live status of the scraper
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
    filename = 'scraped_ids.csv'
    # checks if the csv exists
    if filename not in os.listdir(pathname):
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
    idx = int(url.split('/')[-1])
    soup, status_code = open_soup(url)
    if status_code == 200:
        save(idx)
    elif status_code == 404:
        pass
    elif status_code == 403:
        pass
    else:
        check_idx(url)

if __name__ == '__main__':
    start = time.time()
    urls = []
    for idx in range(1, 100000):
        urls.append(f'https://www.gunviolencearchive.org/incident/{idx}')
    with Pool(cpu_count()) as p:
        p.map(check_idx, urls)
    print('Done!', round(time.time() - start))
