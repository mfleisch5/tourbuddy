import utils, requests, json

API = utils.api()

class Tour:
    def __init__(self, location):
        self.location = location

    def geolocate(self):
        query = 'https://maps.googleapis.com/maps/api/' \
                'geocode/json?address={}&key={}'.format(self.location.replace(' ', '+'), API)
        geocode = tuple(requests.get(query).json()['results'][0]['geometry']['location'].values())
        return geocode


    def get_places(self):
        location_str = ','.join([str(point) for point in self.geolocate()])
        query = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?' \
                'location={}&keyword=point+of+interest&radius=2000&key={}'.format(location_str, API)
        print(query)
        places = requests.get(query).json()
        print(json.dumps(places, indent=4))



tour1 = Tour('23 Worcester Sq, 02118')
tour1.get_places()
