from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

# Add custom filters here. Use these decorators: @register.filter, @stringfilter.
