from flashtext import KeywordProcessor
import re


def prepare_text(text):
    # text = text.replace(r'`', '')
    text = re.sub(r'(\d+) (\d+)', r'\1\2', text)
    # text = re.sub(r'(\d+)([кk]?)\s?-\s?(\d+)([кk]?)', r'\1\2-\3\4', text)
    text = re.sub(r'(от )?(\d+)\s?[кk]?\s?(-|до)\s?(\d+)\s?[кk]', r'\g<2>000-\g<4>000', text)
    text = re.sub(r'(\d+)\s?[kк]', r'\g<1>000', text)
    text = re.sub(r'[*?._\'\"#` ]+', r' ', text)
    number_symbols = {'1️⃣': '1',
                      '2️⃣': '2',
                      '3️⃣': '3',
                      '4️⃣': '4',
                      '5️⃣': '5',
                      '6️⃣': '6',
                      '7️⃣': '7',
                      '8️⃣': '8',
                      '9️⃣': '9',
                      '0️⃣': '0',
                      '➕': '+'}
    # pattern = re.compile(r'\b(' + '|'.join(number_symbols.keys()) + r')\b')
    pattern = re.compile(u'1️⃣|2️⃣|3️⃣|4️⃣|5️⃣|6️⃣|7️⃣|8️⃣|9️⃣|0️⃣|➕')
    text = pattern.sub(lambda x: number_symbols[x.group()], text)
    # text = re.sub(u'1️⃣ | 2 | 2️⃣ | 4 | 5️⃣ | 6 | 7 | 8 | 9️⃣ |0️⃣', convert_number_symbols, text) #
    # print(text)
    return text


class Filter:
    f_type = ''

    @classmethod
    def get_text_repr(cls, params: dict):
        return ''

    @classmethod
    def get_value(cls, text: str):
        return []

    @classmethod
    def get_db_repr(cls, *args):
        return {}

    @classmethod
    def apply(cls, text):
        return prepare_text(text)


class KeywordFilter(Filter):
    keyword_dict = {}
    keyword_list = []
    exclude_keywords = []

    # processor: KeywordProcessor = None

    param_names = []

    # def __init__(self):
    #     self.processor = KeywordProcessor()
    #     self.processor.add_keywords_from_dict(self.keyword_dict)
    #     self.processor.add_keywords_from_list(self.keyword_list)

    # def apply(self, text):
    #     self.processor = KeywordProcessor()
    #     self.processor.add_keywords_from_dict(self.keyword_dict)
    #     self.processor.add_keywords_from_list(self.keyword_list)
    #     return self.processor.extract_keywords(text)

    @classmethod
    def apply(cls, text):
        processor = KeywordProcessor()
        processor.add_keywords_from_dict(cls.keyword_dict)
        processor.add_keywords_from_list(cls.keyword_list)
        exc_processor = KeywordProcessor()
        exc_processor.add_keywords_from_list(cls.exclude_keywords)
        # TODO must return bool
        text = prepare_text(text)
        if keywords := processor.extract_keywords(text):
            return keywords, exc_processor.extract_keywords(text)
        return [], []

    @classmethod
    def get_text_repr(cls, params: dict):
        return "print method is not defined"


class RegexFilter(Filter):
    regex_list = []
    param_names = []

    @classmethod
    def apply(cls, text):
        text = prepare_text(text)
        if text:
            for regex in cls.regex_list:
                res = re.search(regex, text, re.IGNORECASE)
                if res is not None:
                    return res.group(0)
        return None

    @classmethod
    def get_text_repr(cls, params: dict):
        return "print method is nt defined"


class MultipleChannelsFilter(KeywordFilter):
    keywords = ['каналы']


class BuyChannel(RegexFilter):
    regex_list = [r'куп(лю|им|аю|ка|ку)[*$+,-.]*\s+((?!в )\w*,?\s*){1,5}(крипто)?(канал|чат|акк|траф|подписк)[*$+,-.]*',
                  ]


