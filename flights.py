# SPDX-License-Identifier: MIT

import time
from datetime import datetime, timezone, timedelta
import requests
import click
from rich.console import Console
from country_bounding_boxes import country_subunits_by_iso_code

console = Console(width=400, color_system="auto")

def get_flights(
    area: str, 
    username: str, 
    password: str, 
    limit: int, 
    bbox: bool,
    lamin: float,
    lomin: float,
    lamax: float,
    lomax: float,
    country: bool,
    iso: str
):
    previous = 0
    count = 0
    try:
        while count <= limit:
            if area == 'Barrington':
                r = requests.get(
                    'https://opensky-network.org/api/states/all?lamin=41.708513&lomin=-71.363938&lamax=41.759753&lomax=-71.294243&extended=1',
                    auth = (username, password)
                )
            if area == 'Nayatt':
                r = requests.get(
                    'https://opensky-network.org/api/states/all?lamin=41.711757&lomin=-71.338692&lamax=41.728606&lomax=-71.291314&extended=1',
                    auth = (username, password)
                )
            if area == 'NY':
                r = requests.get(
                    'https://opensky-network.org/api/states/all?lamin=40.4961&lomin=-79.7621&lamax=45.0158&lomax=-71.8562&extended=1',
                    auth = (username, password)
                )
            if area == 'RI':
                r = requests.get(
                    'https://opensky-network.org/api/states/all?lamin=41.146&lomin=-71.862&lamax=42.018&lomax=-71.120&extended=1',
                    auth = (username, password)
                )
            if bbox:
                r = requests.get(
                    f'https://opensky-network.org/api/states/all?lamin={lamin}&lomin={lomin}&lamax={lamax}&lomax={lomax}&extended=1',
                    auth = (username, password)
                )
            if country:
                if iso == 'USA':
                    bbox = [c.bbox for c in country_subunits_by_iso_code(iso)]
                    r = requests.get(
                        f'https://opensky-network.org/api/states/all?lamin={bbox[3][1]}&lomin={bbox[3][0]}&lamax={bbox[3][3]}&lomax={bbox[3][2]}&extended=1',
                        auth = (username, password)
                    )
                else:
                    bbox = [c.bbox for c in country_subunits_by_iso_code(iso)]
                    r = requests.get(
                        f'https://opensky-network.org/api/states/all?lamin={bbox[0][1]}&lomin={bbox[0][0]}&lamax={bbox[0][3]}&lomax={bbox[0][2]}&extended=1',
                        auth = (username, password)
                    )
            r.raise_for_status()
            data = r.json()
            if data['states']:
                for i in data['states']:
                    b = datetime.now(timezone.utc) - timedelta(seconds = 86400)
                    e = datetime.now(timezone.utc)
                    begin = int(time.mktime(b.timetuple()))
                    end = int(time.mktime(e.timetuple()))
                    r = requests.get(
                        f'https://opensky-network.org/api/flights/aircraft?icao24={i[0]}&begin={begin}&end={end}', 
                        auth = (username, password)
                    )
                    r.raise_for_status()
                    data = r.json()
                    print('=====================')
                    print('Callsign: ', data[0]['callsign'])
                    print('True track: ', i[10], ' degrees')
                    print('Barometric altitude: ', i[7], ' m')
                    print('Geometric altitude: ', i[13], ' m')
                    print('Ground velocity: ', i[9], ' m/s')
                    print('Departure airport: ', data[0]['estDepartureAirport'])
                    print('Arrival airport: ', data[0]['estArrivalAirport'])
                    if i[-1] == 4:
                        print('Category: Large (75-300K lbs)')
                    if i[-1] == 3:
                        print('Category: Small (15.5K - 75K lbs)')
                    if i[-1] == 1:
                        print('Category: No info')
                    if i[-1] == 6:
                        print('Category: Heavy (> 300K lbs)')
                    if i[-1] == 8:
                        print('Category: Rotorcraft')
                    if i[-1] == 2:
                        print('Category: Light (< 15.5K lbs)')
                    if i[-1] == 5:
                        print('Category: High Vortex Large')
                    print('SPI? ', i[15])
                    print('=====================')
                previous = 1
                count += 1
                now = datetime.now().strftime("%H:%M:%S")
                print('Pausing at ' + now + ' for 5s...')
                time.sleep(5)
            else:
                if previous == 0 and count > 0:
                    time.sleep(5)
                elif previous == 0 and count == 0:
                    now = datetime.now().strftime("%H:%M:%S")
                    print('No flights found in airspace since ', now)
                    time.sleep(5)
                elif previous == 1:
                    now = datetime.now().strftime("%H:%M:%S")
                    print('No flights found in airspace since ', now)
                    time.sleep(5)
                previous = 0
                count += 1
    except KeyboardInterrupt:
        exit()

@click.command()
@click.option(
    '--area',
    help=
    """
    Area options: Barrington, Nayatt, RI, NY
    """,
    default=str('Barrington')
)
@click.option(
    '--username',
    help=
    """
    OpenSky username
    """
)
@click.option(
    '--password',
    help=
    """
    OpenSky password
    """
)
@click.option(
    '--limit',
    help=
    """
    API request limit: integer up to 1000
    """,
    default=int(1000)
)
@click.option(
    '--bbox',
    help=
    """
    Boolean. Floats for '--lamin', '--lomin', '--lamax', '--lomax' required if 
    'True'. See https://openskynetwork.github.io/opensky-api/rest.html for an 
    example query with a bounding box. Use a tool such as http://bboxfinder.com/ 
    to get bbox coordinates via a map-based GUI.
    """,
    default=bool(False)
)
@click.option(
    '--lamin'
)
@click.option(
    '--lomin'
)
@click.option(
    '--lamax'
)
@click.option(
    '--lomax'
)
@click.option(
    '--country',
    help=
    """
    Boolean. ISO code string required if 'True' and country other than USA desired.
    For a list of ISO codes, see: https://www.nationsonline.org/oneworld/country_code_list.htm.
    """,
    default=bool(False)
)
@click.option(
    '--iso',
    default=str('USA')
)

def main(
    area: str,
    username: str,
    password: str,
    limit: int,
    bbox: bool,
    lamin: float,
    lomin: float,
    lamax: float,
    lomax: float,
    country: bool,
    iso: str
):
    print(
      """
              @@@@@@@@@@ @@@@     @@@@@ @@@@@@@@@ @@@@ @@@@ @@@@@@@@@ @@@@@@@@@@@@
             @@@@@@@@@@ @@@@     @@@@@ @@@   @@@ @@@@ @@@@ @@@@@@@@@ @@@@@@@@@@@
            @@@@@      @@@@     @@@@@ @@@       @@@@@@@@@    @@@@   @@@@@
           @@@@@@@@@@ @@@@     @@@@@ @@@  @@@@ @@@@@@@@@    @@@@     @@@@@
        @@@@@@@      @@@@@@@@ @@@@@ @@@@   @@ @@@@ @@@@    @@@@  @@@@@@@@@@
      @@@@@@@@      @@@@@@@@ @@@@@ @@@@@@@@@ @@@@ @@@@    @@@@  @@@@@@@@@@
        
      IFOs in your bounding box from the OpenSky API
      By Michael Robinson
      MIT License
      """
    )
    with console.status('working...', spinner='aesthetic'):
        get_flights(
            area=area, 
            username=username, 
            password=password, 
            limit=limit, 
            bbox=bbox,
            lamin=lamin,
            lomin=lomin,
            lamax=lamax,
            lomax=lomax,
            country=country,
            iso=iso
        )

if __name__ == "__main__":
    main()