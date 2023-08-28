import logging
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import *
import asyncio
import json
import sqlite3
import strings
from defines import *
import os

# установил уровень логов
logging.basicConfig(level=logging.INFO)

# создал логгер
logger = logging.getLogger(__name__)

# инициализация бота и диспетчера
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# подключение к БД
connection = sqlite3.connect('films.sqlite3')
cursor = connection.cursor()


# обработка команды /start
@dp.message_handler(commands=['start'])
async def start_handler(msg: types.Message):
    logger.info("Получена команда /start")

    await msg.answer(
        "🎬 Тебя приветствует КиноМан! 🍿\n\n"
        "Я отлично разбираюсь в кинематографе и с легкостью подберу тебе фильм на любой вкус, "
        "который точно не оставит тебя равнодушным! 😊🎥"
        "\n\nПогрузись в мир кино вместе с КиноМан! 🌟"
    )
    await msg.answer("Чтобы получить полный список команд, просто введи /help. Я буду рад помочь! 😊🤖")


# обработка команда /help
@dp.message_handler(commands=['help'])
async def help_handler(msg: types.Message):
    logger.info("Получена команда /help")
    instructions = """
/film - начать поиск фильма или сбросить все фильтры
/search - найти фильм по названию\n
Если пропала клавиатура с выбором элементов, ее можно вернуть, кликнув на значок рядом с выбором фотографии (четыре квадратика в прямоугольнике).\n
По всем вопросам обращаться: @alvoro44\n
Вперед, к новым кинолентам! 🌟🎥
"""
    await msg.answer(instructions)


# обработка команда /film
@dp.message_handler(commands=['film'])
async def film_handler(msg: types.Message):
    logger.info("Получена команда /film")
    await msg.answer("Отлично! Давай подберем фильм вместе! 🎉🎥😊")

    # получаю id пользователя
    id = str(msg.from_user.id)
    
    # считываю json-файл с запросами
    with open('requests_info.json', 'r', encoding='utf-8') as json_file:
        existing_data = json.load(json_file)

    # добавляю id пользователя в json-файл для формирования запроса к БД
    if id not in existing_data:
        new_data = {
            id: {
                "genre": [],
                "duration": [],
                "year": [],
                "country": [],
                "rate_kp": [],
                "rate_imdb": [],
                "age_limit": [],
                "series": False,
                "stage_number": 1,
                "viewed": [],
                "search": False,
                "films_list": [], 
                "current": 0
            }
        }
        existing_data.update(new_data)
    else:
        existing_data[id]["genre"] = []
        existing_data[id]["duration"] = []
        existing_data[id]["year"] = []
        existing_data[id]["country"] = []
        existing_data[id]["rate_kp"] = []
        existing_data[id]["rate_imdb"] = []
        existing_data[id]["age_limit"] = []
        existing_data[id]["series"] = False
        existing_data[id]["stage_number"] = 1      
        existing_data[id]["search"] = False
        existing_data[id]["films_list"] = []
        existing_data[id]["current"] = 0  

    with open('requests_info.json', 'w', encoding='utf-8') as json_file:
        json.dump(existing_data, json_file, indent=4, ensure_ascii=False)

    # создаю клавиатуру
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = strings.countries
    keyboard.add(*buttons)
    
    await msg.answer("Начнем с первого шага: выбери страну-производителя фильма. И помни: чем больше вариантов ты выберешь, тем выше шанс получить отличный фильм на вечер! Поехали! 🌟🎬🌍", reply_markup=keyboard)


# обработка нажатий на клавиатуру с выбором страны
@dp.message_handler(lambda msg: msg.text in strings.countries[:-1])
async def country_handler(msg: types.Message):

    id = str(msg.from_user.id)

    # запись в запрос страны
    with open('requests_info.json', 'r', encoding='utf-8') as json_file:
        existing_data = json.load(json_file)

    country = country_decoder[msg.text]

    if country not in existing_data[id]['country']:
        existing_data[id]['country'].append(country)
    else:
        await msg.reply("Ой! Кажется, ты уже выбрал эту страну. 🙈 Попробуй другую! 😊")

    with open('requests_info.json', 'w', encoding='utf-8') as json_file:
        json.dump(existing_data, json_file, indent=4, ensure_ascii=False)


# обработка нажатий на клавиатуру с выбором жанра
@dp.message_handler(lambda msg: msg.text in strings.genres[:-1])
async def genre_handler(msg: types.Message):

    id = str(msg.from_user.id)

    # запись в запрос жанра
    with open('requests_info.json', 'r', encoding='utf-8') as json_file:
        existing_data = json.load(json_file)

    genre = genre_decoder[msg.text]

    if genre not in existing_data[id]['genre']:
        existing_data[id]['genre'].append(genre)
    else:
        await msg.reply("Ой! Ты уже выбрал данный жанр. Попробуй выбрать другой, и мы продолжим поиск фильма! 🎬🌟😊")

    with open('requests_info.json', 'w', encoding='utf-8') as json_file:
        json.dump(existing_data, json_file, indent=4, ensure_ascii=False)


