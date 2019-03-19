import utils, requests, json

API = utils.api()


class Tour:
    def __init__(self, location=None, json_data=None):
        self.location = None
        self.places = None
        self.initialize(location, json_data)

    def get_locality(self):
        query = 'https://maps.googleapis.com/maps/api/' \
                'geocode/json?address={}&key={}'.format(self.location.replace(' ', '+'), API)
        address_components = requests.get(query).json()['results'][0]['address_components']
        locality = next(comp for comp in address_components if 'locality' in comp['types'])['short_name'].strip()
        return locality

    def get_places(self):
        locality = self.get_locality().lower().replace(' ', '+')
        query = 'https://maps.googleapis.com/maps/api/place/textsearch/json?' \
                'query={}+point+of+interest&language=en&key={}'.format(locality, API)
        return requests.get(query).json()['results']

    def dump_places(self, file):
        compressed = {'location': self.location, 'places': self.get_places()}
        with open(file, 'w') as jf:
            json.dump(compressed, jf, indent=4)

    def filter_destinations(self):
        self.places.sort(key=lambda dest: -dest['user_ratings_total'])
        del self.places[20:]
        print(*[(dest['name'], dest['types'], dest['user_ratings_total']) for dest in self.places], sep='\n')

    def initialize(self, location, dest_json):
        if bool(location) == bool(dest_json):
            raise ValueError("Input must be either location string or json destination")
        if location:
            self.location = location
            self.places = self.get_places()
        else:
            with open(dest_json, 'r') as dj:
                data = json.load(dj)
                self.location = data['location']
                self.places = data['places']
        self.filter_destinations()


tour1 = Tour(location='23 Worcester Sq, 02118')
tour1.filter_destinations()
# tour2.filter_destinations()
