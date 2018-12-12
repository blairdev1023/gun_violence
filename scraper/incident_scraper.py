import os
import csv
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd

def main_controller(lower, upper):
    '''
    Controls the script. First it will fetch the indices between the specified bounds - inclusively. Then for each index gets it page returns its soup (soup_opener), retrieves the data available from the soup (soup_eater), and writes that string to a csv (soup_pooper)
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
    Rescursive controller for opening the soup. A lot of the time the first scrape doesn't work so it needs to be done until it is!

    Returns soup
    '''
    idx = int(url.split('/')[-1])
    soup, status_code = opener(url)
    if status_code == 200:
        return soup
    else:
        return soup_opener(url)

def opener(url):
    '''
    Returns the soup and status code from the url
    '''
    idx = int(url.split('/')[-1])
    try:
        page = requests.get(url, timeout=10)
        return BeautifulSoup(page.text, 'html.parser'), page.status_code
    except requests.exceptions.SSLError:
        now = round(time.time() - start)
        print(f'SSLError on {idx}, trying again......', now)
        return opener(url)
    except requests.exceptions.ChunkedEncodingError:
        now = round(time.time() - start)
        print(f'ChunkedEncodingError on {idx}, trying again...', now)
        return opener(url)
    except requests.exceptions.ConnectionError:
        now = round(time.time() - start)
        print(f'Oops! Lost Connection on {idx}, trying again...', now)
        return opener(url)
    except requests.exceptions.ReadTimeout:
        return opener(url)

def soup_eater(soup):
    '''
    Main parser of the soup. Checks to see what is in the soup (gun types, notes, etc...) and tasks helper functions with extracting the data. All the helper functions this calls start with "scrape"
    '''
    # This div has all the data in it
    main_divs = soup.find('div', {'id': 'block-system-main'}).select('div')
    # Headers to check what's in page
    h2s = [h2.text for h2 in soup.find_all('h2')]

    data = scrape_header(soup)
    data += scrape_location(soup)
    if 'Incident Characteristics' in h2s:
        data += scrape_characteristics(main_divs)
    else:
        data += ','
    if 'Notes' in h2s:
        data += scrape_notes(main_divs)
    else:
        data += ','
    if 'Sources' in h2s:
        data += scrape_sources(main_divs)
    else:
        data += ','

    return data

def scrape_header(soup):
    '''
    parser calls this to scrape the header of the site

    The only data point retrieved is the date
    '''
    tag = soup.find_all('h1')[-1].text
    date = tag.split()[0]
    return date + ','

def scrape_location(soup):
    '''
    soup_eater calls this to scrape the location data

    Specifically it gets:
        * Misc. location notes
        * Address
        * City & State
        * Lat/Lon
    '''
    n_spans = len(soup.find_all('span')) # IMPORTANT!
    # if n_spans is 7 then no location description
    spans = [span.text for span in soup.find_all('span')]

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

def scrape_characteristics(main_divs):
    '''
    parser calls this to scrape all of the characteristics about the
    incident. Examples: "Shot - Wounded/Injured", "Assault weapon",
    "Accidental/Negligent Discharge"

    I have noticed these characteristics are inconsistent at best so take them
    with a lot of salt.
    '''
    for div in main_divs:
        div_h2s = [h2.text for h2 in div.find_all('h2')]
        if 'Incident Characteristics' in div_h2s:
            list_items = [li.text for li in div.find_all('li')]
    return '||'.join(list_items) + ','

def scrape_notes(main_divs):
    '''
    parser calls this to scrape the hand written notes of the incident
    '''
    for div in main_divs:
        if 'Notes' in [h2.text for h2 in div.find_all('h2')]:
            note_text = div.find('p').text
    return note_text.replace(',', ';') + ','

def scrape_gun_types():
    '''
    parser calls this to scrape the type and stolen status of each gun
    recorded
    '''
    pass

def scrape_sources(main_divs):
    '''
    parser calls this to scrape the urls of the news links
    '''
    for div in main_divs:
        if 'Sources' in [h2.text for h2 in div.find_all('h2')]:
            sources = []
            for link in div.find_all('a'):
                sources.append(link.get('href'))
    return '||'.join(sources) + ','

def soup_pooper(row):
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
        'gun_types', 'incident_characteristics',  'notes',
        'participant_type', 'participant_status', 'participant_name',
        'participant_age', 'participant_age_group', 'participant_gender',
        'sources']
    if filename not in os.listdir(pathname):
        with open(pathname+filename, 'w') as f:
            f.write(','.join(col_names))
            f.write('\n')
    # this is the save
    with open(pathname+filename, 'a') as f:
        f.write(row)
        f.write('\n')

if __name__ == '__main__':
    lower =200000
    upper =200500
    main_controller(lower, upper)