# обработка нажатий на клавиатуру с выбором продолжительности
@dp.message_handler(lambda msg: msg.text in strings.durations[:-1])
async def duration_handler(msg: types.Message):

    id = str(msg.from_user.id)

    # запись в запрос продолжительности
    with open('requests_info.json', 'r', encoding='utf-8') as json_file:
        existing_data = json.load(json_file)

    duration = duration_decoder[msg.text]

    if duration not in existing_data[id]['duration']:
        existing_data[id]['duration'].append(duration)
    else:
        await msg.reply("Ой! Ты уже выбрал данный элемент! Попробуй другой вариант и продолжим поиск фильма! 🎬🌟😊")

    with open('requests_info.json', 'w', encoding='utf-8') as json_file:
        json.dump(existing_data, json_file, indent=4, ensure_ascii=False)


# обработка нажатий на клавиатуру с выбором времени
@dp.message_handler(lambda msg: msg.text in strings.years[:-1])
async def year_handler(msg: types.Message):

    id = str(msg.from_user.id)

    # запись в запрос времени
    with open('requests_info.json', 'r', encoding='utf-8') as json_file:
        existing_data = json.load(json_file)

    year = year_decoder[msg.text]

    if year not in existing_data[id]['year']:
        existing_data[id]['year'].append(year)
    else:
        await msg.reply("Ой! Ты уже выбрал данный элемент! Попробуй другой вариант и продолжим поиск фильма! 🎬🌟😊")

    with open('requests_info.json', 'w', encoding='utf-8') as json_file:
        json.dump(existing_data, json_file, indent=4, ensure_ascii=False)


# обработка нажатий на клавиатуру с выбором возрастного ограничения
@dp.message_handler(lambda msg: msg.text in strings.ages[:-1])
async def age_handler(msg: types.Message):

    id = str(msg.from_user.id)

    # запись в запрос времени
    with open('requests_info.json', 'r', encoding='utf-8') as json_file:
        existing_data = json.load(json_file)

    age = age_decoder[msg.text]

    if age not in existing_data[id]['age_limit']:
        existing_data[id]['age_limit'].append(age.split("+")[0])
    else:
        await msg.reply("Ой! Ты уже выбрал данный элемент! Попробуй другой вариант и продолжим поиск фильма! 🎬🌟😊")

    with open('requests_info.json', 'w', encoding='utf-8') as json_file:
        json.dump(existing_data, json_file, indent=4, ensure_ascii=False)


# обработка нажатий на клавиатуру с выбором рейтинга на КиноПоиске
@dp.message_handler(lambda msg: msg.text in strings.rate_kp[:-1])
async def rate_kp_handler(msg: types.Message):

    id = str(msg.from_user.id)

    # запись в запрос времени
    with open('requests_info.json', 'r', encoding='utf-8') as json_file:
        existing_data = json.load(json_file)

    rate_kp = rate_kp_decoder[msg.text]

    if rate_kp not in existing_data[id]['rate_kp']:
        existing_data[id]['rate_kp'].append(rate_kp)
    else:
        await msg.reply("Ой! Ты уже выбрал данный элемент! Попробуй другой вариант и продолжим поиск фильма! 🎬🌟😊")

    with open('requests_info.json', 'w', encoding='utf-8') as json_file:
        json.dump(existing_data, json_file, indent=4, ensure_ascii=False)


# обработка нажатий на клавиатуру с выбором рейтинга на IMDB
@dp.message_handler(lambda msg: msg.text in strings.rate_imdb[:-1])
async def rate_imdb_handler(msg: types.Message):

    id = str(msg.from_user.id)

    # запись в запрос времени
    with open('requests_info.json', 'r', encoding='utf-8') as json_file:
        existing_data = json.load(json_file)

    rate_imdb = rate_imdb_decoder[msg.text]

    if rate_imdb not in existing_data[id]['rate_imdb']:
        existing_data[id]['rate_imdb'].append(rate_imdb)
    else:
        await msg.reply("Ой! Ты уже выбрал данный элемент! Попробуй другой вариант и продолжим поиск фильма! 🎬🌟😊")        

    with open('requests_info.json', 'w', encoding='utf-8') as json_file:
        json.dump(existing_data, json_file, indent=4, ensure_ascii=False)


