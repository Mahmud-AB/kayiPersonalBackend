import base64
import datetime
import json
import random
import re

import pytz
from django import template
from django.template.defaultfilters import stringfilter

from web_api.models import Users

register = template.Library()


@register.filter(name='multiply')
@stringfilter
def multiply(value, arg):
    return int(value) * arg


@register.filter(name='sum')
def sum(value, arg):
    return round((float(value) + arg), 2)


@register.filter(name='sub')
def sub(value, arg):
    return round((float(value) - arg), 2)


@register.filter(name='loop_ranges')
def loop_ranges(number):
    return range(number)


@register.filter(name='new_product')
def new_product(created):
    a = datetime.datetime(created.year, created.month, created.day, created.hour, created.minute, created.second)
    a = (datetime.datetime.utcnow() - a).total_seconds()
    if a < 60 * 60 * 24:
        return True
    else:
        return False


@register.filter(name='p_price')
def p_price(value, arg):
    return round(((100 - arg) / 100) * int(value), 2)


@register.filter(name='convert_to_json')
def convert_to_json(value):
    try:
        return json.dumps(value)
    except:
        return ""


@register.filter(name='random_str')
def random_str(arr=""):
    return random.choice(arr.split(","))


def plane_text_1(html):
    import html2text
    html = html2text.html2text(html)
    html = html.replace("\t", " ")
    html = html.replace("\n", " ")
    html = html.replace("\r", " ")
    return html


def plane_text_2(html):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', html)


@register.filter(name='textify_n_char')
def textify_n_char(html, arg):
    try:
        text_only = plane_text_2(html)
        if len(text_only) <= arg:
            return text_only
        return text_only[:arg] + "..."
    except:
        return ""


@register.filter(name='sting_to_md5')
def sting_to_md5(str):
    try:
        return base64.b64encode(str.encode("ascii")).decode("ascii")
    except:
        return ""


@register.simple_tag
def define(val=None):
    return val


@register.filter(name='nowdayago')
@stringfilter
def nowdayago(intval, date):
    import timeago, datetime
    now = datetime.datetime.utcnow()
    now = now.replace(tzinfo=pytz.utc)
    ret = str(timeago.format(date, now))
    ret = ret.replace("seconds", "sec")
    ret = ret.replace("minutes", "min")
    ret = ret.replace("hours", "hou")
    return ret


@register.filter(name='shop_info')
@stringfilter
def shop_info(shop_id='0'):
    try:
        user = Users.objects.get(pk=shop_id)
        str = '<a href="/service/info?id=' + shop_id + '" target="_blank"><img src="' + user.image + '" style="height: 40px;width: 40px"></a>'
        return str
    except:
        return ""


@register.filter(name='page_range')
def page_range(page, last):
    span = 7
    return range(max(min(page - (span - 1) // 2, last - span + 1), 1), min(max(page + span // 2, span), last) + 1)
