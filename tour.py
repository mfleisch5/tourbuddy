import utils, requests, json

API = utils.api()

class Tour:
    def __init__(self, location):
        self.location = location

    def get_places(self):
        query = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?' \
                'location={}&keyword=point+of+interest&key={}'

