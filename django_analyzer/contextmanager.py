from contextlib import contextmanager
from django_analyzer.profiler import Profiler
from django_analyzer.timeline import Timeline


class ThreadContext(object):
    """
    Django Analyzer context holding/exposing "local" timeline, profiler etc. to the app.
    """
    def __init__(self):
        try:
            from threading import local
        except ImportError:
            from django.utils._threading_local import local
        finally:
            self._locals = local()

    def _get_instance(self, clazz):
        name = '_django_analyzer__' + clazz.__name__
        instance = getattr(self._locals, name, None)
        if instance is None:
            instance = clazz()
            setattr(self._locals, name, instance)
        return instance

    @property
    def timeline(self):
        return self._get_instance(Timeline)

    @property
    def profiler(self):
        return self._get_instance(Profiler)


context = ThreadContext()


@contextmanager
def measure(label):
    """
    Context manager that measures time within block and adds time span to timeline.
    """
    context.timeline.time_split(label)
    yield
    context.timeline.time_split(label)
