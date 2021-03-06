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
        row = str(id) + ','
        url = f'https://www.gunviolencearchive.org/incident/{id}'
        soup = soup_opener(url)
        row += soup_eater(soup)
        # print(row)
        soup_pooper(row)

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
    data += scrape_location(main_divs)
    if 'Guns Involved' in h2s:
        data += scrape_guns(main_divs)
    else:
        data += ',,'
    if 'Incident Characteristics' in h2s:
        data += scrape_characteristics(main_divs)
    else:
        data += ','
    if 'Notes' in h2s:
        data += scrape_notes(main_divs)
    else:
        data += ','
    if 'Participants' in h2s:
        data += scrape_participants(main_divs)
    else:
        data += ',,,,,,,,'
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

def scrape_location(main_divs):
    '''
    soup_eater calls this to scrape the location data

    Specifically it gets:
        * Misc. location notes
        * Address
        * City & State
        * Lat/Lon
    '''
    for div in main_divs:
        div_h2s = [h2.text for h2 in div.find_all('h2')]
        if 'Location' in div_h2s:
            spans = [span.text for span in div.find_all('span')]

    # Loc. Description
    if len(spans) == 4:
        data = spans[0] + ','
    else:
        data = ','
    # Address
    data += spans[-3] + ','
    # City/State
    city = spans[-2].split(', ')[0]
    state = spans[-2].split(', ')[1]
    data += city + ',' + state  + ','
    # Lat/Lon
    lat = spans[-1].split()[1].strip(',')
    lon = spans[-1].split()[2]
    data += lat + ',' + lon + ','

    return data

def scrape_participants(main_divs):
    '''
    parser calls this to scrape information about the participant(s)

    For each participant, the scraper will gather type and status and look for
    additional data points like name, age, age group, and gender
    '''
    # Get the list items with the data
    for div in main_divs:
        div_h2s = [h2.text for h2 in div.find_all('h2')]
        if 'Participants' in div_h2s:
            list_items = [li.text for li in div.find_all('li')]

    # Pull data out of list_items
    cols = ['type', 'status', 'name', 'age', 'age_group', 'gender']
    data = [['' for col in cols]]
    part_df = pd.DataFrame(data=data, columns=cols)
    for item in list_items:
        trait = item.split(': ')[0].lower().replace(' ', '_')
        if trait == 'relationship': # opting not to scrape this data, too sparse
            continue
        value = item.split(': ')[1]
        value = value.replace(',', ';')
        if part_df[trait][0] != '':
            value = '||' + value
        part_df[trait] += value

    # Count number of injured and killed
    statuses = part_df['status'].iloc[0].split('||')
    statuses = [status.lower() for status in statuses]
    n_killed = str(statuses.count('killed'))
    n_injured = str(statuses.count('injured'))

    # Assemble row
    data = part_df.values.astype(str)[0]
    data = ','.join(data) + ','
    data = n_killed + ',' + n_injured + ',' + data

    return data

def scrape_guns(main_divs):
    '''
    parser calls this to scrape the type and stolen status of each gun
    recorded
    '''
    # Get the list items with the data
    for div in main_divs:
        div_h2s = [h2.text for h2 in div.find_all('h2')]
        if 'Guns Involved' in div_h2s:
            list_items = [li.text for li in div.find_all('li')]

    # Pull data out of list_items
    cols = ['type', 'stolen']
    data = [['' for col in cols]]
    gun_df = pd.DataFrame(data=data, columns=cols)
    for item in list_items:
        trait = item.split(': ')[0].lower().replace(' ', '_')
        value = item.split(': ')[1]
        if trait:
            '||' + value
        gun_df[trait] += value

    data = gun_df.values.astype(str)[0]
    data = ','.join(data) + ','

    return data


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
    list_items = '||'.join(list_items)
    list_items = list_items.replace(',', ';')
    return list_items + ','

def scrape_notes(main_divs):
    '''
    parser calls this to scrape the hand written notes of the incident
    '''
    for div in main_divs:
        if 'Notes' in [h2.text for h2 in div.find_all('h2')]:
            note_text = div.find('p').text
            note_text = note_text.replace(',', ';')
            note_text = note_text.replace('\n', '')
    return note_text + ','

def scrape_sources(main_divs):
    '''
    parser calls this to scrape the urls of the news links
    '''
    for div in main_divs:
        if 'Sources' in [h2.text for h2 in div.find_all('h2')]:
            sources = []
            for link in div.find_all('a'):
                sources.append(link.get('href'))
    # Wrap it in quotes, otherwise the commas will cause problems
    sources = ['"' + source + '"' for source in sources]
    return '||'.join(sources)

def soup_pooper(row):
    '''
    Takes in the entire line as a string and writes it to the filename

    Also checks if the csv file exists, if not, it makes it with the right
    column names
    '''
    pathname = '../data/'
    filename = 'id_data.csv'
    # checks if the csv exists
    col_names = ['incident_id', 'date', 'location_description', 'address', 'city', 'state', 'lat', 'lon', 'gun_types', 'gun_stolen', 'incident_characteristics',  'notes', 'n_killed', 'n_injured', 'participant_type', 'participant_status', 'participant_name', 'participant_age', 'participant_age_group', 'participant_gender', 'sources']
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