# обработка нажатия на клавишу "Далее >>"
@dp.message_handler(lambda msg: msg.text == "Далее >>")
async def continue_handler(msg: types.Message):

    id = str(msg.from_user.id)

    with open('requests_info.json', 'r', encoding='utf-8') as json_file:
        existing_data = json.load(json_file)

    if existing_data[id]['stage_number'] == 1:
        existing_data[id]['stage_number'] = 2
        await msg.answer("Отлично!", reply_markup=types.ReplyKeyboardRemove())
        await asyncio.sleep(1)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons =  strings.genres
        keyboard.add(*buttons)
        await msg.answer("А как насчет создания атмосферы? Под одеялом с чашкой чая и романтической мелодрамой, или, может быть, с попкорном в руках и адреналином от боевика? В любом случае, выбор за тобой! 😊🎥", reply_markup=keyboard)

    elif existing_data[id]['stage_number'] == 2:
        existing_data[id]['stage_number'] = 3
        await msg.answer("Жанр выбран!", reply_markup=types.ReplyKeyboardRemove())
        await asyncio.sleep(1)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = strings.durations
        keyboard.add(*buttons)
        await msg.answer("Ах, это трудный выбор! 🤔 С одной стороны, \"быстрая порция удовольствия\" звучит заманчиво — короткий фильм, и ты уже в настроении. ⏱️🍿 С другой стороны, наслаждение долгой картиной подарит тебе возможность погрузиться в мир героев и истории. 🌟🎥 Что скажешь?", reply_markup=keyboard)

    elif existing_data[id]['stage_number'] == 3:
        existing_data[id]['stage_number'] = 4
        await msg.answer("Продолжительность выбрана!", reply_markup=types.ReplyKeyboardRemove())
        await asyncio.sleep(1)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = strings.years
        keyboard.add(*buttons)
        await msg.answer("Если бы я выбирал, то, наверное, предпочел бы современную графику и спецэффекты. 🚀🌟 Но, конечно, это зависит от настроения — иногда хочется уютной атмосферы доброй старой кинопленки. Выбор за тобой, и в любом случае оба варианта обещают прекрасно провести время! 😊🍿", reply_markup=keyboard)

    elif existing_data[id]['stage_number'] == 4:
        existing_data[id]['stage_number'] = 5
        await msg.answer("Эпоха выбрана!", reply_markup=types.ReplyKeyboardRemove())
        await asyncio.sleep(1)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = strings.ages
        keyboard.add(*buttons)
        await msg.answer("Раздумываем, устроить семейный киносеанс или выбрать более взрослый сюжет? 😊🍿 Что насчет возрастного ограничения? 🤔🔞", reply_markup=keyboard)

    elif existing_data[id]['stage_number'] == 5:
        existing_data[id]['stage_number'] = 6
        await msg.answer("Возрастное ограничение выбрано!", reply_markup=types.ReplyKeyboardRemove())
        await asyncio.sleep(1)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = strings.rate_kp
        keyboard.add(*buttons)
        await msg.answer("Если бы я мог выбирать, то, наверное, предпочел бы фильм с рейтингом на КиноПоиске от 7 и выше, чтобы иметь хорошие шансы на интересное кино. 🌟🎥 Однако, как мы знаем, рейтинги могут быть субъективными, и иногда даже фильмы с низким рейтингом могут приятно удивить. 😊🍿", reply_markup=keyboard)

    elif existing_data[id]['stage_number'] == 6:
        existing_data[id]['stage_number'] = 7
        await msg.answer("Рейтинг на КиноПоиске выбран!", reply_markup=types.ReplyKeyboardRemove())
        await asyncio.sleep(1)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = strings.rate_imdb
        keyboard.add(*buttons)
        await msg.answer("Если говорить о рейтинге на IMDB — всемирно известной киноплатформе, то важно помнить, что, как и в предыдущем пункте, рейтинги составляются людьми и могут не всегда отражать реальное качество фильма. Рейтинги это всего лишь один из аспектов, и важнее всего — наслаждаться просмотром! 😊🍿", reply_markup=keyboard)

    with open('requests_info.json', 'w', encoding='utf-8') as json_file:
        json.dump(existing_data, json_file, indent=4, ensure_ascii=False)


