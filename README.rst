Django Analyzer
===============

A set of tools to profile django and python applications.


Configuration
-------------

#. Set ``DEBUG`` to True in your Django settings

#. Add ``django_analyzer`` to your ``INSTALLED_APPS`` setting so Django can
   find the template files associated with the Debug Toolbar::

       INSTALLED_APPS = (
           ...
           'django_analyzer',
       )


Analyzer
--------

The analyzer uses middlewares and an optional template tag to measure time
spent on different parts of a Django request:

#. Request total time

#. Middlewares request time

#. View execution time

#. Template rendering time

#. Middlewares response time


Configuration
-------------

#. The timeline is shown in a debug toolbar panel, add the following panel to
   your toolbar config::

       DEBUG_TOOLBAR_PANELS = (
           # ...
           'django_analyzer.toolbar.panels.ProfilingDebugPanel',
       )


Usage
-----

Optionally you can precise your timing stats by wrapping parts of your template
code with the ``measure`` template tag, name the block by passing a name/label token::

    {% load monkey_analyzer %}
    {% measure slowstuff %}
        <!-- crap -->
    {% endmeasure %}
