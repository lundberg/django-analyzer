from debug_toolbar.panels import DebugPanel
from django_analyzer.contextmanager import context


class ProfilingDebugPanel(DebugPanel):
    """
    Panel that displays the Profiling stats.
    """
    name = 'Profiling'
    template = 'django_analyzer/panel/django_analyzer_panel.html'
    has_content = True

    @property
    def timeline(self):
        if not hasattr(self, '_timeline'):
            self._timeline = context.timeline.build()
        return self._timeline

    def nav_title(self):
        return self.name

    def nav_subtitle(self):
        return u'%i blocks analyzed in %.2fms' % (self.timeline.count(), self.timeline.total_block_time)

    def url(self):
        return ''

    def title(self):
        return u'Timeline'

    def get_stats(self):
        return {
            'timeline': self.timeline,
            'profiler_stats': context.profiler.analyze(),
        }