# обработка нажатия на клавишу "Далее >>"
@dp.message_handler(lambda msg: msg.text == "Готово")
async def done_handler(msg: types.Message):
    global cursor
    try:
        await msg.answer("Начинаю поиск, готовься, ведь скоро ты отправишься в увлекательное путешествие по миру кино! 🕵️‍♂️🎥", reply_markup=types.ReplyKeyboardRemove())
        id = str(msg.from_user.id)

        with open('requests_info.json', 'r', encoding='utf-8') as json_file:
            existing_data = json.load(json_file)

        if len(existing_data[id]["genre"]) == 0 or "Любой 📽️" in existing_data[id]["genre"]:
            genre_list = ["биография", "боевик", "вестерн", "военный", "детектив", "мульт", "док", "драма", "история", "комедия", "криминал", "мелодрама", "мюзикл", "приключения", "семейный", "спорт", "триллер", "ужасы", "фантастика", "фэнтези"]
        else:
            genre_list = existing_data[id]["genre"]    

        if len(existing_data[id]["country"]) == 0 or "Любая" in existing_data[id]["country"]:
            country_list = ["Россия", "США", "Британия", "Германия", "Франция", "Испания", "Италия"]
        else:
            country_list = existing_data[id]["country"]

        if len(existing_data[id]["age_limit"]) == 0 or "Любое 🆗" in existing_data[id]["age_limit"]:
            age_list = ["0", "6", "12", "16", "18"]
        else:
            age_list = existing_data[id]["age_limit"]

        duration_range = duration_converter(existing_data[id]["duration"])
        year_range = year_converter(existing_data[id]["year"])
        min_kp = rate_kp_converter(existing_data[id]["rate_kp"])
        min_imdb = rate_imdb_converter(existing_data[id]["rate_imdb"])

        query = "SELECT * FROM films WHERE " + \
            "(" + " OR ".join(["country LIKE ?"] * len(country_list)) + ")" + \
            " AND " + \
            "(" + " OR ".join(["genre LIKE ?"] * len(genre_list)) + ")" + \
            " AND " + \
            "duration >= ? AND duration <= ?" + \
            " AND " + \
            "year >= ? AND year <= ?" + \
            " AND " + \
            "(" + " OR ".join(["age_limit LIKE ?"] * len(age_list)) + ")" + \
            " AND " + \
            "rate_kp >= ?" + \
            " AND " + \
            "rate_imdb >= ?"

        countries = ["%" + item + "%" for item in country_list]
        genres = ["%" + item + "%" for item in genre_list]
        ages = ["%" + item + "%" for item in age_list]
        rates = [float(min_kp), float(min_imdb)]
        result = cursor.execute(query, countries + genres + duration_range + year_range + ages + rates).fetchall()

        if result:
            existing_data[id]["films_list"] = [x[0] for x in result if x[0] not in existing_data[id]["viewed"]]
            
            for film in result:
                if film[0] not in existing_data[id]["viewed"]:
                    name = f"<i>{film[1]}</i> ({film[4]})"
                    genre = f"<b>Жанры:</b> <i>{', '.join(film[2].split(';'))}</i>"
                    duration = f"<b>{human_duration(film[3])}</b>"
                    country = f"<b>Страны-производители:</b> <i>{', '.join(film[5].split(';'))}</i>"
                    rate_kp = f"<b>Рейтинг на КиноПоиске:</b> {film[6]}"
                    rate_imdb = f"<b>Рейтинг на IMDB:</b> {film[7]}"
                    age_limit = f"<b>Возрастное ограничение: {film[11]}+</b>"
                    description = f"<i>{film[8]}</i>"
                    trailer_link = "<u><a href='" + film[9] + "'>Посмотреть трейлер</a></u>"
                    soundtrack_link = "<u><a href='" + film[10] + "'>Послушать саундтрек</a></u>"

                    message = f"🎬 {name}\n"
                    message += f"🌍 {country}\n"
                    message += f"🎶 {genre}\n"
                    message += f"⏱️ {duration}\n"
                    message += f"🔞 {age_limit}\n\n"
                    message += f"{description}\n\n"
                    message += f"📊 {rate_kp}\n"
                    message += f"📈 {rate_imdb}\n\n"
                    message += f"🎥 {trailer_link}\n"
                    message += f"🎵 {soundtrack_link}"

                    photo_name = get_image_from_url(film[13])
                    existing_data[id]["current"] = film[0]
                    keyboard = types.InlineKeyboardMarkup(row_width=2)
                    keyboard.add(types.InlineKeyboardButton(text="Просмотрен ✅", callback_data="viewed"))
                    keyboard.add(types.InlineKeyboardButton(text="Не рекомендовать ❌", callback_data="bad_recommendation"))
                    keyboard.add(types.InlineKeyboardButton(text="Еще вариант ➡️", callback_data="next_film"))
                    with open(photo_name, "rb") as photo_file:
                        await bot.send_photo(chat_id=msg.chat.id, photo=types.InputFile(photo_file), caption=message, parse_mode="HTML", reply_markup=keyboard)
                    os.remove(photo_name)
                    break
            else:
                await msg.answer("Ой! 😊 К сожалению, в нашей базе закончились ленты, соответствующие вашему запросу. Но не переживайте! 🎬 Мы усердно расширяем нашу базу фильмов и работаем для вашего удобства! В скором времени здесь появятся новые интересные киноленты! 🎉")
                    
        else:
            await msg.answer("Ой! 😊 К сожалению, пока нет фильмов, соответствующих вашему запросу. Но не переживайте! 🎬 Мы усердно расширяем нашу базу фильмов и работаем для вашего удобства! В скором времени здесь появятся новые интересные киноленты! 🎉 \nДавай попробуем ещё раз. Введи команду /film, и мы начнем поиск! Помни: чем больше вариантов ты выберешь на каждом этапе, тем больше шансов на успешный результат! 😊🔍")
            with open("bad_requests.txt", 'a', encoding="utf-8") as text_file:
                text_file.write(str(existing_data[id]))
                text_file.write("\n")

        with open('requests_info.json', 'w', encoding='utf-8') as json_file:
            json.dump(existing_data, json_file, indent=4, ensure_ascii=False)

    except Exception as e:
        await msg.answer("Ой, кажется, что-то пошло не так! Но не волнуйтесь, наши разработчики уже уведомлены об ошибке и активно работают над её устранением. Искренне извиняемся за неудобства! Мы стараемся сделать всё возможное, чтобы улучшить наш сервис. 😊🛠️")
        with open("errors.txt", 'a', encoding="utf-8") as text_file:
            text_file.write(str(e) + str(existing_data[id]))
            text_file.write("\n")


