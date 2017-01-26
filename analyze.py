import datetime
import itertools
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
plt.rcdefaults()



class PostItem(object):

    def __init__(self, dt, name, rest):
        self._dt = dt
        self._name = name.decode("utf-8-sig").encode("utf-8").strip()
        self._rest = rest.decode("utf-8-sig").encode("utf-8").strip()
        self._lines = []

    def add_line(self, line):
        self._lines.append(line)

    @property
    def month(self):
        return self._dt.date().month

    @property
    def hour(self):
        return self._dt.time().hour

    @property
    def name(self):
        return self._name

    @property
    def is_phone(self):
        return not self._name.replace(' ', '').isalpha()

    @property
    def is_image(self):
        return 'image omitted' in self._rest

    @property
    def is_video(self):
        return 'video omitted' in self._rest

    @property
    def is_lol(self):
        return 'lol' in self._rest.lower()

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
    while index < len(post_items) - (1 + scan_ahead):
        current_post = post_items[index]
        if current_post.month >= start_month:
            if current_post.name == poster1:
                next_posts_names = [post.name for post in post_items[index + 1:index + 1 + scan_ahead]]
                if poster2 in next_posts_names:
                    count += 1
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
                print current.hour
                items.append(current)
            else:
                current.add_line(line)
    return items


def get_people_groups(items, min_count=10):
    p = {k: list(g) for k, g in itertools.groupby(sorted(items, key=lambda t: t.name), key=lambda t: t.name)}
    return {k: v for k, v in p.items() if len(v) > min_count}


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


def print_media_statistics(caption, p_groups, media_dict):
    print '-----------------------------------------------------------'
    data = []
    for k, v in media_dict.items():
        count = len(v)
        percent = (count * 100.0)/len(p_groups[k])
        data.append((k, count, percent))

    data = sorted(data, key=lambda x : x[2], reverse=True)
    for d in data:
        print 'Total {} by {} = {}.    {}%'.format(caption, d[0], d[1], d[2])


def media_statistics(p_groups):
    images = {}
    videos = {}
    media = {}
    lols = {}
    for p, items in p_groups.items():
        images[p] = [item for item in items if item.is_image]
        videos[p] = [item for item in items if item.is_video]
        media[p] = [item for item in items if item.is_video or item.is_image]
        lols[p] = [item for item in items if item.is_video or item.is_lol]

    print_media_statistics('image', p_groups, images)
    print_media_statistics('video', p_groups, videos)
    print_media_statistics('media', p_groups, media)
    print_media_statistics('lols', p_groups, lols)


def display_month_trend(p_items):
    month_groups = {k: list(g) for k, g in itertools.groupby(p_items, key=lambda t: t.month)}
    x = []
    y = []
    for k, v in month_groups.items():
        print k, len(v)
        x.append(k)
        y.append(len(v))

    plt.scatter(x, y)
    plt.plot(np.unique(x), np.poly1d(np.polyfit(x, y, 1))(np.unique(x)))
    plt.plot(np.unique(x), np.poly1d(np.polyfit(x, y, 2))(np.unique(x)))
    plt.show()


def print_adjacency_list_for(name, a_list):
    print('-----------------------------------------------')
    a_list = [i for i in a_list if i[1] == name]
    names = []
    freq = []

    for i in sorted(a_list, key=lambda x: x[3], reverse=False):
        print '{}, {} = {},   {}%'.format(i[0], i[1], i[2], i[3])
        names.append(i[0])
        freq.append(i[2])

    '''
    objects = tuple(names)
    y_pos = np.arange(len(objects))
    plt.barh(y_pos, freq, align='center', alpha=0.5)
    plt.yticks(y_pos, objects)
    plt.ylabel('')
    plt.title('Post Frequency of {}'.format(name))

    plt.show()
    '''


def radial_bar_plot(keys, values):
    # force square figure and square axes looks better for polar, IMO
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8], polar=True)
    ax.xaxis.set_major_formatter(plt.NullFormatter())

    N = len(keys) #24
    theta = np.arange(0.0, 2 * np.pi, 2 * np.pi / N)
    radii = values #10 * np.random.rand(N)
    width = np.pi / N #4 * np.random.rand(N)
    bars = ax.bar(theta, radii, width=width, bottom=0.0)
    for r, bar in zip(radii, bars):
        bar.set_facecolor(cm.jet(r / 1000.))
        bar.set_alpha(0.5)

    plt.show()


def compute_adjacency(p_groups, p_items):
    peoples = p_groups.keys()
    adjacency_list = []
    percentages = []
    # print peoples
    for p1 in peoples:
        for p2 in peoples:
            if p1 != p2:
                count = count_adjacent(p_items, p1, p2, scan_ahead=3)
                if count > 0:
                    percent = (count * 100.0)/len(p_groups[p1])
                    tup = p1, p2, count, percent
                    adjacency_list.append(tup)
                    percentages.append(percent)

    print "Mean", np.mean(percentages)
    print "Std", np.std(percentages)

    for p1 in peoples:
        print_adjacency_list_for(p1, adjacency_list)

if __name__ == '__main__':

    post_items = get_post_items('/home/utpal/chats/PanoChat.txt')
    print 'all lines parsed'

    post_items = [item for item in post_items if not (item.is_birthday or item.is_phone)]
    hour_freq = {k: 0 for k in range(0, 24)}
    for item in post_items:
        hour_freq[item.hour] += 1

    print hour_freq
    print hour_freq.keys()
    print hour_freq.values()
    radial_bar_plot(hour_freq.keys(), hour_freq.values())

    """
    # display_month_trend(post_items)

    people_groups = get_people_groups(post_items)
    compute_adjacency(people_groups, post_items)
    """

    """
    post_freq = print_post_frequency_by_people(people_groups)
    media_statistics(people_groups)
    #plot_post_freq(post_freq)

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