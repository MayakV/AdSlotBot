from collections import namedtuple

import db

# TODO refactor code duplicaion in modify_filter
# TODO rework operand system into a proper action system
# TODO convert list of filters to sets

HelpParams = namedtuple('HelpParams', ['text', 'number_of_args', 'input_type'])


class UserFilter:
    f_type = ''
    operand_help = {}
    help_text = ''
    input_type = ''

    @classmethod
    def get_string(cls, conn, user_id):
        f_name = cls.f_type.title()
        if _filter := cls.get_user_filter(conn, user_id):
            op = _filter["operand"]
            val = _filter["value"]
            if op == 'in' and isinstance(val, list):
                return f'{f_name}: {",".join(val)}\r\n'
            elif op in ('>', '<'):
                return f'{f_name}: {str(op)} {str(val)}\r\n'  #
            else:
                return f'{f_name}: {str(val)}\r\n'  # str(op) + " " +
        else:
            return f'{f_name}: не выбрано\r\n'

    @classmethod
    def get_user_filter(cls, conn: db.Connection, user_id):
        if old_filters := conn.get_user_filter(user_id, cls.f_type):
            # only one filter can exist in db
            return old_filters[0]
        else:
            # no filter found
            return None

    @classmethod
    def apply(cls, conn: db.Connection, user_id, ads: list):
        return ads

    @classmethod
    def modify_filter(cls, conn: db.Connection, user_id, operand='', value=''):
        pass


class Reach(UserFilter):
    f_type = 'охват'
    operand_help = {'>': HelpParams('Охват ОТ', 1, 'type_in'),
                    #'<': HelpParams('Охват ДО', 1, 'type_in'),
                    '-': HelpParams('Очистить фильтр', 0, None)
                    }
    help_text = 'Фильтр по охвату каналов.\r\n'
    input_type = 'type_in'

    @classmethod
    def check_above_min(cls, ad: dict, value):
        if (_min := ad.get('secondary_filter_params', []).get('reach_min', 0)) >= value:  # or _min == 0:
            return True
        else:
            return False

    @classmethod
    def check_below_max(cls, ad: dict, value):
        if (_max := ad.get('secondary_filter_params', []).get('reach_max', 0)) <= value:  # or _max == 0:
            return True
        else:
            return False

    @classmethod
    def apply(cls, conn: db.Connection, user_id, ads: list):
        _filter = cls.get_user_filter(conn, user_id)
        if _filter:
            if _filter['operand'] == '>':
                return filter(lambda ad: cls.check_above_min(ad, _filter.get('value', 0)), ads)
            elif _filter['operand'] == '<':
                return filter(lambda ad: cls.check_below_max(ad, _filter.get('value', 0)), ads)
            else:
                return ads
        else:
            # no filter found
            return ads

    @classmethod
    def modify_filter(cls, conn: db.Connection, user_id, operand='', value=''):
        # if not operand:
        #     return 'Не указан операнд \r\n' \
        #            'Воспользуйтесь командой /помощь, чтобы увидеть пример команды для изменения фильтра'
        # if not value:
        #     return 'Не указано значение \r\n' \
        #            'Воспользуйтесь командой /помощь, чтобы увидеть пример команды для изменения фильтра'
        if value:
            try:
                value = int(value)
            except ValueError:
                return 'Предоставленное значение должно быть числовым'
        if old_filter := cls.get_user_filter(conn, user_id):
            if operand in ['>', '<']:
                if value != old_filter['value']:
                    conn.save_user_filter(user_id, cls.f_type, operand, value)
                    return 'Фильтр изменен'
                else:
                    return 'Данный фильтр уже добавлен \r\n' \
                           'Воспользуйтесь командой /filters, чтобы увидеть добавленные фильтры'
            elif operand == '-':
                conn.delete_user_filter(user_id, cls.f_type)
                return 'Фильтр удален'
            # else:
            #     return 'Данный операнд не найден \r\n' \
            #            'Воспользуйтесь командой /помощь, чтобы увидеть пример команды для изменения фильтра'
        elif operand in ['>', '<']:
            conn.save_user_filter(user_id, cls.f_type, operand, int(value))
            return 'Новый фильтр добавлен'
        elif operand == '-':
            return 'Данный фильтр не добавлен \r\n' \
                   'Воспользуйтесь командой /filters, чтобы увидеть добавленные фильтры'
        # else:
        #     return 'Данный операнд не найден \r\n' \
        #            'Воспользуйтесь командой /помощь, чтобы увидеть пример команды для изменения фильтра'


