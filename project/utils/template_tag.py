# coding: utf-8
# from datetime import datetime
#
# from project.data.consts import LANG, LANG_LEVEL, ROLES, PERSIAN_MON, AWARD
# from .date import gregorian_to_jalali
# from .template import is_ajax
# from .persian import english_num_to_persian
# from .thumbnail import Thumbnail
# from project.utils import persian
#
#
# def jalali(value):
#     if not value:
#         return ''
#
#     datelist = gregorian_to_jalali(value).split("/")
#     datelist[0] = persian(datelist[0])
#     datelist[2] = persian(datelist[2])
#     datelist[1] = PERSIAN_MON[int(datelist[1]) - 1]
#
#     return u"{} {} {}".format(datelist[2], datelist[1], datelist[0])


def teaser(text, length=35):
    """
    Convert a long text to teaser without any word wrappings

    Author: Hamid FzM
    Email: hamidfzm@gmail.com
    """
    if len(text) <= length:
        return text
    parts = text.split(' ')
    while len(' '.join(parts)) > length:
        parts.pop()
    return ' '.join(parts) + '...'


def qrcode(string, size="150x150"):
    return '<img src="https://api.qrserver.com/v1/create-qr-code/?size={size}&data={string}&charset-source=UTF-8">'.format(size=size, string=string)

def init_filters(app):
    # app.jinja_env.globals['jalali'] = jalali
    app.jinja_env.globals['teaser'] = teaser
    app.jinja_env.globals['qrcode'] = qrcode
