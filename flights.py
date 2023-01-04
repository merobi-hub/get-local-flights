# SPDX-License-Identifier: MIT

import time
from datetime import datetime, timezone, timedelta
import requests
import click
from rich.console import Console
from country_bounding_boxes import country_subunits_by_iso_code

console = Console(width=400, color_system="auto")

class Flights:

    def __init__(
        self, 
        area: str, 
        username: str, 
        password: str, 
        limit: int, 
        b: bool,
        t: bool,
        array: bool,
        lamin: str,
        lomin: str,
        lamax: str,
        lomax: str,
        iso: str
        ): 
        self.area = area 
        self.username = username 
        self.password = password 
        self.limit = limit 
        self.b = b
        self.t = t 
        self.array = array
        self.lamin = lamin
        self.lomin = lomin
        self.lamax = lamax
        self.lomax = lomax
        self.iso = iso
        self.bbox_data = {}
        self.aircraft_data = {}
        self.output_array = []        

    def get_flights(self):
        previous = 0
        count = 0
        try:
            while count < self.limit:
                if self.area == 'Barrington':
                    r = requests.get(
                        'https://opensky-network.org/api/states/all?lamin=41.708513&lomin=-71.363938&lamax=41.759753&lomax=-71.294243&extended=1',
                        auth = (self.username, self.password)
                    )
                elif self.area == 'Nayatt':
                    r = requests.get(
                        'https://opensky-network.org/api/states/all?lamin=41.711757&lomin=-71.338692&lamax=41.728606&lomax=-71.291314&extended=1',
                        auth = (self.username, self.password)
                    )
                elif self.area == 'NY':
                    r = requests.get(
                        'https://opensky-network.org/api/states/all?lamin=40.4961&lomin=-79.7621&lamax=45.0158&lomax=-71.8562&extended=1',
                        auth = (self.username, self.password)
                    )
                elif self.area == 'RI':
                    r = requests.get(
                        'https://opensky-network.org/api/states/all?lamin=41.146&lomin=-71.862&lamax=42.018&lomax=-71.120&extended=1',
                        auth = (self.username, self.password)
                    )
                elif self.b:
                    url = f'https://opensky-network.org/api/states/all?lamin={self.lamin}&lomin={self.lomin}&lamax={self.lamax}&lomax={self.lomax}&extended=1'
                    r = requests.get(
                        url,
                        auth = (self.username, self.password)   
                    )
                elif self.iso == 'USA':
                    bbox = [c.bbox for c in country_subunits_by_iso_code(self.iso)]
                    r = requests.get(
                        f'https://opensky-network.org/api/states/all?lamin={bbox[3][1]}&lomin={bbox[3][0]}&lamax={bbox[3][3]}&lomax={bbox[3][2]}&extended=1',
                        auth = (self.username, self.password)
                    )
                elif self.iso != 'USA':
                    bbox = [c.bbox for c in country_subunits_by_iso_code(self.iso)]
                    r = requests.get(
                        f'https://opensky-network.org/api/states/all?lamin={bbox[0][1]}&lomin={bbox[0][0]}&lamax={bbox[0][3]}&lomax={bbox[0][2]}&extended=1',
                        auth = (self.username, self.password)
                    )
                self.bbox_data = r.json()
                if self.bbox_data['states']:
                    for i in self.bbox_data['states']:
                        b = datetime.now(timezone.utc) - timedelta(seconds = 86400)
                        e = datetime.now(timezone.utc)
                        begin = int(time.mktime(b.timetuple()))
                        end = int(time.mktime(e.timetuple()))
                        try:
                            r = requests.get(
                                f'https://opensky-network.org/api/flights/aircraft?icao24={i[0]}&begin={begin}&end={end}', 
                                auth = (self.username, self.password)
                            )
                            r.raise_for_status()
                        except requests.exceptions.HTTPError:
                            continue
                        self.aircraft_data = r.json()
                        if self.t:
                            self.to_terminal()
                        if self.array:
                            self.to_array()
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
            if self.array:
                self.return_array()
            exit()

    def to_terminal(self):
        for i in self.bbox_data['states']:
            print('=====================')
            print('Callsign: ', self.aircraft_data[0]['callsign'])
            print('True track: ', i[10], ' degrees')
            print('Barometric altitude: ', i[7], ' m')
            print('Geometric altitude: ', i[13], ' m')
            print('Ground velocity: ', i[9], ' m/s')
            print('Departure airport: ', self.aircraft_data[0]['estDepartureAirport'])
            print('Arrival airport: ', self.aircraft_data[0]['estArrivalAirport'])
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

    def to_array(self):
        ifo = {}
        if self.bbox_data['states']:
            for i in self.bbox_data['states']:
                ifo['callsign'] = self.aircraft_data[0]['callsign']
                ifo['true track (degrees)'] = i[10]
                ifo['barometric altitude (m)'] = i[7]
                ifo['geometric altitude (m)'] = i[13]
                ifo['ground velocity (m/s)'] = i[9]
                ifo['departure airport'] = self.aircraft_data[0]['estDepartureAirport']
                ifo['arrival airport'] = self.aircraft_data[0]['estArrivalAirport']
                if i[-1] == 4:
                    ifo['category'] = 'Large (75-300K lbs)'
                if i[-1] == 3:
                    ifo['category'] = 'Small (15.5K - 75K lbs)'
                if i[-1] == 1:
                    ifo['category'] = 'No info'
                if i[-1] == 6:
                    ifo['category'] = 'Heavy (> 300K lbs)'
                if i[-1] == 8:
                    ifo['category'] = 'Rotorcraft'
                if i[-1] == 2:
                    ifo['category'] = 'Light (< 15.5K lbs)'
                if i[-1] == 5:
                    ifo['category'] = 'High Vortex Large'
                ifo['SPI'] = i[15]
                self.output_array.append(ifo)
    
    def return_array(self):
        print('Returning array of flights found...')
        print(self.output_array)
        print('Done!')
        return self.output_array

