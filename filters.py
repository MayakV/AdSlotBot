from flashtext import KeywordProcessor
import re


def prepare_text(text):
    text = text.replace(r'`', '')
    text = re.sub(r'(\d+) (\d+)', r'\1\2', text)
    # text = re.sub(r'(\d+)([кk]?)\s?-\s?(\d+)([кk]?)', r'\1\2-\3\4', text)
    text = re.sub(r'(\d+)[кk]?\s?-\s?(\d+)[кk]', r'\g<1>000-\g<2>000', text)
    text = re.sub(r'(\d+)[kк]', r'\g<1>000', text)
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


class KeywordFilter:
    keyword_dict = {}
    keyword_list = []

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
        return processor.extract_keywords(text)

    @classmethod
    def get_text_repr(cls, params: dict):
        return "print method is not defined"


class RegexFilter:
    regex_list = []

    param_names = []

    @classmethod
    def apply(cls, text):
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


class BuyOrder(KeywordFilter):
    keyword_list = ['куплю рекламу',
                    '#куплюрекламу',
                    '#покупкарекламы',
                    'куплю на сегодня',
                    'куплю на завтра',
                    'куплю на сейчас',
                    'куплю сегодня',
                    'куплю завтра',
                    # 'за пост', # Иногда подтягивает продажи, хз что делать
                    'куплю/продам рекламу',
                    'куплю в каналах',
                    'куплю в канале',
                    'куплю утро',
                    'куплю день',
                    'куплю вечер',
                    'куплю ночь',
                    'куплю фулл день',
                    'покупка рекламы',  # тоже подтягивает рекламу иногда
                    'куплю места',
                    'куплю на понедельник',
                    'куплю на вторник',
                    'куплю на среду',
                    'куплю на четверг',
                    'куплю на пятницу',
                    'куплю на субботу',
                    'куплю на воскресенье',
                    'куплю понедельник',
                    'куплю вторник',
                    'куплю среду',
                    'куплю четверг',
                    'куплю пятницу',
                    'куплю субботу',
                    'куплю воскресенье',
                    ]


class Audience(KeywordFilter):
    keyword_list = ['мца', 'жца', 'сца']

    @classmethod
    def apply(cls, text):
        if text:
            res = [*set(super().apply(text))]
            return {'audience': res}
        return {}

    @classmethod
    def get_text_repr(cls, params: dict):
        audiences = params.get('audience', '-')
        text = ''
        if audiences:
            for audience in audiences:
                text += audience + ', '
        else:
            text = '-'
        return f'аудитории : {text}\r\n'


class Category(KeywordFilter):
    keyword_dict = {'эротика': ['18+', 'эро', 'порн', 'для взрослых', 'хент', 'прон',
                                ' э ', ' э,', ' э.', ' э!', '/э/', '/э ', ' э/'],  # 'эротический', 'хентай', 'хентаю', 'эротика',
                    'автомобили': ['машин', 'тачки', 'автомобил'], #, 'автомобили'
                    'кулинария': ['кулинар', 'готовка', 'рецепты'], #'кулинарная', 'кулинария'
                    'финансы': ['крипто', 'экономик', 'финанc'],
                    'бизнес': ['трейдинг', 'бизнес'],
                    'психология': ['саморазвит', 'психолог', 'мотивац'],
                    'новости': ['новост', 'политик', 'война'],
                    'философия': ['философ'],
                    'астрология': ['астролог', 'гороскоп'],
                    'образование': ['образование']
                    }

    @classmethod
    def apply(cls, text):
        if text:
            # set is needed to remove duplicates
            res = [*set(super().apply(text))]
            return {'categories': res}
        return {}

    @classmethod
    def get_text_repr(cls, params: dict):
        cats = params.get('categories', '-')
        text = ''
        if cats:
            for cat in cats:
                text += cat + ', '
        else:
            text = '-'
        return f'категории : {text}\r\n'


class Reach(RegexFilter):
    regex_list = [r'((от|до)\s?)?(\d+|\d+\s?-\s?\d+){1}[+]?[+]? (- )?охв(ат|ата|атом)?( пост(а|ов))?',
                  r'охв(ат|ата|атом)?( пост(а|ов))? (- )?((от|до)\s?)?(\d+|\d+\s?-\s?\d+){1}[+]?[+]?',
                  r'аудитори(я|ей)\s?((от|до)\s?)?[:]?\s?(\d+|\d+\s?-\s?\d+){1}[+]?']

    # regex_list = [r'((от|до)\s?)?\d+[+]?[кkмm]?[+]? охват']

    @classmethod
    def apply(cls, text):
        if text:
            reach_full = super().apply(text)
            if reach_full:
                res = re.search(r"\d+-\d+", reach_full)
                if res:
                    reach_range = res.group(0).split('-')
                    return {'reach_min': int(reach_range[0]), 'reach_max': int(reach_range[1])}
                else:
                    res = re.search(r"\d+", reach_full).group(0)
                    return {'reach_min': int(res), 'reach_max': int(res)}
            return {}
        return {}

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
        return f'охват : {reach}\r\n'


class Stat(KeywordFilter):
    keyword_dict = {'стата++': ['+стата', '+ стата', '+стат', 'стата +', 'стата+', 'стат+']}

    @classmethod
    def apply(cls, text):
        if text:
            res = super().apply(text)
            return {'stat': res}
        return {}

    @classmethod
    def get_text_repr(cls, params: dict):
        stat = params.get('stat', '-')
        if not stat:
            stat = '-'
        return f'стата : {str(stat)}\r\n'


class Price(RegexFilter):
    regex_list = ['\d+', '\d+-\d+']

# 'стата++'