@dp.message_handler(commands=['search'])
async def search_handler(msg: types.Message):

    id = str(msg.from_user.id)
    
    await msg.reply("Введите название фильма, и я попробую найти его в своей базе данных! 😊🎬")

    with open('requests_info.json', 'r', encoding='utf-8') as json_file:
        existing_data = json.load(json_file)
    
    existing_data[id]["search"] = True

    with open('requests_info.json', 'w', encoding='utf-8') as json_file:
        json.dump(existing_data, json_file, indent=4, ensure_ascii=False)    


@dp.message_handler()
async def all_handler(msg: types.Message):
    try:
        with open('requests_info.json', 'r', encoding='utf-8') as json_file:
            existing_data = json.load(json_file)

        id = str(msg.from_user.id)

        if existing_data[id]["search"]:
            film_name_cap = f"%{msg.text.capitalize()}%"
            film_name = f"%{msg.text}%"
            query = "SELECT * FROM films WHERE name LIKE ? OR name LIKE ?"
            result = cursor.execute(query, (film_name_cap, film_name)).fetchall()

            if len(result) > 0:
                for film in result:
                    name = f"<i>{film[1]}</i> ({film[4]})"
                    genre = f"<b>Жанры:</b> <i>{', '.join(film[2].split(';'))}</i>"
                    duration = f"<b>{human_duration(film[3])}</b>"
                    country = f"<b>Страны-производители:</b> <i>{', '.join(film[5].split(';'))}</i>"
                    rate_kp = f"<b>Рейтинг на КиноПоиске:</b> {film[6]}"
                    rate_imdb = f"<b>Рейтинг на IMDB:</b> {film[7]}"
                    age_limit = f"<b>Возрастное ограничение: {film[11]}+</b>"
                    description = f"<i>{film[8]}</i>"
                    trailer_link = "<u><a href='" + film[9] + "'>Посмотреть трейлер</a></u>"
                    soundtrack_link = "<u><a href='" + film[10] + "'>Послушать саундтрек</a></u>"

                    message = f"🎬 {name}\n"
                    message += f"🌍 {country}\n"
                    message += f"🎶 {genre}\n"
                    message += f"⏱️ {duration}\n"
                    message += f"🔞 {age_limit}\n\n"
                    message += f"{description}\n\n"
                    message += f"📊 {rate_kp}\n"
                    message += f"📈 {rate_imdb}\n\n"
                    message += f"🎥 {trailer_link}\n"
                    message += f"🎵 {soundtrack_link}"

                    photo_name = get_image_from_url(film[13])
                    existing_data[id]["current"] = film[0]
                    keyboard = types.InlineKeyboardMarkup(row_width=2)
                    keyboard.add(types.InlineKeyboardButton(text="Просмотрен ✅", callback_data="viewed"))
                    with open(photo_name, "rb") as photo_file:
                        await bot.send_photo(chat_id=msg.chat.id, photo=types.InputFile(photo_file), caption=message, parse_mode="HTML", reply_markup=keyboard)
                    os.remove(photo_name)
            else:
                await msg.reply("Ой! 😊 К сожалению, пока нет фильмов, соответствующих вашему запросу. Но не переживайте! 🎬 Мы усердно расширяем нашу базу фильмов и работаем для вашего удобства! В скором времени здесь появятся новые интересные киноленты! 🎉")

        else:
            await msg.reply("Если у вас возникли затруднения с точным названием команды, просто введите /help — и я с удовольствием помогу! 😊🔍")
    
    except Exception as e:
        await msg.answer("Ой, кажется, что-то пошло не так! Но не волнуйтесь, наши разработчики уже уведомлены об ошибке и активно работают над её устранением. Искренне извиняемся за неудобства! Мы стараемся сделать всё возможное, чтобы улучшить наш сервис. 😊🛠️")
        with open("errors.txt", 'a', encoding="utf-8") as text_file:
            text_file.write(str(e) + ' ' + msg.text)
            text_file.write("\n")


