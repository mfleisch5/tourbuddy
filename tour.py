import utils, requests, json, math

API = utils.api()


class Stop:
    def __init__(self, data):
        self.address = data['formatted_address']
        self.x, self.y = tuple(data['geometry']['location'].values())
        self.name = data['name']
        self.rating = float(data['rating'])
        self.reviews = float(data['user_ratings_total'])

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

    def location_as_stop(self):
        

    def plan(self):
        the_plan = TourPlanner(1000, self.stops, self.location)


class TourState:
    def __init__(self, time, remaining, base, visited, node):
        self.time = time
        self.remaining = remaining
        self.visited = visited
        self.base = base
        self.node = node

    def score(self):
        """
        # check if starting location
        if self.curr:
            # if not, assign score as (rating/5 * number of reviews)/number of reviews * remaining nodes
            # makes heuristic always < the number of nodes remaining, which is the max true cost-to-go when the cost is
            # always 1
            score = ((self.curr.rating * self.curr.reviews / 5.0) / self.curr.reviews) * len(self.remaining)
        else:
            # if starting state or has no reviews, assign score of 0
            score = 0
        """

        score = ((self.node.rating * self.node.reviews / 5.0) / self.node.reviews) * len(self.remaining)

        return score

    def next_stops(self):
        dist = lambda o: math.sqrt((self.node.x - o.x) ** 2 + (self.node.y - o.y) ** 2)
        queue, stops = set(self.remaining), []
        for _ in range(3):
            next_stop = min(queue, key=dist)
            queue.remove(next_stop)
            stops.append(next_stop)
        # https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins=Washington,DC&destinations=New+York+City,NY&key=YOUR_API_KEY
        return stops

    def is_plausible(self):
        pass


class TourPlanner(TourState):
    def __init__(self, time, remaining, base):
        TourState.__init__(self, time, remaining, base, set(), base)

    def score(self):
        """
        # check if starting location
        if self.curr:
            # if not, assign score as (rating/5 * number of reviews)/number of reviews * remaining nodes
            # makes heuristic always < the number of nodes remaining, which is the max true cost-to-go when the cost is
            # always 1
            score = ((self.curr.rating * self.curr.reviews / 5.0) / self.curr.reviews) * len(self.remaining)
        else:
            # if starting state or has no reviews, assign score of 0
            score = 0
        """

        return 0

    def is_plausible(self):
        return True

    def search(self):
        # Need a priority queue to account for cost
        fringe = utils.PriorityQueue()

        fringe.push(self.node, 0)
        while not fringe.isEmpty():
            node = fringe.pop()
            self.visited.add(node)
            self.remaining.remove(node)
            if node == self.base and node.visited:
                return node.visited
            for stop in node.next_stops():
                if stop not in self.visited:
                    fringe.update(stop, stop.score())


tour1 = Tour(location='23 Worcester Sq, 02118')
tour1.filter_destinations()
# tour2.filter_destinations()
