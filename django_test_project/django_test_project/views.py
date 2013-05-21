from django.shortcuts import render_to_response
from django.template import RequestContext


def analyze(request):
    import time
    for x in range(1000000):
        x = 1 * 20

    return render_to_response('analyze.html', {}, RequestContext(request))