@dp.callback_query_handler(text="viewed")
async def viewed_handler(call: types.CallbackQuery):
    try:
        id = str(call.from_user.id)
        flag = True
        with open('requests_info.json', 'r', encoding='utf-8') as json_file:
            existing_data = json.load(json_file)

        if not existing_data[id]["search"]:
            await call.message.answer("Фильм добавлен в просмотренные!")
            await call.message.answer("Ищу новый...")
            existing_data[id]["viewed"].append(existing_data[id]["current"])
            existing_data[id]["films_list"].pop(0)
            if len(existing_data[id]["films_list"]) > 0:
                existing_data[id]["current"] = existing_data[id]["films_list"][0]
            else:
                flag = False
            await call.answer()
            await call.message.edit_reply_markup(reply_markup=None)

            if flag:
                query = "SELECT * FROM films WHERE id = ?"
                result = cursor.execute(query, (existing_data[id]["current"],)).fetchall()
                film = result[0]
                name = f"<i>{film[1]}</i> ({film[4]})"
                genre = f"<b>Жанры:</b> <i>{', '.join(film[2].split(';'))}</i>"
                duration = f"<b>{human_duration(film[3])}</b>"
                country = f"<b>Страны-производители:</b> <i>{', '.join(film[5].split(';'))}</i>"
                rate_kp = f"<b>Рейтинг на КиноПоиске:</b> {film[6]}"
                rate_imdb = f"<b>Рейтинг на IMDB:</b> {film[7]}"
                age_limit = f"<b>Возрастное ограничение: {film[11]}+</b>"
                description = f"<i>{film[8]}</i>"
                trailer_link = "<u><a href='" + film[9] + "'>Посмотреть трейлер</a></u>"
                soundtrack_link = "<u><a href='" + film[10] + "'>Послушать саундтрек</a></u>"

                message = f"🎬 {name}\n"
                message += f"🌍 {country}\n"
                message += f"🎶 {genre}\n"
                message += f"⏱️ {duration}\n"
                message += f"🔞 {age_limit}\n\n"
                message += f"{description}\n\n"
                message += f"📊 {rate_kp}\n"
                message += f"📈 {rate_imdb}\n\n"
                message += f"🎥 {trailer_link}\n"
                message += f"🎵 {soundtrack_link}"

                photo_name = get_image_from_url(film[13])
                existing_data[id]["current"] = film[0]
                keyboard = types.InlineKeyboardMarkup(row_width=2)
                keyboard.add(types.InlineKeyboardButton(text="Просмотрен ✅", callback_data="viewed"))
                keyboard.add(types.InlineKeyboardButton(text="Не рекомендовать ❌", callback_data="bad_recommendation"))
                keyboard.add(types.InlineKeyboardButton(text="Еще вариант ➡️", callback_data="next_film"))
                with open(photo_name, "rb") as photo_file:
                    await bot.send_photo(chat_id=call.message.chat.id, photo=types.InputFile(photo_file), caption=message, parse_mode="HTML", reply_markup=keyboard)
                os.remove(photo_name)

            else:
                await call.message.answer("К сожалению, по твоему запросу больше ничего нет. Не переживай, попробуй другой запрос! 🕵️‍♂️🔍")
        else:
            await call.message.answer("Фильм добавлен в просмотренные!")
            existing_data[id]["search"] = False
            if existing_data[id]["current"] not in existing_data[id]["viewed"]:
                existing_data[id]["viewed"].append(existing_data[id]["current"])
            existing_data[id]["films_list"].pop(0)
            await call.answer()
            await call.message.edit_reply_markup(reply_markup=None)

        with open('requests_info.json', 'w', encoding='utf-8') as json_file:
            json.dump(existing_data, json_file, indent=4, ensure_ascii=False)

    except Exception as e:
        await call.answer("Ой, кажется, что-то пошло не так! Но не волнуйтесь, наши разработчики уже уведомлены об ошибке и активно работают над её устранением. Искренне извиняемся за неудобства! Мы стараемся сделать всё возможное, чтобы улучшить наш сервис. 😊🛠️")
        with open("errors.txt", 'a', encoding="utf-8") as text_file:
            text_file.write(str(e) + str(existing_data[id]))
            text_file.write("\n")


