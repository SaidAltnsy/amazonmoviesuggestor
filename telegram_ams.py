import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, ConversationHandler, \
    MessageHandler, Filters
import pandas as pd
import random
import config

df = pd.read_csv('amazon_movie_final.csv')
df = df.drop(columns=['Unnamed: 0'])


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# stages
STAGE_CHOICE, LIST_FILTERS, STAGE_FILTERS, GET_TEXT = range(4)
stage_start = ['FILTER_SELECTION', 'RANDOM_SUGGESTION']
stage_filters = ['Genre', 'Year', 'Rating', 'ages', 'person']

genres = ['Action', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Romance', 'Thriller', 'War', 'History', 'Paranormal', 'Western']

ratings = ['8-10', '5-8', '0-5']
years = ['2021', '2015-2020', '2010-2015', '2000-2010', '1920-2000']
f_list = []
person1 = {'name': ''}


def start(update: Update, context: CallbackContext) -> None:
    f_list.clear()
    keyboard = [
        [InlineKeyboardButton('Search Movie 🎥', callback_data=stage_start[0]),
         InlineKeyboardButton('Suggest Random Movie', callback_data=stage_start[1])],

    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        'Welcome to the Easy Movie Finder; You can search among 100,000 movies and previews.',
        reply_markup=reply_markup)
    return STAGE_CHOICE


def select_filters(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    if query.data == 'clear all':
        f_list.clear()
    keyboard = [

        [InlineKeyboardButton('Genre 🎬', callback_data=stage_filters[0]),
         InlineKeyboardButton('Year 📆', callback_data=stage_filters[1]),
         InlineKeyboardButton('Rating 👍🏼', callback_data=stage_filters[2]),
         ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text(text='Choose filters you want to search', reply_markup=reply_markup)

    return STAGE_FILTERS


def genre(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    keyboard2 = []
    keyboard = []
    for j in range(len(genres)):
        keyboard.append(InlineKeyboardButton(genres[j], callback_data=genres[j]))
        if j % 3 == 2:
            keyboard2.append(keyboard)
            keyboard = []
    keyboard2.append(keyboard)

    reply_markup = InlineKeyboardMarkup(keyboard2)

    query.edit_message_text(text='Please choose one of the following genres:', reply_markup=reply_markup)

    return LIST_FILTERS


def rating(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    keyboard2 = []
    keyboard = []
    for j in range(len(ratings)):
        keyboard.append(InlineKeyboardButton(ratings[j], callback_data=ratings[j]))
        if j % 3 == 2:
            keyboard2.append(keyboard)
            keyboard = []
    keyboard2.append(keyboard)

    reply_markup = InlineKeyboardMarkup(keyboard2)

    query.edit_message_text(text='Please choose rating:', reply_markup=reply_markup)
    return LIST_FILTERS


def year(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    keyboard2 = []
    keyboard = []
    for j in range(len(years)):
        keyboard.append(InlineKeyboardButton(years[j], callback_data=years[j]))
        if j % 3 == 2:
            keyboard2.append(keyboard)
            keyboard = []
    keyboard2.append(keyboard)
    reply_markup = InlineKeyboardMarkup(keyboard2)

    query.edit_message_text(text='Please choose year:', reply_markup=reply_markup)
    return LIST_FILTERS


def get_person(update: Update, context: CallbackContext) -> None:
    person1['name'] = update.message.text.lower()
    lst = df.Actors.tolist()
    lst_lower = [x.lower() for x in lst]
    elem = person1['name']
    flm = []
    for i in range(len(lst_lower)):
        if elem in lst_lower[i]:
            flm.append(i)
    j = random.randint(0, len(flm) - 1)
    movie = df.iloc[flm[j]].tolist()
    keyboard = [
        [InlineKeyboardButton('Go to Movie', url=movie[4]),
         InlineKeyboardButton('Back to filters', callback_data='FILTER_SELECTION')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(text='*FILM NAME*:  ' + str(
        movie[0]) + '\n' + '*YEAR*:  ' + str(movie[1]) + '\n' + '*DURATION*:  ' + str(
        movie[2]) + ' minutes' + '\n' + '*ACTORS*: ' + (
                                       str(movie[3]).strip('[]/""').replace("'", "")) + '\n' + '*GENRE*: ' + str(
        movie[5]) + '\n' + '*PRICE*: ' + str(movie[8]) + '\n' + '*RATING*: ' + str(movie[9]) + '\n' + str(movie[7]),
                              parse_mode='Markdown', reply_markup=reply_markup)

    return STAGE_CHOICE


def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Use /start to test this bot.")


def main():
    updater = Updater(config.TELEGRAM_TOKEN, use_context=True)

    dispatcher = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            STAGE_CHOICE: [
                CallbackQueryHandler(select_filters, pattern='^' + stage_start[0] + '$'),
                CallbackQueryHandler(select_filters, pattern='^' + 'clear all' + '$'),
                CallbackQueryHandler(get_movie, pattern='^' + 'Search Movie' + '$'),
                CallbackQueryHandler(genre, pattern='^' + 'genre' + '$'),
                CallbackQueryHandler(get_movie),

            ],
            LIST_FILTERS: [
                CallbackQueryHandler(filter_list),
            ],
            STAGE_FILTERS: [
                #CallbackQueryHandler(person, pattern='^' + 'PERSON' + '$'),
                CallbackQueryHandler(genre, pattern='^' + stage_filters[0] + '$'),
                CallbackQueryHandler(rating, pattern='^' + stage_filters[2] + '$'),
                CallbackQueryHandler(year, pattern='^' + stage_filters[1] + '$'),
                    ],
            GET_TEXT: [
                MessageHandler(Filters.text, get_person),
                    ],
        },
        fallbacks=[CommandHandler('start', start)],
    )

    dispatcher.add_handler(conv_handler)
    # Starting the Bot
    updater.start_polling()

    updater.idle()


def filter_list(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    if query.data not in f_list:
        f_list.append(query.data)
    keyboard = [
        [InlineKeyboardButton('Add another filter', callback_data=stage_start[0]),
         InlineKeyboardButton('Clear all filters', callback_data='clear all'), ],
        [InlineKeyboardButton('Search Movie', callback_data='Search Movie')]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    gnr_lst = []
    yr_lst = []
    rtng_lst = []
    for i in range(len(f_list)):
        if f_list[i] in genres:
            gnr_lst.append(f_list[i])
        elif f_list[i] in years:
            yr_lst.append(f_list[i])
        elif f_list[i] in ratings:
            rtng_lst.append(f_list[i])

    query.edit_message_text(
        'Selected filters:' + '\n' + '*SELECTED GENRES:* ' + str(gnr_lst).replace("'",
                                                                                  "") + '\n' + '*SELECTED YEARS:* ' + str(
            yr_lst).replace("'", "") + '\n' + '*SELECTED RATINGS:* ' + str(rtng_lst).replace("'", ""),
        parse_mode='Markdown',
        reply_markup=reply_markup)
    return STAGE_CHOICE


def get_movie(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    # print(query)
    gen_len = len(f_list)

    if gen_len == 0:
        movie = df.sample(1).iloc[0].tolist()
    else:

        lst_genre = []
        lst_year = []
        lst_rating = []
        for i in range(gen_len):

            if f_list[i] in genres:
                df1 = df[df.Genre == str(f_list[i])]
                lst_genre.append(df1)

            elif f_list[i] in years:

                mn = f_list[i].split('-')
                df2 = df[(df.Year <= int(mn[-1])) & (df.Year > int(mn[0]))]
                lst_year.append(df2)

            elif f_list[i] in ratings:
                mn = f_list[i].split('-')
                df3 = df[(df.Ratings <= float(mn[-1])) & (df.Ratings > float(mn[0]))]
                lst_rating.append(df3)
        if len(lst_genre) > 0:
            df1 = pd.concat(lst_genre)
        elif len(lst_genre) == 0:
            df1 = df
        if len(lst_year) > 0:
            df2 = pd.concat(lst_year)
        elif len(lst_year) == 0:
            df2 = df
        if len(lst_rating) > 0:
            df3 = pd.concat(lst_rating)
        elif len(lst_rating) == 0:
            df3 = df

        try:
            movie = pd.concat([df1, df2, df3], ignore_index=True, axis=1, join="inner").sample(1).iloc[0].tolist()
        except:
            f_list.clear()
            keyboard = [
                [InlineKeyboardButton('Search movie', callback_data='FILTER_SELECTION'),
                 InlineKeyboardButton('Suggest random movie', callback_data='RANDOM_SUGGESTION')]

            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.edit_message_text(text='It does not match any film, please back to filters. ',
                                    reply_markup=reply_markup)
            return STAGE_CHOICE

    keyboard = [
        [InlineKeyboardButton('Go to Movie', url=movie[6]),
         InlineKeyboardButton('Suggest another', callback_data='Search Movie'),
         InlineKeyboardButton('Back to filters', callback_data='clear all')],
        [InlineKeyboardButton('Try free 1 month Amazon Prime Watch', url='http://www.amazon.co.uk/tryprimefree?tag=moviefinder-tg-21')],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text='*FILM NAME*:  ' + str(
        movie[0]) + '\n' + '*YEAR*:  ' + str(movie[1]) + '\n' + '*DURATION*:  ' + str(
        movie[2]) + ' minutes' + '\n' + '*GENRE*: ' + str(
        movie[5]) + '\n' + '*RATING*: ' + str(movie[4]) + '\n' + str(movie[6]),
                            parse_mode='Markdown', reply_markup=reply_markup)
    return STAGE_CHOICE


if __name__ == '__main__':
    main()
