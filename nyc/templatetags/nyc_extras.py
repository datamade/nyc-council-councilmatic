from django import template
from django.template.defaultfilters import stringfilter
from django.utils.html import strip_tags
import re

register = template.Library()

@register.filter
@stringfilter
def clean_plain_text(text):
    paragraphs = text.replace('�', '§').split('\n')

    text = ''.join('<p class="text-preview">{}</span></p>'.format(p.strip()) for p in paragraphs if is_text(p.strip()))

    return text

def is_text(text):
  return (text) and ('..' not in text) and (text != '2')
