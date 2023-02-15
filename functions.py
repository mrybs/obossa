import json
import sqlite3
from PIL import *
from PIL import Image, ImageDraw, ImageFont
from vkbottle import Bot
from vkbottle.bot import Message

def prepare_mask(size, antialias=2):
    mask = Image.new('L', (size[0] * antialias, size[1] * antialias), 0)
    ImageDraw.Draw(mask).ellipse((0, 0) + mask.size, fill=255)
    return mask.resize(size, Image.ANTIALIAS)

def crop(im, s):
    w, h = im.size
    k = w / s[0] - h / s[1]
    if k > 0: im = im.crop(((w - h) / 2, 0, (w + h) / 2, h))
    elif k < 0: im = im.crop((0, (h - w) / 2, w, (h + w) / 2))
    return im.resize(s, Image.ANTIALIAS)

def wrap(string: str, width: int):
    pre_result = ''
    a = 0
    for i in range(len(string)):
        pre_result += string[i]
        if string[i] == '\n': a = -1
        if string[i] in ['.', ',', '?', '!']:
            a += -1
        if a >= width:
            pre_result += '\n'
            a = 0
        a += 1
    result = []
    for pr in pre_result.split(sep='\n'):
        result.append(pr.strip())
    return result

def makeshit(who: str, when: str, save_file: str, ava_file: str, text: str, dot3_file='dot3.png', aspect=2, theme={}):
    roboto_medium18 = ImageFont.truetype('Roboto-Medium.ttf', size=18 * aspect)
    roboto_regular18 = ImageFont.truetype('Roboto-Regular.ttf', size=18 * aspect)
    roboto_medium14 = ImageFont.truetype('Roboto-Medium.ttf', size=14 * aspect)
    if 'files' in list(theme) and theme['files']['medium18'] is not None:
        try:
            roboto_medium18 = ImageFont.truetype('themes/files/'+theme['files']['medium18']
                    , size=18 * aspect)
        except Exception: pass
    if 'files' in list(theme) and theme['files']['medium14'] is not None:
        try:
            roboto_medium14 = ImageFont.truetype('themes/files/'+theme['files']['medium14'], size=14 * aspect)
        except Exception: pass
    if 'files' in list(theme) and theme['files']['regular18'] is not None:
        try:
            roboto_regular18 = ImageFont.truetype('themes/files/'+theme['files']['regular18'], size=18 * aspect)
        except Exception: pass

    x = 576
    y = 1
    if 'textgen' in list(theme) and theme['textgen']['y-aspect'] is not None:
        y = theme['textgen']['y-aspect']
    a = 25.1
    if 'textgen' in list(theme) and theme['textgen']['maxline'] is not None:
        y *= float(74.5 + 74.5 + len(wrap(text, theme['textgen']['maxline'])) * a)
    else:
        y *= float(74.5*2 + len(wrap(text, 54)))
    y = int(y)

    if 'colors' in list(theme) and theme['colors']['background'] is not None:
        photo = Image.new('RGBA', (x * aspect, y * aspect), theme['colors']['background'])
    else:
        photo = Image.new('RGBA', (x * aspect, y * aspect), '#222222')
    ava = Image.open(ava_file)
    dot3 = Image.open(dot3_file)

    if 'files' in list(theme) and theme['files']['dot3'] is not None:
        try:
            dot3 = Image.open(f'themes/files/{theme["files"]["dot3"]}')
        except Exception: pass

    Draw = ImageDraw.Draw(photo)

    if 'colors' in list(theme) and theme['colors']['whom'] is not None:
        Draw.text((90 * aspect, 20 * aspect), text=who, font=roboto_medium18, fill=theme['colors']['whom'])
    else:
        Draw.text((90 * aspect, 20 * aspect), text=who, font=roboto_medium18, fill='#c5c8cd')
    if 'colors' in list(theme) and theme['colors']['when'] is not None:
        Draw.text((90 * aspect, 45 * aspect), text=when, font=roboto_medium14, fill=theme['colors']['when'])
    else:
        Draw.text((90 * aspect, 45 * aspect), text=when, font=roboto_medium14, fill='#757678')

    margin = 20
    offset = 40
    distance = 9.4
    if 'textgen' in list(theme) and theme['textgen']['distance'] is not None:
            distance = theme['textgen']['distance']
    textc = ''
    if 'textgen' in list(theme) and theme['textgen']['maxline'] is not None:
        textc = '\n'.join(wrap(text, theme['textgen']['maxline']))
    else:
        textc = '\n'.join(wrap(text, 54))
    text = textc
    print(text)
    while '\n\n' in text:
        text = text.replace('\n\n', '\n')

    for line in text.split(sep='\n'):
        if 'colors' in list(theme) and theme['colors']['text'] is not None:
            Draw.text((margin*aspect, ((59+offset/2) * aspect)), line, font=roboto_regular18, fill=theme['colors']['text'])
        else:
            Draw.text((margin*aspect, ((59+offset/2) * aspect)), line, font=roboto_regular18, fill="#dfe0e4")
        offset += roboto_medium18.getsize(line)[1] + distance

    if 'colors' in list(theme) and theme['colors']['button-publish'] is not None:
        Draw.text((90 * aspect, (y - 40) * aspect), text='Опубликовать', font=roboto_medium18, fill=theme['colors']['button-publish'])
    else:
        Draw.text((90 * aspect, (y - 40) * aspect), text='Опубликовать', font=roboto_medium18, fill='#e2e1e6')
    if 'colors' in list(theme) and theme['colors']['button-reject'] is not None:
        Draw.text(((x - 105 - 85) * aspect, (y - 40) * aspect), text='Отклонить', font=roboto_medium18, fill=theme['colors']['button-reject'])
    else:
        Draw.text(((x - 105 - 85) * aspect, (y - 40) * aspect), text='Отклонить', font=roboto_medium18, fill='#f96060')
    if 'colors' in list(theme) and theme['colors']['button-lines'] is not None:
        Draw.line((40 * aspect, (y - 60) * aspect, (x - 40) * aspect, (y - 60) * aspect), fill=theme['colors']['button-lines'])
        Draw.line((x / 2 * aspect, (y - 60 + 10) * aspect, x / 2 * aspect, (y - 10) * aspect), fill=theme['colors']['button-lines'])
    else:
        Draw.line((40 * aspect, (y - 60) * aspect, (x - 40) * aspect, (y - 60) * aspect), fill='#3a3636')
        Draw.line((x / 2 * aspect, (y - 60 + 10) * aspect, x / 2 * aspect, (y - 10) * aspect), fill='#3a3636')

    ava = crop(ava, (55 * aspect, 55 * aspect))
    ava.putalpha(prepare_mask((55 * aspect, 55 * aspect), 4))

    photo.paste(ava, (20 * aspect, 10 * aspect), ava)
    photo.paste(dot3, ((x - 30) * aspect, 25 * aspect), dot3)

    photo.save(save_file)

