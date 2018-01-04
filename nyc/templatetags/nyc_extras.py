from django import template
from django.template.defaultfilters import stringfilter
from django.utils.html import strip_tags
import re

register = template.Library()

# Add custom filters here. Use these decorators: @register.filter, @stringfilter.
