import utils, math, requests, json, argparse, sys

API = utils.api()


class Stop:
    def __init__(self, address, coords, name, rating, reviews):
        self.address = address
        self.coords = coords
        self.name = name
        self.rating = float(rating)
        self.reviews = reviews

    def __eq__(self, o):
        return isinstance(o, Stop) and self.name == o.name and self.coords == o.coords

    def __hash__(self):
        return hash(self.name) ^ hash(self.coords) ^ hash((self.name, self.coords))

    def __str__(self):
        return ' '.join([self.name, str(self.coords[0]), str(self.coords[1]), str(self.rating), str(self.reviews)])


class Tour:
    def __init__(self, location, json_data, h, m, s):
        self.location = None
        self.places = None
        self.stops = None
        self.initialize(location, json_data)
        self.duration = (h * 3600) + (m * 60) + s

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
        the_plan = TourPlanner(self.duration, self.stops, Stop(*self.location, 'base', 0.0, 0))
        the_plan.search()


class TourState:
    def __init__(self, node, time, remaining, path, tcost, base):
        self.time = time
        self.remaining = remaining
        self.base = base
        self.node = node
        self.path = path
        self.tcost = tcost
        self.path_hash = ''.join(set(stop.name for stop in self.path))
        self.next_states = None

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

        #  score = ((self.node.rating * self.node.reviews / 5.0) / self.node.reviews) * len(self.remaining)

        score = utils.wt(self.node.coords, self.base.coords) - (200 * self.node.rating * (self.node.reviews ** 0.5))

        return score

    def is_goal(self):
        self.next_states = self.find_next_states()
        return not self.next_states

    def find_next_states(self):
        queue, states = set(self.remaining), []
        walk_time = lambda o: utils.wt(self.node.coords, o.coords)
        i = min(len(self.remaining), 3)
        while i > 0 and queue:
            next_stop = min(queue, key=walk_time)
            next_remaining = set(self.remaining)
            next_remaining.remove(next_stop)
            stop_time = walk_time(next_stop) + 1000
            next_state = TourState(next_stop, self.time - stop_time, next_remaining, self.path + [next_stop],
                                   self.tcost + stop_time, self.base)
            queue.remove(next_stop)
            if next_state.is_plausible():
                states.append(next_state)
            i -= 1

        # https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins=Washington,DC&destinations=New+York+City,NY&key=YOUR_API_KEY
        #  print(*states, sep='\n')
        return states

    def is_plausible(self):
        return (self.time - utils.wt(self.node.coords, self.base.coords)) > 0

    def __str__(self):
        return ' | '.join([str(self.score()), str(len(self.remaining)), self.node.name, '-->'.join([stop.name for stop in self.path])])

    def __hash__(self):
        return hash(self.path_hash)

    def __eq__(self, o):
        return isinstance(o, TourState) and self.path_hash == o.path_hash


class TourPlanner(TourState):
    def __init__(self, time, remaining, base):
        TourState.__init__(self, base, time, remaining, [base], 0, base)

    def score(self):
        return 0

    def is_plausible(self):
        return True

    def search(self):
        # Need a priority queue to account for cost
        fringe = utils.PriorityQueue()
        visited = set()
        fringe.push(self, self.score())
        visited.add(self)
        curr_state = None
        while not fringe.isEmpty():
            curr_state = fringe.pop()
            if curr_state.is_goal():
                print(curr_state.next_states)
                break
            print(curr_state)
            visited.add(curr_state)
            for next_state in curr_state.next_states:
                if next_state not in visited:
                    fringe.update(next_state, next_state.tcost + next_state.score())
        print('FINAL PATH:  ' + '--->'.join([stop.name for stop in curr_state.path]) + '--->base')
        print('FINAL PATH LEN: ', len(curr_state.path))
        print('Time left:', curr_state.time)

        # All nodes are checked for plausibility and once all nodes are implausible the queue will die out which will
        # lead to result


# tour1 = Tour(location='360 Huntington Ave, 02115')
# tour1.plan()
# tour2.filter_destinations()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='The address of your hotel or the path of your input file')
    duration = parser.add_argument_group(description='The duration of your tour')
    duration.add_argument('-hr', '--hours', type=float, default=0.0)
    duration.add_argument('-m', '--mins', type=float, default=0.0)
    duration.add_argument('-s', '--seconds', type=float, default=0.0)

    args = parser.parse_args()
    duration = args.hours, args.mins, args.seconds
    inputs = (args.input, None) if not '.json' in args.input else (None, args.input)
    if not any(duration):
        print("Need to input duration")
        sys.exit(1)

    tour = Tour(*inputs, *duration)
    tour.plan()
