import utils, requests, json

API = utils.api()


class Stop:
    def __init__(self, data):
        self.address = data['formatted_address']
        self.x, self.y = tuple(data['geometry']['location'].values())
        self.name = data['name']
        self.rating = data['rating']
        self.reviews = data['user_ratings_total']

    def __eq__(self, o):
        return isinstance(o, Stop) and self.name == o.name and (self.x, self.y) == (o.x, o.y)

    def __hash__(self):
        return hash(self.name) ^ hash(self.x) ^ hash(self.y) ^ hash((self.name, self.x, self.y))


class Tour:
    def __init__(self, location=None, json_data=None):
        self.location = None
        self.places = None
        self.stops = None
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
        self.stops = set(Stop(place) for place in self.places)


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


class TourPlanner:
    def __init__(self, visited, time, nodes, base):
        self.visited = visited
        self.time = time
        self.nodes = nodes
        self.base = base

    def score(self, state, visited, nodes):
        # check if starting location
        if bool(state['rating']) and bool(state['user_ratings_total']):
            # if not, assign score as (rating/5 * number of reviews)/number of reviews * remaining nodes
            # makes heuristic always < the number of nodes remaining, which is the max true cost-to-go when the cost is
            # always 1
            remaining = len(nodes) - len(visited)
            reviews = state['user_ratings_total']
            rating = state['rating'] / 5
            score = ((rating * reviews) / reviews) * remaining
        else:
            # if starting state or has no reviews, assign score of 0
            score = 0

        return score

    def next_stop(self):
        pass

    def is_plausible(self):
        pass

    def search(self, base, visited, nodes):
        # Need a priority queue to account for cost
        fringe = utils.PriorityQueue()

        start = (base, [], 0)  # (node, path, cost)
        fringe.push(start, 0)

        while not fringe.isEmpty():
            (node, path, cost) = fringe.pop()

            if node == base and not path.isEmpty():
                return path

            if not node in visited:
                visited.add(node)
                for n, action, cost in self.next_stop():
                    nCost = 1 + cost
                    nPath = path + [action]
                    state = (n, nPath, nCost)
                    priority = self.score(n, visited, nodes) + nCost
                    fringe.push(state, priority)

        pass


tour1 = Tour(location='23 Worcester Sq, 02118')
tour1.filter_destinations()
# tour2.filter_destinations()
