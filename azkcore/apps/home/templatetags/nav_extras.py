from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def nav_active(context, *url_names):
    request = context['request']
    current = request.resolver_match.url_name
    return current in url_names