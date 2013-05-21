import traceback
from decimal import Decimal
from itertools import groupby, izip
from time import time


class Timeline(object):

    def __init__(self):
        self._start_time = None
        self._end_time = None
#        self._stack = []
        self._log = []
        self._splits = []
        self.stats = []
        self.total_block_time = 0

#    def push_block(self, name):
#        self._stack.append(name)
#
#    def log(self, label, start, stop):
#        self._log.append((tuple(self._stack), label, start, stop))
#        self._stack.pop()

    def time_split(self, *name):
        split_time = time()
        for n in name:
            self._splits.append((n, split_time))
        return split_time

    @property
    def start_time(self):
        if self._splits:
            return Decimal(self._splits[0][1])
        elif self._log:
            return Decimal(self._log[0][-2])
        else:
            return Decimal(time())

    @property
    def end_time(self):
        if self._splits:
            return Decimal(self._splits[-1][1])
        elif self._log:
            return Decimal(self._log[-1][-1])
        else:
            return Decimal(time())

    def count(self):
        return len([s for s in self.stats if s.type == 'block'])

    def total_time(self):
        return (self.end_time - self.start_time) * Decimal(1000)

    def build(self, name='request'):
        try:
            stats = []

            ### Outer timeline entry
            if self._splits:
                stats.append(StatsEntry(self, name, self.start_time, self.end_time))

            ### Group split times by name to create block entries
            block_sort_func = lambda s: s[0]
            blocks = {}
            for name, splits in groupby(sorted(self._splits, key=block_sort_func), block_sort_func):
                splits = list(splits)
                if len(splits) >= 2:
                    if not len(splits) % 2:
                        for start, stop in izip(splits, splits[1:]):
                            blocks[name] = StatsEntry(self, name, start[1], stop[1])
                    else:
                        raise Exception('Trailing measure block "%s"' % name)

            stats.extend(blocks.values())

            ### Add "lonely" split times
            for (name, start_time), (_, end_time) in zip(self._splits, self._splits[1:]):
                if not name in blocks.keys():
                    stats.append(StatsEntry(self, name, start_time, end_time))

            ### Analyze blocks
#            block_sort_func = lambda s: s[0]
#            for stack, log_entries in groupby(sorted(self._log, key=block_sort_func), block_sort_func):
#                log_entries = list(log_entries)
#                block_stats = BlockStats(self, stack, log_entries)
#                stats.append(block_stats)

            ### Fill gaps
            stats = sorted(stats, key=lambda s: s.start_time)
            next = None
            for previous, next in zip(stats, stats[1:]):
                if previous.start_time < next.start_time < previous.end_time:
                    stats.append(StatsEntry(self, '...', previous.start_time, next.start_time))
                elif next.start_time > previous.end_time:
                    stats.append(StatsEntry(self, '...', previous.end_time, next.start_time))
            ### Add tail gap
            if next.end_time < self.end_time:
                stats.append(StatsEntry(self, '...', next.end_time, self.end_time))

            ### Level entries
            level = 1
            parents = []
            stats = sorted(stats, key=lambda s: s.start_time)
            for previous, next in zip(stats, stats[1:]):
                previous.level = level
                if previous.wraps(next):
                    previous.level = level
                    parents.append(previous)
                    level += 1
                if next.start_time > parents[-1].end_time:
                    parent = parents.pop()
                    level = parent.level
            if parents:
                stats[-1].level = parents[0].level + 1

        except Exception, e:
            traceback.print_exc()

        else:
            self.stats = stats
            self.total_block_time = sum((s.time for s in self.stats if isinstance(s, BlockStats) and s.is_parent))

        return self


class StatsEntry(dict):

    type = 'split'

    def __init__(self, timeline, name, start, stop, level=1):
        super(StatsEntry, self).__init__()
        self.timeline = timeline
        if isinstance(name, tuple):
            self.prefix, self.name = name
        else:
            self.prefix, self.name = None, name
        self.start_time, self.end_time = Decimal(start), Decimal(stop)
        self.level = level
        self.is_parent = False

    def __repr__(self):
        return u'%s [%s]' % (self.name, self.get_percent())

    def split(self, name, split_time, before=True):
        if before:
            new_entry = StatsEntry(self.timeline, name, self.start_time, split_time)
            self.start_time = split_time
        else:
            new_entry = StatsEntry(self.timeline, name, split_time, self.end_time)
            self.end_time = split_time

        return new_entry

    def wraps(self, other):
        if other.start_time >= self.start_time and self.end_time >= other.end_time:
            self.is_parent = True
        return self.is_parent

    @property
    def time(self):
        return (self.end_time - self.start_time) * Decimal(1000)

    @property
    def percent(self):
        return self.time / self.timeline.total_time() * Decimal(100)

    def get_percent(self):
        return (u'%.8f%%' % self.percent).replace(',', '.')

    @property
    def offset(self):
        return (((self.start_time - self.timeline.start_time) * Decimal(1000)) / self.timeline.total_time()) * Decimal(100)

    def get_offset(self):
        return (u'%s%%' % self.offset).replace(',', '.')

    def is_child(self):
        return self.level > 1


class BlockStats(StatsEntry):

    type = 'block'

    def __init__(self, timeline, stack, stats):
        stats_dict = {name: (start, stop) for _, name, start, stop in stats}

        name = stack[-1]
        super(BlockStats, self).__init__(timeline, name, *stats_dict.pop('time'))

        self.update(stats_dict)