def get_state(user_id: int) -> str:
    try: return DBexecute(f'select state from states where id = {user_id}')[0][0]
    except Exception: return ''

def set_state(user_id: int, value: str):
    try:
        response = DBexecute(f'select state from states where id = {user_id}')
        if len(response) != 0: DBexecute(f'update states set state = "{value}" where id = {user_id}')
        else: DBexecute(f'insert into states (id,state,data) values({user_id},"{value}","")')
    except Exception: pass

def open_state(user_id: int):
    try: return json.loads(DBexecute(f'select data from states where id = {user_id}')[0][0].replace('\'', '"'))
    except Exception as e: return {}

def save_state(user_id: int, data: dict):
    try:
        response = DBexecute(f'select state from states where id = {user_id}')
        if len(response) != 0:
            dump = json.dumps(data)
            DBexecute(f'update states set data = "{data}" where id = {user_id}')
        else: DBexecute(f'insert into states (id,state,data) values({user_id},"","{json.dumps(data)}")')
    except Exception as e: print(e)

def clear_state(user_id: int):
    set_state(user_id, '')
    save_state(user_id, {})

def DBexecute(code: str):
    print(code)
    sheduleDB = sqlite3.connect('db.sqlite3', isolation_level=None)
    cursor = sheduleDB.cursor()
    cursor.execute(code)
    result = cursor.fetchall()
    sheduleDB.commit()
    sheduleDB.close()
    return result
