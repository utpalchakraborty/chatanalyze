import datetime
import itertools
import numpy as np
import matplotlib.pyplot as plt
plt.rcdefaults()
import matplotlib.pyplot as plt


class PostItem(object):

    def __init__(self, dt, name, rest):
        self._dt = dt
        self._name = name.decode("utf-8-sig").encode("utf-8").strip()
        self._rest = rest
        self._lines = []

    def add_line(self, line):
        self._lines.append(line)

    @property
    def month(self):
        return self._dt.date().month

    @property
    def name(self):
        return self._name

    @property
    def is_phone(self):
        return not self._name.replace(' ', '').isalpha()


    @property
    def is_birthday(self):
        return len(self._lines) == 0 and self._rest.lower().find('birthday') != -1

    @property
    def rest(self):
        return self._rest


def get_time(line):
    try:
        date_string = line[0:line.index(': ')].decode("utf-8-sig").encode("utf-8").strip()
        dt = datetime.datetime.strptime(date_string, '%m/%d/%y, %I:%M:%S %p')
        rest = line[line.index(': ') + 2:].strip()
        name_index = rest.index(': ')
        return dt, rest[0:name_index], rest[name_index + 2:]
    except ValueError as e:
        return None, None, None


def count_adjacent(post_items, poster1, poster2, start_month=0, scan_ahead=1):
    index = 0
    count = 0
    while index < len(post_items) - 2:
        current_post = post_items[index]
        next_post = post_items[index + 1]
        if current_post.month >= start_month:
            if current_post.name == poster1 and next_post.name == poster2:
                count += 1
            #elif current_post.name == poster2 and next_post.name == poster1:
            #    count += 1
        index += 1
    return count


def get_post_items(file_name):
    items = []
    current = None
    for line in open(file_name):
        line = line.strip()
        if len(line) > 0:
            dt, name, rest = get_time(line)
            if dt and name and rest:
                current = PostItem(dt, name, rest)
                items.append(current)
            else:
                current.add_line(line)
    return items


def get_people_groups(items):
    return {k: list(g) for k, g in itertools.groupby(sorted(items, key=lambda t: t.name), key=lambda t: t.name)}


def print_post_frequency_by_people(p_groups):
    freq = [(k, len(v)) for k, v in p_groups.items()]
    freq = sorted(freq, key=lambda x: x[1], reverse=True)
    for i in freq:
        print 'Total posts by {} = {}'.format(i[0], i[1])
    return freq


def plot_post_freq(f):
    objects = tuple([item[0] for item in f])
    y_pos = np.arange(len(objects))
    performance = [item[1] for item in f]

    plt.barh(y_pos, performance, align='center', alpha=0.5)
    plt.yticks(y_pos, objects)
    plt.ylabel('')
    plt.title('Post Frequency')

    plt.show()


if __name__ == '__main__':

    post_items = get_post_items('/home/utpal/chats/PanoChat.txt')

    print 'all lines parsed'

    post_items = [item for item in post_items if not (item.is_birthday or item.is_phone)]
    people_groups = get_people_groups(post_items)
    post_freq = print_post_frequency_by_people(people_groups)
    plot_post_freq(post_freq)

    """
    peoples = people_groups.keys()
    adjacency_list = []
    percentages = []
    #print peoples
    for p1 in peoples:
        for p2 in peoples:
            if p1 != p2:
                count = count_adjacent(post_items, p1, p2)
                if count > 0:
                    percent = (count * 100.0)/len(people_groups[p2])
                    tup = p1, p2, count, percent
                    adjacency_list.append(tup)
                    percentages.append(percent)

    print "Mean", np.mean(percentages)
    print "Std", np.std(percentages)

    for i in sorted(adjacency_list, key=lambda x : x[2], reverse=True):
        print '{}, {} = {}'.format(i[0], i[1], i[2])
    """

    """
    month_groups = {k: list(g)  for k, g in itertools.groupby(post_items, key=lambda t : t.month)}


    for k, v in month_groups.items():
        print k, len(v)

    """

    """

    person_posts_by_month = {}
    for k, v in people_groups.items():
        person_posts_by_month[k] = [len(list(g)) for m, g in itertools.groupby(v, key=lambda t: t.month)]

    for k, month_qty in person_posts_by_month.items():
        print k, month_qty

    print np.corrcoef(person_posts_by_month['Alpana Prasad'], person_posts_by_month['Ajay Bansiwal'])
    """

    """
    post_freq = sorted([(k, len(v)) for k, v in people_groups.items()], key=lambda x: x[1], reverse=True)
    for i in post_freq:
        print i[0], i[1]
    """