class BuyOrder(KeywordFilter):
    # keyword_list = ['куплю рекламу',
    #                 'купаю рекламу',
    #                 'купаю гарь',
    #                 'куплю гарь',
    #                 '#куплюрекламу',
    #                 '#покупкарекламы',
    #                 'покупка рекламы',  # тоже подтягивает рекламу иногда
    #                 'куплю на тест',
    #                 'куплю на 1',
    #                 'куплю на 2',
    #                 'куплю на 3',
    #                 'куплю на 4',
    #                 'куплю на 5',
    #                 'куплю на 6',
    #                 'куплю на 7',
    #                 'куплю на 8',
    #                 'куплю на 9',
    #                 'куплю на 0',
    #                 'возьму на 1',
    #                 'возьму на 2',
    #                 'возьму на 3',
    #                 'возьму на 4',
    #                 'возьму на 5',
    #                 'возьму на 6',
    #                 'возьму на 7',
    #                 'возьму на 8',
    #                 'возьму на 9',
    #                 'возьму на 0',
    #                 'возьму на сегодня',
    #                 'куплю на сегодня',
    #                 'купаю на сегодня',
    #                 'возьму на завтра',
    #                 'куплю на завтра',
    #                 'купаю на завтра',
    #                 'возьму на сейчас',
    #                 'возьму на щас',
    #                 'куплю на щас',
    #                 'купаю на щас',
    #                 'куплю на сейчас',
    #                 'купаю на сейчас',
    #                 'куплю сегодня',
    #                 'купаю сегодня',
    #                 'куплю завтра',
    #                 'купаю завтра',
    #                 # 'за пост', # Иногда подтягивает продажи, хз что делать
    #                 'куплю/продам рекламу',
    #                 'возьму в ',  # ????
    #                 'возьму только в ',  # ????
    #                 'возьму исключительно в ',  # ????
    #                 'куплю в ',  # ????
    #                 'куплю только в ',  # ????
    #                 'куплю исключительно в ',  # ????
    #                 'купаю в ',  # ????
    #                 'купаю только в ',  # ????
    #                 'купаю исключительно в ',  # ????                    'куплю в ',  # ????
    #                 'куплю только во ',  # ????
    #                 'куплю исключительно во ',  # ????
    #                 'купаю во ',  # ????
    #                 'купаю только во ',  # ????
    #                 'купаю исключительно во ',  # ????
    #                 # 'куплю в каналах',
    #                 # 'куплю в канале',
    #                 # 'куплю в тематик',
    #                 'куплю все ',
    #                 'купаю все ',
    #                 'возьму все ',
    #                 'куплю всё',
    #                 'купаю всё',
    #                 'возьму всё',
    #                 'куплю утро',
    #                 'купаю утро',
    #                 'куплю день',
    #                 'купаю день',
    #                 'куплю вечер',
    #                 'купаю вечер',
    #                 'куплю ноч',
    #                 'купаю ноч',
    #                 'куплю фулл день',
    #                 'купаю фулл день',
    #                 'куплю мест',
    #                 'возьму мест',
    #                 'рассмотрю мест',
    #                 'куплю одно мест',
    #                 'возьму одно мест',
    #                 'рассмотрю одно мест',
    #                 'куплю горящие мест',
    #                 'куплю свободные мест',
    #                 'купаю свободные мест',
    #                 'купаю горящие мест',
    #                 'купаю мест',
    #                 'ищу мест',
    #                 'куплю несколько мест',
    #                 'куплю рекламн',  # типа место
    #                 'купаю рекламн',  # типа место
    #                 'купаю несколько мест',
    #                 'куплю строк',
    #                 'куплю много строк',
    #                 'купаю строк',
    #                 'купаю много строк',
    #                 'ищу строк',
    #                 'куплю на понедельник',
    #                 'купаю на понедельник',
    #                 'куплю на вторник',
    #                 'купаю на вторник',
    #                 'куплю на среду',
    #                 'купаю на среду',
    #                 'куплю на четверг',
    #                 'купаю на четверг',
    #                 'куплю на пятницу',
    #                 'купаю на пятницу',
    #                 'куплю на субботу',
    #                 'купаю на субботу',
    #                 'куплю на воскресенье',
    #                 'купаю на воскресенье',
    #                 'куплю понедельник',
    #                 'купаю понедельник',
    #                 'куплю вторник',
    #                 'купаю вторник',
    #                 'куплю среду',
    #                 'купаю среду',
    #                 'куплю четверг',
    #                 'купаю четверг',
    #                 'куплю пятницу',
    #                 'купаю пятницу',
    #                 'куплю субботу',
    #                 'купаю субботу',
    #                 'куплю воскресенье',
    #                 'купаю воскресенье',
    #                 'закупаю',
    #                 'покажите',
    #                 'предложите',
    #                 'куплю жца',
    #                 'купаю жца',
    #                 'куплю мца',
    #                 'купаю мца',
    #                 'куплю сца',
    #                 'купаю сца',
    #                 # 'горит место',  # доразвить  -- и это продажа
    #                 # 'бронируйте рекламу'  # доразвить -- это продажа наверн
    #                 ]
    f_type = 'buy'
    keyword_list = ['куплю',
                    'купаем',
                    'купаю',
                    'рассмотрю',
                    'предложите',
                    'покажите',
                    'предлагайте',
                    'дайте',  # Ловит ожидайте :с
                    'покупка',
                    'ищу мест',
                    'ищу строк',
                    'ищу много',
                    'ищу реклам',
                    ]
    exclude_keywords = ['куплю канал',
                        'куплю к@',
                        'канал куплю',
                        'куплю чат',
                        'куплю акк',
                        'куплю вам',
                        'куплю нагон',
                        'куплю вериф',
                        'куплю подтверждение',
                        'куплю новостник',
                        'куплю крипт',
                        'куплю btc',
                        'куплю инвайт',
                        'куплю в бота',
                        'куплю сигнал',
                        'услуги',
                        'рассмотрю канал',
                        'продам',
                        'продаешь',
                        'продаёшь',
                        'продаю',
                        'продает',
                        'продаж',
                        'продаёт',
                        'набор на',
                        'продают',
                        'накрутка',
                        'пушкинская',  # карту
                        'пушкинскую',
                        'пушкинские',
                        'подписчика',
                        'накручиваем',
                        'купаю под бота',
                        'купаю подписчик',
                        'куплю телеграм',
                        'куплю пасп',
                        'куплю лиды',
                        'пойду',
                        'акция',
                        'nребуется таргетол',
                        'научу',
                        'возьму на регистрацию',
                        'куплю аккаунты',
                        'куплю готовые',
                        'куплю накрут',
                        'куплю бинанс',
                        'дайте актив',
                        'залив',
                        'пойду менеджер',
                        'пойду закупщик',
                        'стану менеджер',
                        'стану закупщик',
                        'менеджером',
                        'закупщиком',
                        'окупит',
                        'биржа чат',
                        'наши чат',
                        'наших чат',
                        'чаты по',
                        'это сеть чат',
                        'отдам',
                        # 'сеть чат',  # опасно
                        'лесенку',
                        'админских чат',
                        'окупаемост',
                        'кидайте в бан',
                        'бан кидайте',
                        'разбираем',
                        'elfsale',  # имя чата
                        'воронка продаж',
                        'binance',
                        'регистрация',
                        'юзер',
                        'куплю привод',
                        'куплю приход',
                        'способ заработка',
                        'набрать людей',
                        'есть мест',
                        'горит мест',
                        'горят мест',
                        'горит на сегодня',
                        'горит на завтра',
                        'адхот',  # реклама назойливая
                        'aдхот',  # реклама назойливая a lation
                        'адxот',  # реклама назойливая x latin
                        'адхoт',  # реклама назойливая o latin
                        'aдxот',  # реклама назойливая ax latin
                        'aдхoт',  # реклама назойливая ao latin
                        'адxoт',  # реклама назойливая xo latin
                        'aдxoт',  # реклама назойливая axo latin
                        ]

    @classmethod
    def apply(cls, text):
        if text:
            keywords, exc_keywords = super().apply(text)
            if keywords:
                if exc_keywords:
                    # print("Found message:\r\n" + text
                    #       + "\r\n\tWith keywords : " + str(keywords)
                    #       + "\r\n\tMessage excluded because of keywords: " + str(exc_keywords))
                    return keywords, exc_keywords
                elif c := BuyChannel.apply(text):
                    # print("Found message:\r\n" + text
                    #       + "\r\n\tWith keywords : " + str(keywords)
                    #       + "\r\n\tMessage excluded because of channels filter: " + str(c))
                    return keywords, [c]
                else:
                    return keywords, []
        return [], []


