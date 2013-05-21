from django import template
from django_analyzer.contextmanager import measure

register = template.Library()


class MeasureNode(template.Node):

    def __init__(self, name, nodelist):
        self.name = name
        self.nodelist = nodelist

    def render(self, context):
        with measure(('measure', self.name)):
            output = self.nodelist.render(context)
        return output


@register.tag('measure')
def measure_tag(parser, token):
    name = token.split_contents()[-1]
    nodelist = parser.parse(('endmeasure',))
    parser.delete_first_token()
    return MeasureNode(name, nodelist)