class Category(UserFilter):
    f_type = 'категория'
    operand_help = {#'+': HelpParams('Добавить значение', 1, 'type_in'),
                    '-': HelpParams('Очистить фильтр', 0, 'inline')
                    }
    help_text = 'Фильтр по категориям каналов. Показывает заявки, в которых присутствует выбранная категория.\r\n\r\n' \
                'Доступные категории:\r\n' \
                'эротика\r\n' \
                'автомобили\r\n' \
                'кулинария\r\n' \
                'финансы\r\n' \
                'бизнес\r\n' \
                'психология\r\n'  # category list in AdScraper/filters.py in Category class
    valid_values = ['эротика',
                    'автомобили',
                    'кулинария',
                    'финансы',
                    'бизнес',
                    'психология']
    input_type = 'inline'

    @classmethod
    def check_category(cls, ad, value):
        if set(value) & set(ad.get('secondary_filter_params', []).get('categories', [])):  # == []
            return True
        else:
            return False

    @classmethod
    def apply(cls, conn: db.Connection, user_id, ads: list):
        _filter = cls.get_user_filter(conn, user_id)
        if _filter:
            if _filter['operand'] == 'in':
                return list(filter(lambda ad: cls.check_category(ad, _filter.get('value', [])), ads))
            else:
                return ads
        else:
            # no filter found
            return ads

    @classmethod
    def modify_filter(cls, conn: db.Connection, user_id, operand='', value=''):
        # if not operand:
        #     return 'Не указан операнд \r\n' \
        #            'Воспользуйтесь командой /помощь, чтобы увидеть пример команды для изменения фильтра'
        # if not value:
        #     return 'Не указано значение \r\n' \
        #            'Воспользуйтесь командой /помощь, чтобы увидеть пример команды для изменения фильтра'
        if value and value not in cls.valid_values:
            return 'Введена неверная категория'
        if old_filter := cls.get_user_filter(conn, user_id):
            if operand == '+':
                if value not in old_filter['value']:
                    old_filter['value'].append(value)
                    conn.save_user_filter(user_id, cls.f_type, 'in', old_filter['value'])
                    return 'Фильтр изменен'
                else:
                    return 'Данный фильтр уже добавлен \r\n' \
                           'Воспользуйтесь командой /filters, чтобы увидеть добавленные фильтры'
            elif operand == '-':
                if value:
                    if value in old_filter['value']:
                        old_filter['value'].remove(value)
                        if old_filter['value']:
                            conn.save_user_filter(user_id, cls.f_type, 'in', old_filter['value'])
                            return 'Фильтр изменен'
                        else:
                            conn.delete_user_filter(user_id, cls.f_type)
                            return 'Фильтр удален'
                else:
                    conn.delete_user_filter(user_id, cls.f_type)
                    return 'Фильтр удален'
            else:
                return 'Данный операнд не найден \r\n' \
                       'Воспользуйтесь командой /помощь, чтобы увидеть пример команды для изменения фильтра'
        elif operand == '+':
            conn.save_user_filter(user_id, cls.f_type, 'in', [value])
            return 'Новый фильтр добавлен'
        else:
            return 'Данный фильтр не добавлен \r\n' \
                   'Воспользуйтесь командой /filters, чтобы увидеть добавленные фильтры'