class Audience(KeywordFilter):
    f_type = 'аудитории'
    keyword_list = ['мца', 'жца', 'сца', 'женская ца', 'мужская ца', 'средняя ца']

    @classmethod
    def get_text_repr(cls, params: dict):
        audiences = params.get('audience', '-')
        if audiences:
            text = ', '.join(audiences)
        else:
            text = '-'
        return f'{cls.f_type} : {text}\r\n'

    @classmethod
    def get_db_repr_from_text(cls, text: str):
        _type, val = text.split(' : ')
        if '-' not in val:
            val = val.replace(' ', '')
            audiences = val.split(',')
            if '' in audiences:
                audiences.remove('')
            if audiences:
                return cls.get_db_repr(audiences)
        return cls.get_db_repr([])

    @classmethod
    def get_db_repr(cls, audiences):
        return {'audience': audiences}

    @classmethod
    def apply(cls, text):
        if text:
            keywords, _ = super().apply(text)
            res = [*set(keywords)]
            return {'audience': res}
        return {}


class Category(KeywordFilter):
    f_type = 'категории'
    keyword_dict = {'эротика': ['18+', 'эро', 'порн', 'для взрослых', 'хент', 'прон',
                                ' э ', ' э,', ' э.', ' э!', '/э/', '/э ', ' э/'],
                    # 'эротический', 'хентай', 'хентаю', 'эротика',
                    # 'автомобили': ['машин', 'тачки', 'автомобил'], #, 'автомобили'
                    'кулинария': ['кулинар', 'готовка', 'рецепты'],  # 'кулинарная', 'кулинария'
                    'финансы': ['экономик', 'финанc'],
                    'бизнес': ['трейдинг', 'бизнес'],
                    'крипта': ['крипт', 'crypt'],
                    'психология': ['саморазвит', 'психолог', 'мотивац'],
                    'новости': ['новост', 'политик', 'информац'],
                    'философия': ['философ'],
                    'астрология': ['астролог', 'гороскоп'],
                    'образование': ['образов'],
                    'наука': ['наук', 'познавал', 'познавател'],
                    'кино': ['кино', 'фильм']
                    }

    @classmethod
    def get_text_repr(cls, params: dict):
        cats = params.get('categories', '-')
        if cats != '-':
            text = ', '.join(cats)
        else:
            text = '-'
        return f'{cls.f_type} : {text}\r\n'

    @classmethod
    def get_db_repr_from_text(cls, text: str):
        _type, val = text.split(' : ')
        if '-' not in val:
            val = val.replace(' ', '')
            cats = val.split(',')
            if '' in cats:
                cats.remove('')
            if cats:
                return cls.get_db_repr(cats)
        return cls.get_db_repr([])

    @classmethod
    def get_db_repr(cls, cats):
        return {'categories': cats}

    @classmethod
    def apply(cls, text):
        if text:
            # set is needed to remove duplicates
            keywords, _ = super().apply(text)
            res = [*set(keywords)]
            return cls.get_db_repr(res)
        return {}