@click.command()
@click.option(
    '--area',
    help=
    """
    Area options: Barrington, Nayatt, RI, NY
    """
)
@click.option(
    '--username',
    help=
    """
    OpenSky username
    """,
    required=True
)
@click.option(
    '--password',
    help=
    """
    OpenSky password
    """,
    required=True
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
    '-b',
    is_flag=True,
    help=
    """
    Floats for '--lamin', '--lomin', '--lamax', '--lomax' required if used. See 
    https://openskynetwork.github.io/opensky-api/rest.html for an example query 
    with a bounding box. Use a tool such as http://bboxfinder.com/ to get bbox 
    coordinates via a map-based GUI.
    """
)
@click.option(
    '-t',
    is_flag=True,
    help=
    """
    Prints flights to terminal if set.
    """,
    default=bool(False)
)
@click.option(
    '-array',
    is_flag=True,
    help=
    """
    If set to False, an array of all flights will not be returned.
    """,
    default=bool(True)
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
    '--iso',
    help=
    """
    For a list of ISO codes, see: https://www.nationsonline.org/oneworld/country_code_list.htm.
    """
)

def main(
    area: str,
    username: str,
    password: str,
    limit: int,
    b: bool,
    t: bool,
    array: bool,
    lamin: str,
    lomin: str,
    lamax: str,
    lomax: str,
    iso: str
    ):
    print(
      """
        @@@@@@@@@@ @@@@     @@@@@ @@@@@@@@@ @@@@ @@@@ @@@@@@@@@@ @@@@@@@@@@@@
       @@@@@@@@@@ @@@@     @@@@@ @@@   @@@ @@@@ @@@@ @@@@@@@@@@ @@@@@@@@@@@
      @@@@@      @@@@     @@@@@ @@@       @@@@@@@@@    @@@@    @@@@@
     @@@@@@@@   @@@@     @@@@@ @@@  @@@@ @@@@@@@@@    @@@@      @@@@@
  @@@@@@@      @@@@@@@@ @@@@@ @@@@   @@ @@@@ @@@@    @@@@   @@@@@@@@@@
@@@@@@@@      @@@@@@@@ @@@@@ @@@@@@@@@ @@@@ @@@@    @@@@   @@@@@@@@@@
____________________________________________________________________  
IFOs in your bounding box from the OpenSky API
Copyright 2022-2023 Michael Robinson | MIT License
      """
    )
    with console.status('working...', spinner='aesthetic'):
        f = Flights(
            area=area, 
            username=username, 
            password=password, 
            limit=limit, 
            b=b,
            t=t,
            array=array,
            lamin=lamin,
            lomin=lomin,
            lamax=lamax,
            lomax=lomax,
            iso=iso
            )
        f.get_flights()
        if array:
            f.return_array()

if __name__ == "__main__":
    main()