@dp.callback_query_handler(text="bad_recommendation")
async def bad_recommendation_handler(call: types.CallbackQuery):
    try:
        id = str(call.from_user.id)
        flag = True
        with open('requests_info.json', 'r', encoding='utf-8') as json_file:
            existing_data = json.load(json_file)

        if not existing_data[id]["search"]:
            await call.message.answer("Фильм больше не попадет к тебе в рекомендации")
            await call.message.answer("Ищу новый...")
            existing_data[id]["viewed"].append(existing_data[id]["current"])
            existing_data[id]["films_list"].pop(0)
            if len(existing_data[id]["films_list"]) > 0:
                existing_data[id]["current"] = existing_data[id]["films_list"][0]
            else:
                flag = False
            await call.answer()
            await call.message.edit_reply_markup(reply_markup=None)

            if flag:
                query = "SELECT * FROM films WHERE id = ?"
                result = cursor.execute(query, (existing_data[id]["current"],)).fetchall()
                film = result[0]
                name = f"<i>{film[1]}</i> ({film[4]})"
                genre = f"<b>Жанры:</b> <i>{', '.join(film[2].split(';'))}</i>"
                duration = f"<b>{human_duration(film[3])}</b>"
                country = f"<b>Страны-производители:</b> <i>{', '.join(film[5].split(';'))}</i>"
                rate_kp = f"<b>Рейтинг на КиноПоиске:</b> {film[6]}"
                rate_imdb = f"<b>Рейтинг на IMDB:</b> {film[7]}"
                age_limit = f"<b>Возрастное ограничение: {film[11]}+</b>"
                description = f"<i>{film[8]}</i>"
                trailer_link = "<u><a href='" + film[9] + "'>Посмотреть трейлер</a></u>"
                soundtrack_link = "<u><a href='" + film[10] + "'>Послушать саундтрек</a></u>"

                message = f"🎬 {name}\n"
                message += f"🌍 {country}\n"
                message += f"🎶 {genre}\n"
                message += f"⏱️ {duration}\n"
                message += f"🔞 {age_limit}\n\n"
                message += f"{description}\n\n"
                message += f"📊 {rate_kp}\n"
                message += f"📈 {rate_imdb}\n\n"
                message += f"🎥 {trailer_link}\n"
                message += f"🎵 {soundtrack_link}"

                photo_name = get_image_from_url(film[13])
                existing_data[id]["current"] = film[0]
                keyboard = types.InlineKeyboardMarkup(row_width=2)
                keyboard.add(types.InlineKeyboardButton(text="Просмотрен ✅", callback_data="viewed"))
                keyboard.add(types.InlineKeyboardButton(text="Не рекомендовать ❌", callback_data="bad_recommendation"))
                keyboard.add(types.InlineKeyboardButton(text="Еще вариант ➡️", callback_data="next_film"))
                with open(photo_name, "rb") as photo_file:
                    await bot.send_photo(chat_id=call.message.chat.id, photo=types.InputFile(photo_file), caption=message, parse_mode="HTML", reply_markup=keyboard)
                os.remove(photo_name)

            else:
                await call.message.answer("К сожалению, по твоему запросу больше ничего нет. Не переживай, попробуй другой запрос! 🕵️‍♂️🔍")
            with open('requests_info.json', 'w', encoding='utf-8') as json_file:
                json.dump(existing_data, json_file, indent=4, ensure_ascii=False)

    except Exception as e:
        await call.answer("Ой, кажется, что-то пошло не так! Но не волнуйтесь, наши разработчики уже уведомлены об ошибке и активно работают над её устранением. Искренне извиняемся за неудобства! Мы стараемся сделать всё возможное, чтобы улучшить наш сервис. 😊🛠️")
        with open("errors.txt", 'a', encoding="utf-8") as text_file:
            text_file.write(str(e) + str(existing_data[id]))
            text_file.write("\n")