class Reach(RegexFilter):
    f_type = 'охват'
    regex_list = [r'((от|до)\s?)?(\d+|\d+\s?-\s?\d+){1}[+]?[+]? (- )?охв(ат|ата|атом)?( пост(а|ов))?',
                  r'охв(ат|ата|атом)?( пост(а|ов))? (- )?((от|до)\s?)?(\d+|\d+\s?-\s?\d+){1}[+]?[+]?',
                  r'аудитори(я|ей)\s?((от|до)\s?)?[:]?\s?(\d+|\d+\s?-\s?\d+){1}[+]?']

    # regex_list = [r'((от|до)\s?)?\d+[+]?[кkмm]?[+]? охват']

    # TODO why is there a space in the end
    @classmethod
    def get_text_repr(cls, params: dict):
        reach_min = params.get('reach_min', 0)
        reach_max = params.get('reach_max', 0)
        if reach_min == 0 and reach_max == 0:
            reach = '-'
        elif reach_min == reach_max:
            reach = str(reach_min)
        else:
            reach = f'{reach_min}-{reach_max}'
        return f'{cls.f_type} : {reach}\r\n'

    @classmethod
    def get_db_repr_from_text(cls, text: str):
        _type, val = text.split(' : ')
        if '-' not in val:
            val_min, *val_max = val.split('-')
            if val_max:
                return cls.get_db_repr(int(val_min), int(val_max[0]))
            else:
                return cls.get_db_repr(int(val_min), int(val_min))
        return cls.get_db_repr(None, None)

    @classmethod
    def get_db_repr(cls, _min, _max):
        return {'reach_min': _min, 'reach_max': _max}

    @classmethod
    def apply(cls, text):
        if text:
            reach_full = super().apply(text)
            if reach_full:
                res = re.search(r"\d+-\d+", reach_full)
                if res:
                    reach_range = res.group(0).split('-')
                    return cls.get_db_repr(int(reach_range[0]), int(reach_range[1]))
                else:
                    res = re.search(r"\d+", reach_full).group(0)
                    return cls.get_db_repr(int(res), int(res))
            return {}
        return {}


class Stat(KeywordFilter):
    f_type = 'стата'
    keyword_dict = {'стата++': ['+стата', '+ стата', '+стат', 'стата +', 'стата+', 'стат+', 'на +']}

    @classmethod
    def get_text_repr(cls, params: dict):
        stat = params.get('stat', '-')
        if not stat:
            stat = '-'
        else:
            stat = stat[0]
        return f'{cls.f_type} : {str(stat)}\r\n'

    @classmethod
    def get_db_repr_from_text(cls, text: str):
        _type, val = text.split(' : ')
        if '-' not in val:
            return cls.get_db_repr(['стата++'])
        else:
            return cls.get_db_repr([])

    @classmethod
    def get_db_repr(cls, stat):
        return {'stat': stat}

    @classmethod
    def apply(cls, text):
        if text:
            res, _ = super().apply(text)
            return cls.get_db_repr(res)
        return {}


class Price(RegexFilter):
    regex_list = [r'\d+', r'\d+-\d+']


active_filters = [
    Reach,
    Audience,
    Category,
    Stat,
]
