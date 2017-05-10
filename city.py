from roads import Roads


class City(object):

    def __init__(self, name, x, y):
        self.x = x
        self.y = y
        self.name = name

        self.roads = Roads()
        # This string representation is set only once.
        self._str = "%s (%4.2f, %4.2f)" % (self.name, self.x, self.y)

    def __str__(self):
        return self._str

    def __cmp__(self, other):
        return cmp(self._str, str(other))
