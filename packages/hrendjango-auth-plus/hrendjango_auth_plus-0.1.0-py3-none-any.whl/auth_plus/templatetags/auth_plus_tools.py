from django.template import Library
from auth_plus import TFA_WAYS

register = Library()


@register.inclusion_tag('auth_plus/includes/tfa_ways.html', takes_context=True)
def tfa_ways(context):
    return dict(tfa_ways=TFA_WAYS, current_id=context['request'].path.split('/')[-1])