@dp.callback_query_handler(text="next_film")
async def next_film_handler(call: types.CallbackQuery):
    try:
        id = str(call.from_user.id)
        flag = True
        with open('requests_info.json', 'r', encoding='utf-8') as json_file:
            existing_data = json.load(json_file)

        if not existing_data[id]["search"]:
            await call.message.answer("Ищу новый...")
            existing_data[id]["films_list"].pop(0)
            if len(existing_data[id]["films_list"]) > 0:
                existing_data[id]["current"] = existing_data[id]["films_list"][0]
            else:
                flag = False
            await call.answer()
            await call.message.edit_reply_markup(reply_markup=None)

            if flag:
                query = "SELECT * FROM films WHERE id = ?"
                result = cursor.execute(query, (existing_data[id]["current"],)).fetchall()
                film = result[0]
                name = f"<i>{film[1]}</i> ({film[4]})"
                genre = f"<b>Жанры:</b> <i>{', '.join(film[2].split(';'))}</i>"
                duration = f"<b>{human_duration(film[3])}</b>"
                country = f"<b>Страны-производители:</b> <i>{', '.join(film[5].split(';'))}</i>"
                rate_kp = f"<b>Рейтинг на КиноПоиске:</b> {film[6]}"
                rate_imdb = f"<b>Рейтинг на IMDB:</b> {film[7]}"
                age_limit = f"<b>Возрастное ограничение: {film[11]}+</b>"
                description = f"<i>{film[8]}</i>"
                trailer_link = "<u><a href='" + film[9] + "'>Посмотреть трейлер</a></u>"
                soundtrack_link = "<u><a href='" + film[10] + "'>Послушать саундтрек</a></u>"

                message = f"🎬 {name}\n"
                message += f"🌍 {country}\n"
                message += f"🎶 {genre}\n"
                message += f"⏱️ {duration}\n"
                message += f"🔞 {age_limit}\n\n"
                message += f"{description}\n\n"
                message += f"📊 {rate_kp}\n"
                message += f"📈 {rate_imdb}\n\n"
                message += f"🎥 {trailer_link}\n"
                message += f"🎵 {soundtrack_link}"

                photo_name = get_image_from_url(film[13])
                existing_data[id]["current"] = film[0]
                keyboard = types.InlineKeyboardMarkup(row_width=2)
                keyboard.add(types.InlineKeyboardButton(text="Просмотрен ✅", callback_data="viewed"))
                keyboard.add(types.InlineKeyboardButton(text="Не рекомендовать ❌", callback_data="bad_recommendation"))
                keyboard.add(types.InlineKeyboardButton(text="Еще вариант ➡️", callback_data="next_film"))
                with open(photo_name, "rb") as photo_file:
                    await bot.send_photo(chat_id=call.message.chat.id, photo=types.InputFile(photo_file), caption=message, parse_mode="HTML", reply_markup=keyboard)
                os.remove(photo_name)

            else:
                await call.message.answer("К сожалению, по твоему запросу больше ничего нет. Не переживай, попробуй другой запрос! 🕵️‍♂️🔍")
            with open('requests_info.json', 'w', encoding='utf-8') as json_file:
                json.dump(existing_data, json_file, indent=4, ensure_ascii=False)

    except Exception as e:
        await call.answer("Ой, кажется, что-то пошло не так! Но не волнуйтесь, наши разработчики уже уведомлены об ошибке и активно работают над её устранением. Искренне извиняемся за неудобства! Мы стараемся сделать всё возможное, чтобы улучшить наш сервис. 😊🛠️")
        with open("errors.txt", 'a', encoding="utf-8") as text_file:
            text_file.write(str(e) + str(existing_data[id]))
            text_file.write("\n")


# конвертер продолжительности в удобный формат
def duration_converter(duration_list):
    duration_list.sort()
    range = [0, 1000]

    if len(duration_list) == 0 or "Любая ⏱️" in duration_list:
        return range
    if duration_list == ["1-2 часа"]:
        range = [40, 120]
    elif duration_list == ["2-3 часа"]:
        range = [120, 180]
    elif duration_list == ["более 3 часов"]:
        range = [180, 1000]
    elif duration_list == ["1-2 часа", "2-3 часа"]:
        range = [40, 180]
    elif duration_list == ["1-2 часа", "2-3 часа", "более 3 часов"] or duration_list == ["1-2 часа", "более 3 часов"]:
        range = [40, 1000]
    elif duration_list == ["2-3 часа", "более 3 часов"]:
        range = [120, 1000]
    return range


# конвертер года съемки в удобный формат
def year_converter(year_list):
    year_list.sort()
    range = [1900, 2230]

    if len(year_list) == 0:
        return range
    if "до 1970-х" in year_list:
        range[0] = 1900
        if len(year_list) == 1:
            return [1900, 1970]
        year_list.remove("до 1970-х")
        year_list.sort()
    if "Любой ⏳" in year_list:
        return [1900, 2230]
    else:
        range[0] = int(year_list[0].split("-")[0])
    if "2020-" in year_list:
        range[1] = 2230
    else:
        range[1] = int(year_list[-1].split("-")[1])
    return range


# конвертер возрастного ограничения в удобный формат
def age_converter(age_list):
    age_list.sort()
    age_value = 0

    if len(age_list) == 0 or "Любое 🆗" in age_list:
        return age_value
    age_value = int(age_list[0].split("+")[0])
    return age_value


# конвертер рейтинга на КиноПоиске в удобный формат
def rate_kp_converter(rate_list):
    only_rate_list = [int(value.split()[-1].split("+")[0]) for value in rate_list if value != "Любой ➡️"]
    if len(only_rate_list) < len(rate_list) or len(rate_list) == 0:
        return 0
    only_rate_list.sort()
    return min(only_rate_list)


# конвертер рейтинга на IMDB в удобный формат
def rate_imdb_converter(rate_list):
    only_rate_list = [int(value.split()[-1].split("+")[0]) for value in rate_list if value != "Любой ✅"]
    if len(only_rate_list) < len(rate_list) or len(rate_list) == 0:
        return 0
    only_rate_list.sort()
    return min(only_rate_list)


# запуск бота
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)