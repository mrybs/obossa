import json
import random
import urllib

from vkbottle import PhotoMessageUploader

from config import *
from functions import *

bot = Bot(token=TOKEN)

@bot.on.message(command='start')
async def start(msg: Message):
    await msg.answer('Привет!\nДля получения справки по командам введи /help')
    clear_state(msg.from_id)

@bot.on.message(command='help')
async def help(msg: Message):
    clear_state(msg.from_id)
    await msg.answer(
        'Доступные команды:\n\n'
        '/start - начать\n'
        '/help - вывести эту справку\n'
        '/cancel - отмена\n'
        '/makeshit или /ms - сделать говно(сгенерировать скрин предложки)\n'
        '/makeshit-theme или /mst - выбрать тему для /makeshit'
    )

@bot.on.message(command='cancel')
async def cancel(msg: Message):
    await msg.answer('Отмена')
    clear_state(msg.from_id)

@bot.on.message(text=['/makeshit', '/ms'])
async def makeshitс(msg: Message):
    await msg.answer('Для начала генерации говна введите id профиля, либо напишите "моё"')
    clear_state(msg.from_id)
    set_state(msg.from_id, 'makeshit2')

@bot.on.message(text=['/makeshit-theme', '/mst'])
async def makeshit_theme(msg: Message):
    clear_state(msg.from_id)
    try:
        themes = []
        themes_file_names = []
        all_themes = json.loads(open(f'themes.json', 'r').read())
        for enum_theme in list(all_themes['themes']):
            themes_file_names.append(all_themes['themes'][enum_theme])

        for enum_theme_file in themes_file_names:
            theme = json.loads(open(f'themes/{enum_theme_file}.json', 'r').read())
            themes.append(f'\n{theme["name"]} - {theme["id"]}')

        await msg.answer(f'Выберите тему из списка и напишите ее номер\n{"".join(themes)}')
        set_state(msg.from_id, 'makeshit-theme')
    except Exception as e:
        await msg.answer(f'Не удалось загрузить список тем. Сообщите об этой ошибке @mrybs. Текст ошибки: {e}')

@bot.on.message()
async def states(msg: Message):
    state = get_state(msg.from_id)
    if state == 'makeshit2':
        id = msg.text
        if not (id.lower() in ['моё', 'мое', 'мой', 'моя', 'я']):
            if len(await bot.api.users.get(id)) == 0:
                await msg.answer('Неверный ID!')
                clear_state(msg.from_id)
                return
        else: id = msg.from_id

        await msg.answer('Хорошо. Введите время(вчера в 20:05, 24 мая в 05:39, 3 секунды назад, 10 января 2019 в 19:16)')
        data = open_state(msg.from_id)
        data['id'] = str(id)
        save_state(msg.from_id, data)
        set_state(msg.from_id, 'makeshit3')
    elif state == 'makeshit3':
        await msg.answer('Теперь введите анекдот и ждите результат')
        data = open_state(msg.from_id)
        data['time'] = msg.text
        save_state(msg.from_id, data)
        set_state(msg.from_id, 'makeshit4')
    elif state == 'makeshit4':
        file_name = f'photoe/photo{random.randint(0, 1000000)}.png'
        file_name_ava = f'photoe/ava{random.randint(0, 1000000)}.png'
        data = open_state(msg.from_id)
        user = (await bot.api.users.get(data['id'], fields=['photo']))[0]
        name = user.first_name + ' ' + user.last_name
        urllib.request.urlretrieve(user.photo, file_name_ava)

        theme = {}
        try:
            theme_name = ''
            theme_id = json.loads(DBexecute(f'select data from settings where id = {msg.from_id}')[0][0].replace('\'', '"'))['theme-id']
            themes = json.loads(open(f'themes.json', 'r').read())
            for enum_theme in list(themes['themes']):
                if theme_id == enum_theme:
                    theme_name = themes['themes'][enum_theme]

            theme = json.loads(open(f'themes/{theme_name}.json', 'r').read())
        except Exception as e:
            await msg.answer('Выбранная вами тема скорее всего была удалена. Выберите другую тему. Если не удается выбрать тему, то сообщите об ошибке @mrybs\n\nСейчас будет использована тема по умолчанию')

        makeshit(name, data['time'], file_name, file_name_ava, msg.text, theme=theme)
        photo = await PhotoMessageUploader(bot.api).upload(file_name)
        await msg.answer('Результат', attachment=photo)
        clear_state(msg.from_id)
    elif state == 'makeshit-theme':
        clear_state(msg.from_id)
        theme_id = ''
        themes = json.loads(open(f'themes.json', 'r').read())
        for enum_theme in list(themes['themes']):
            if msg.text == enum_theme:
                theme_id = msg.text

        if theme_id == '': await msg.answer('Выбранной вами темы не существует или она не зарегистрированна. Если вы действительно не ошиблись, то сообщите об ошибке @mrybs')
        else:
            try:
                data = {}
                if len(DBexecute(f'select data from settings where id = {msg.from_id}')) != 0:
                    data = json.loads(DBexecute(f'select data from settings where id = {msg.from_id}')[0][0].replace('\'', '"'))
                else:
                    empty_json = '{}'
                    DBexecute(f'insert into settings(id, data) values({msg.from_id}, "{empty_json}")')
                data['theme-id'] = msg.text
                dump = json.dumps(data).replace('"', '\'')
                DBexecute(f'update settings set data = "{dump}" where id = {msg.from_id}')
                await msg.answer('Тема успешно применена')
            except Exception as e: await msg.answer(f'Произошла непредвиденная ошибка. Сообщите о ней @mrybs. Текст ошибки: {e}')


bot.run_forever()
