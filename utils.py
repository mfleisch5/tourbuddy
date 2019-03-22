import json

def api():
    with open('config.json', 'r') as jf:
        return json.load(jf)['api']


# A simple implementation of Priority Queue
# using Queue.
class PriorityQueue(object):
    def __init__(self):
        self.queue = []

    def __str__(self):
        return ' '.join([str(i) for i in self.queue])

    # for checking if the queue is empty
    def isEmpty(self):
        return len(self.queue) == []

    # for inserting an element in the queue
    def push(self, data, priority):
        d = {'data': data, 'priority': priority}

        self.queue.append(d)

    # for popping an element based on Priority
    def pop(self):
        try:
            max = 0
            for i in range(len(self.queue)):
                if self.queue[i]['priority'] > self.queue[max]['priority']:
                    max = i
            item = self.queue[max]['data']
            del self.queue[max]
            return item
        except IndexError:
            print()
            exit()