class Audience(UserFilter):
    f_type = 'аудитория'
    operand_help = {#'+': HelpParams('Добавить значение', 1, 'inline'),
                    '-': HelpParams('Очистить фильтр', 0, 'inline')
                    }
    help_text = 'Фильтр по целевой аудитории каналов.\r\n' \
                'Доступные целевые аудитории:\r\n' \
                'Мца\r\n' \
                'Жца\r\n' \
                'Сца\r\n'  # category list in AdScraper/filters.py in Audience class
    valid_values = ['жца', 'мца', 'сца']
    input_type = 'inline'

    @classmethod
    def modify_filter(cls, conn: db.Connection, user_id, operand='', value=''):
        # if not operand:
        #     return 'Не указан операнд \r\n' \
        #            'Воспользуйтесь командой /помощь, чтобы увидеть пример команды для изменения фильтра'
        # if not value:
        #     return 'Не указано значение \r\n' \
        #            'Воспользуйтесь командой /помощь, чтобы увидеть пример команды для изменения фильтра'
        # if value not in cls.valid_values:
        #     return 'Введена неверная целевая аудитория'
        if old_filter := cls.get_user_filter(conn, user_id):
            # only one filter can exist in db
            if operand == '+':
                if value not in old_filter['value']:
                    old_filter['value'].append(value)
                    conn.save_user_filter(user_id, cls.f_type, 'in', old_filter['value'])
                    return 'Фильтр изменен'
                else:
                    return 'Данный фильтр уже добавлен \r\n' \
                           'Воспользуйтесь командой /filters, чтобы увидеть добавленные фильтры'
            elif operand == '-':
                if value:
                    if value in old_filter['value']:
                        old_filter['value'].remove(value)
                        if old_filter['value']:
                            conn.save_user_filter(user_id, cls.f_type, 'in', old_filter['value'])
                            return 'Фильтр изменен'
                        else:
                            conn.delete_user_filter(user_id, cls.f_type)
                            return 'Фильтр удален'
                else:
                    conn.delete_user_filter(user_id, cls.f_type)
                    return 'Фильтр удален'
            else:
                return 'Данный операнд не найден \r\n' \
                       'Воспользуйтесь командой /помощь, чтобы увидеть пример команды для изменения фильтра'
        elif operand == '+':
            conn.save_user_filter(user_id, cls.f_type, 'in', [value])
            return 'Новый фильтр добавлен'
        else:
            return 'Данный фильтр не добавлен \r\n' \
                   'Воспользуйтесь командой /filters, чтобы увидеть добавленные фильтры'

    @classmethod
    def check_audience(cls, ad, value):
        if set(value) & set(ad.get('secondary_filter_params', []).get('audience', [])):  # == []
            return True
        else:
            return False

    @classmethod
    def apply(cls, conn: db.Connection, user_id, ads: list):
        _filter = cls.get_user_filter(conn, user_id)
        if _filter:
            if _filter['operand'] == 'in':
                return list(filter(lambda ad: cls.check_audience(ad, _filter.get('value', [])), ads))
            else:
                return ads
        else:
            # no filter found
            return ads


class Stat(UserFilter):
    f_type = 'статистика'
    operand_help = {'+': HelpParams('Добавить фильтр', 0, None),
                    '-': HelpParams('Очистить фильтр', 0, None),
                    }
    help_text = 'Фильтр по статистике каналов.\r\n'
    valid_values = ['стата++']
    input_type = 'type_in'

    @classmethod
    def check_stat(cls, ad: dict, value):
        if {value} & set(ad.get('secondary_filter_params', []).get('stat', [])):  # == []
            return True
        else:
            return False

    @classmethod
    def apply(cls, conn: db.Connection, user_id, ads: list):
        _filter = cls.get_user_filter(conn, user_id)
        if _filter:
            if _filter['operand'] == '+':
                return list(filter(lambda ad: cls.check_stat(ad, _filter.get('value', 0)), ads))
            else:
                return ads
        else:
            # no filter found
            return ads

    @classmethod
    def modify_filter(cls, conn: db.Connection, user_id, operand='', value=''):
        # if not operand:
        #     return 'Не указан операнд \r\n' \
        #            'Воспользуйтесь командой /помощь, чтобы увидеть пример команды для изменения фильтра'
        # if not value:
        #     return 'Не указано значение \r\n' \
        #            'Воспользуйтесь командой /помощь, чтобы увидеть пример команды для изменения фильтра'
        if old_filter := cls.get_user_filter(conn, user_id):
            # only one filter can exist in db
            if operand == '+':
                if value != old_filter['value']:
                    # old_filter['value'] = value
                    conn.save_user_filter(user_id, cls.f_type, '+', 'стата++')  # old_filter['value']
                    return 'Фильтр изменен'
                else:
                    return 'Данный фильтр уже добавлен \r\n' \
                           'Воспользуйтесь командой /filters, чтобы увидеть добавленные фильтры'
            elif operand == '-':
                conn.delete_user_filter(user_id, cls.f_type)
                return 'Фильтр удален'
            else:
                return 'Данный операнд не найден \r\n' \
                       'Воспользуйтесь командой /помощь, чтобы увидеть пример команды для изменения фильтра'
        elif operand == '+':
            conn.save_user_filter(user_id, cls.f_type, '+', 'стата++')
            return 'Новый фильтр добавлен'
        else:
            return 'Данный фильтр не добавлен \r\n' \
                   'Воспользуйтесь командой /filters, чтобы увидеть добавленные фильтры'
