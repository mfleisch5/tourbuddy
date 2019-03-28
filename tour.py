import utils, requests, json, math

API = utils.api()


class Stop:
    def __init__(self, address, coords, name, rating, reviews):
        self.address = address
        self.x, self.y = coords
        self.name = name
        self.rating = float(rating)
        self.reviews = reviews

    def __eq__(self, o):
        return isinstance(o, Stop) and self.name == o.name and (self.x, self.y) == (o.x, o.y)

    def __hash__(self):
        return hash(self.name) ^ hash(self.x) ^ hash(self.y) ^ hash((self.name, self.x, self.y))

    def __str__(self):
        return ' '.join([self.name, str(self.x), str(self.y), str(self.rating), str(self.reviews)])


class Tour:
    def __init__(self, location=None, json_data=None):
        self.location = None
        self.places = None
        self.stops = None
        self.initialize(location, json_data)

    @staticmethod
    def geo_locality(address):
        query = 'https://maps.googleapis.com/maps/api/' \
                'geocode/json?address={}&key={}'.format(address.replace(' ', '+'), API)
        response = requests.get(query).json()['results'][0]
        coords = tuple(response['geometry']['location'].values())
        address_components = response['address_components']
        locality = next(comp for comp in address_components if 'locality' in comp['types'])['short_name'].strip()
        return coords, locality

    @staticmethod
    def get_places(locality):
        locality = locality.lower().replace(' ', '+')
        query = 'https://maps.googleapis.com/maps/api/place/textsearch/json?' \
                'query={}+point+of+interest&language=en&key={}'.format(locality, API)
        return requests.get(query).json()['results']

    def dump_places(self, file):
        compressed = {'location': dict(zip(('address', 'coordinates'), self.location)), 'places': self.places}
        with open(file, 'w') as jf:
            json.dump(compressed, jf, indent=4)

    def filter_destinations(self):
        self.places.sort(key=lambda dest: -dest['user_ratings_total'])
        del self.places[20:]
        stop = lambda p: Stop(p['formatted_address'], tuple(p['geometry']['location'].values()), p['name'],
                              p['rating'], p['user_ratings_total'])
        self.stops = set(stop(place) for place in self.places)

    def initialize(self, location, dest_json):
        if bool(location) == bool(dest_json):
            raise ValueError("Input must be either location string or json destination")
        if location:
            coords, locality = Tour.geo_locality(location)
            self.location = location, coords
            self.places = Tour.get_places(locality)
        else:
            with open(dest_json, 'r') as dj:
                data = json.load(dj)
                self.location = data['location']['address'], tuple(data['location']['coordinates'])
                self.places = data['places']
        self.filter_destinations()

    def plan(self):
        base = Stop(*self.location, 'base', 0.0, 0)
        the_plan = TourPlanner(1000, self.stops, base)
        print(the_plan.next_stops())


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
        for _ in range(min(len(self.remaining), 3)):
            next_stop = min(queue, key=dist)
            queue.remove(next_stop)
            stops.append(next_stop)
        # https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins=Washington,DC&destinations=New+York+City,NY&key=YOUR_API_KEY
        print(*stops, self.node)
        return stops

    def is_plausible(self):
        pass


class TourPlanner(TourState):
    def __init__(self, time, remaining, base):
        TourState.__init__(self, time, remaining, base, set(), base)

    def score(self):
        return 0

    def is_plausible(self):
        return True

    def search(self):
        # Need a priority queue to account for cost
        fringe = utils.PriorityQueue()

        fringe.push(self, 0)
        while not fringe.isEmpty():
            state = fringe.pop()
            self.visited.add(node)
            self.remaining.remove(node)
            if state.node == self.base and state.visited:
                return state.visited
            for next_state in state.next_stops():
                next_stop = next_state.node
                if next_stop not in self.visited:
                    fringe.update(next_stop, next_state.score())

        # All nodes are checked for plausibility and once all nodes are implausible the queue will die out which will
        # lead to result


tour1 = Tour(json_data='turin.json')
tour1.plan()
# tour2.filter_destinations()
