from opensky_api import OpenSkyApi
import time
from datetime import datetime, timezone, timedelta
import requests
from requests.auth import HTTPBasicAuth
import click 
import rich_click

def get_flights(area: str, username: str, password: str):
    ok = 1
    previous = 0
    count = 0
    while ok:
        if area == 'Barrington':
            r = requests.get(
                f'https://opensky-network.org/api/states/all?lamin=41.708513&lomin=-71.363938&lamax=41.759753&lomax=-71.294243&extended=1',
                auth = (username, password)
            )
        if area == 'Nayatt':
            r = requests.get(
                f'https://opensky-network.org/api/states/all?lamin=41.711757&lomin=-71.338692&lamax=41.728606&lomax=-71.291314&extended=1',
                auth = (username, password)
            )
        if area == 'NY':
            r = requests.get(
                f'https://opensky-network.org/api/states/all?lamin=40.4961&lomin=-79.7621&lamax=45.0158&lomax=-71.8562&extended=1',
                auth = (username, password)
            )
        if area == 'RI':
            r = requests.get(
                f'https://opensky-network.org/api/states/all?lamin=41.146&lomin=-71.862&lamax=42.018&lomax=-71.120&extended=1',
                auth = (username, password)
            )
        if area == '55 Adams':
            r = requests.get(
                f'https://opensky-network.org/api/states/all?lamin=41.723676&lomin=-71.295256&lamax=41.724649&lomax=-71.294682&extended=1',
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
                    print('Category: Helicopter')
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
            count += 1

@click.command()
@click.option(
    '--area',
    help=
    """
    Area options: 55 Adams, Barrington, Nayatt, RI, NY
    """,
    default=str('Barrington')
)
@click.option(
    '--username'
)
@click.option(
    '--password'
)

def main(
    area: str,
    username: str,
    password: str
):
    get_flights(area=area, username=username, password=password)

if __name__ == "__main__":
    main()