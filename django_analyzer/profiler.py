import cProfile
import pstats
from cStringIO import StringIO


class Profiler(object):

    def __init__(self):
        self.profile = cProfile.Profile()

    def start(self):
        """
        Start collecting profiling data
        """
        self.profile.enable()

    def stop(self):
        """
        Stop collecting profiling data
        """
        self.profile.disable()

    def run(self, func, *args, **kwargs):
        """
        Profile and collect data for specific function
        """
        return self.profile.runcall(func, *args, **kwargs)

    def analyze(self):
        """
        Analyze and structure collected data

        self.stats structure:
        ('django_analyzer/timeline.py', 29, 'time_split'):
                            (8,
                             8,
                             1.7e-05,
                             2.2e-05,
                             {('django_analyzer/contextmanager.py', 46, 'measure'): (4,
                                                                                     4,
                                                                                     6e-06,
                                                                                     9e-06),
                              ('django_analyzer/patching.py', 35, 'analyze_render_to_response'): (1,
                                                                                                  1,
                                                                                                  3e-06,
                                                                                                  3e-06),
                              ('django_analyzer/patching.py', 94, 'pre_process_response'): (1,
                                                                                            1,
                                                                                            1e-06,
                                                                                            1e-06),
                              ('django_analyzer/patching.py', 103, 'post_process_view'): (1,
                                                                                          1,
                                                                                          4e-06,
                                                                                          4.9999999999999996e-06),
                              ('django_analyzer/patching.py', 113, 'post_process_response'): (1,
                                                                                              1,
                                                                                              3e-06,
                                                                                              4e-06)}),
        """
        stream = StringIO()
        ps = pstats.Stats(self.profile, stream=stream)
        self.stats = ps.stats

        # TODO: Format keys to more readable package/module/func
        # from pprint import pprint
        # pprint(self.stats)
        #
        # ('django_analyzer/timeline.py', 29, 'time_split')
        # -> ('django_analyzer.timeline.time_split()', 29)

        # for x, (calls, rcalls, tottime, cumtime, stack) in ps.stats.iteritems():
        #     print x, '%s/%s' % (rcalls, calls), tottime, cumtime
        #     for y, (sub_rcalls, sub_calls, sub_tottime, sub_cumtime) in stack.iteritems():
        #         print '\t-> ', y, '%s/%s' % (sub_rcalls, sub_calls), sub_tottime, sub_cumtime

        ps.sort_stats('time')
        ps.print_stats()
        return stream.getvalue()
