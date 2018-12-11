import os
import csv
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd

def main_controller(lower, upper):
    '''
    Controls the script. First it will fetch the indices between the specified bounds - inclusively. Then for each index gets it page returns its soup (soup_opener), retrieves the data available from the soup (soup_eater), and writes that string to a csv (csv_writer, duh...)
    '''
    ids = pd.read_csv('../data/assembled_ids.csv')['ids']

    ids = ids[ids >= lower]
    ids = ids[ids <= upper]

    for id in ids:
        print(id)
        url = f'https://www.gunviolencearchive.org/incident/{id}'
        soup = soup_opener(url)
        row = soup_eater(soup)
        print(row)

def soup_opener(url):
    '''
    Returns the soup from the url
    '''
    idx = int(url.split('/')[-1])
    try:
        page = requests.get(url, timeout=10)
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

def soup_eater(soup):
    '''
    Main parser of the soup. Checks to see what is in the soup (gun types, notes, etc...) and tasks helper functions with extracting the data. All the helper functions this calls start with "scrape"
    '''
    h2s = [str(h2) for h2 in soup.find_all('h2')]
    h2s = [h2.replace('<h2>', '').replace('</h2>', '') for h2 in h2s]
    data = scrape_header(soup)
    data += scrape_location(soup)

    return data

def scrape_header(soup):
    '''
    parser calls this to scrape the header of the site

    The only data point retrieved is the date
    '''
    tag = soup.find_all('h1')[-1]
    tag = str(tag).replace('<h1>', '').replace('</h1>', '')
    date = tag.split()[0]
    return date + ','

def scrape_location(soup):
    '''
    parser calls this to scrape the location

    Specifically it gets:
        * Misc. location notes
        * Address
        * City & State
        * Lat/Lon
    '''
    n_spans = len(soup.find_all('span')) # IMPORTANT!
    # if n_spans is 7 then no location description
    spans = [str(span) for span in soup.find_all('span')]
    spans = [span.replace('<span>','').replace('</span>','') for span in spans]

    # City/State
    city = spans[-3].split(', ')[0]
    state = spans[-3].split(', ')[1]
    data = city + ',' + state  + ','

    # Loc. Description
    if n_spans == 7:
        data += ','
    else:
        data = spans[3] + ','
    # Address
    data += spans[-4] + ','
    # Lat/Lon
    lat = spans[-2].split()[1].strip(',')
    lon = spans[-2].split()[2]
    data += lat + ',' + lon + ','

    return data

def scrape_participants():
    '''
    parser calls this to scrape information about the participant(s)

    For each participant, the scraper will gather type and status and look for
    additional data points like name, age, age group, and gender
    '''
    pass

def scrape_characteristics():
    '''
    parser calls this to scrape all of the characteristics about the
    incident. Examples: "Shot - Wounded/Injured", "Assault weapon",
    "Accidental/Negligent Discharge"

    I have noticed these characteristics are inconsistent at best so take them
    with a lot of salt.
    '''
    pass

def scrape_notes():
    '''
    parser calls this to scrape the hand written notes of the incident
    '''
    pass

def scrape_gun_types():
    '''
    parser calls this to scrape the type and stolen status of each gun
    recorded
    '''
    pass

def scrape_sources():
    '''
    parser calls this to scrape the urls of the news links
    '''
    pass

def csv_writer():
    '''
    Takes in the entire line as a string and writes it to the filename

    Also checks if the csv file exists, if not, it makes it with the right
    column names
    '''
    pathname = '../data/'
    filename = 'id_data.csv'
    # checks if the csv exists
    col_names = ['incident_id', 'date', 'city', 'state', 'address',
        'location_description',  'lat', 'lon', 'n_killed', 'n_injuered',
        'gva_url', 'gun_types', 'incident_characteristics',  'notes',
        'participant_type', 'participant_status', 'participant_name',
        'participant_age', 'participant_age_group', 'participant_gender',
        'sources']
    if filename not in os.listdir(pathname):
        with open(pathname+filename, 'w') as f:
            f.write('ids')
            f.write('\n')
    # this is the save
    with open(pathname+filename, 'a') as f:
        f.write(str(idx))
        f.write('\n')

if __name__ == '__main__':
    lower =200000
    upper =200100
    main_controller(lower, upper)
