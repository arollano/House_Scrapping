import requests
from bs4 import BeautifulSoup

def parseHTML(url):
    '''
    '''
    # Download url
    site = requests.get(url)

    # Parse using BS
    soup = BeautifulSoup(site.content, 'html')
    return(soup)

def getPisos(soup):
    '''
    '''
    # Return pisos list given by label
    return(soup.findAll("div", {"class": "row clearfix"}))

def cleanAttribute(attribute):
    '''
    Function to remove \r\n and blanc spaces from the attributes

    INPUT: attribute
    '''
    attribute = attribute.replace('\r\n', '')
    return(attribute.strip())

def getTypeAndRegion(path):
    '''
    Function to get the region and piso type from a path

    INPUT: path
    RETURN:
    - piso_type: piso, estudio, apartamento...
    - region: the region the house belongs to
    '''
    # Clean path
    path = path.replace('/venta/', '')
    path = path.replace('/', '')

    # Get type and region
    piso_type = path[:path.find('-')]
    region = path[path.find('-')+1:]
    return(piso_type, region)


def getPisosAttributesFromPage(pisos_html, path):
    '''
    Scrap main info for each 'piso' scrapped

    INPUT:
    - pisos: Parsed html objetct with all div class='row clearfix'
    - region: region where the piso is located

    RETURN: pisos. Array containing a dict for each house for sale
    - summary
    - description
    - location
    - photo
    - recomendado
    - price
    - offer
    - size
    - rooms
    - price per m2
    - num photos
    '''
    pisos = []

    for dev in pisos_html:
        piso = {}
        # Get main attributes
        piso['summary'] = cleanAttribute(dev.h3.a.text)
        piso['description'] = cleanAttribute(dev.find('div', {'class':'description'}).text)

        # Get location
        if (dev.find('div', {'class':'location'}) != None):
            piso['location'] = cleanAttribute(dev.find('div', {'class':'location'}).text)
        else:
            piso['location'] = ''

        # Get photos
        if (dev.find('img')['src'] != '/Images/assets/blank1x1.png' and dev.find('img')['src'] != None):
            piso['photo'] = dev.find('img')['src']
        elif (dev.find('img')['data-lazy'] == 'true'):
            piso['photo'] = dev.find('img')['data-lazy-img']

        # Get recomendado
        if (dev.find('div', {'class':'tag exclusivo'}) != None):
            piso['recomendado'] = cleanAttribute(dev.find('div', {'class':'tag exclusivo'}).text)
        else:
            piso['recomendado'] = ''

        # Get price
        piso['price'] = cleanAttribute(dev.find('div', {'class':'price'}).text)

        # Get size
        if (dev.find('div', {'class':'item'}) != None):
            piso['size'] = cleanAttribute(dev.find('div', {'class':'item'}).text)
        else:
            piso['size'] = ''

        # Get rooms if defined
        if (dev.find('div', {'class':'item', 'data-rooms':'true'}) != None):
            piso['rooms'] = cleanAttribute(dev.find('div', {'class':'item', 'data-rooms':'true'}).text)
        else:
            piso['rooms'] = ''

        piso['price/m2'] = ''

        # Get bathrooms
        if (dev.find('span', {'class': 'icon icoBath'}) != None):
            piso['bathrooms'] = cleanAttribute(dev.find('span', {'class': 'icon icoBath'}).parent.text)
        else:
            piso['bathrooms'] = ''

        # Get price per m2
        for item in dev.findAll('div', {'class':'item'}):
            if (item.text.find("€/m") != -1):
                piso['price/m2'] = cleanAttribute(item.text)

        # Get number of photos
        if (dev.find('div', {'class':'numPhotos'}) != None):
            piso['Num Photos'] = cleanAttribute(dev.find('div', {'class':'numPhotos'}).text)
        else:
            piso['Num Photos'] = ''

        # Get region and type
        piso['type'], piso['region'] = getTypeAndRegion(path)

        # Append to outcome
        pisos.append(piso)

    # Return array
    return(pisos)

def scanPath(domain, path):
    '''
    Given a path scan all pisos in the site as well as the next pages with the same search pattern

    INPUT: path. e.g. /venta/pisos-huelva/
    OUTPUT: object with all pisos found
    '''
    url = domain + path
    pisos = []

    # Parse site
    soup = parseHTML(url)

    # Scan pisos
    pisos_html = getPisos(soup)
    # Get pisos info
    pisos = getPisosAttributesFromPage(pisos_html, path)
    # Get next page
    next_page = soup.findAll('a', {'id':'lnkPagSig'})

    while len(next_page) != 0:
        for page in next_page:
            # Build  & parse url
            url = domain + page['href']
            soup = parseHTML(url)

            # Scan pisos
            pisos_html = getPisos(soup)
            # Get pisos info
            pisos = pisos + getPisosAttributesFromPage(pisos_html, path)

        # Get next page
        next_page = soup.findAll('a', {'id':'lnkPagSig'})

    return(pisos)

def getCitiesToScan(domain, start_path):
    '''
    This function gets a start path and scan all cities offered in the browser

    INPUT: path to search
    OUTPUT: list of cities given by their paths to scan
    '''
    url = domain + start_path
    soup = parseHTML(url)

    # Find all cities in the browser
    cities = soup.findAll('span', {'class':'black-link'})

    # Extract link
    paths = []
    for city in cities:
        page = city.a
        if page != None:
            paths.append(page['href'])

    return(paths)
