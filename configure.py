import getpass
import sys
import textwrap
from collections import OrderedDict
from datetime import datetime, timedelta
from typing import Any, NoReturn

import bcrypt
from pymongo import MongoClient
from tornado.options import options as opts

from selene import options, version

WELCOME_MESSAGE = f"""Welcome to the Selene {version} configuration utility.

Please enter values for the following options (just press Enter to
accept a default value, if one is given in brackets).

Consider that this utility generates a sample configuration file named
"selene_sample.conf", you should rename it to "selene.conf".

"""

SCRIPT_HEADER = """# Selene configuration file, created by configure.py script on
# %a %b %d %H:%M:%S %Y.
"""

OPTIONS_TO_EXCLUDE = (
    'help',
    'logging',
    'log_to_stderr',
    'log_file_prefix',
    'log_file_max_size',
    'log_file_num_backups',
)


def exit() -> NoReturn:
    print('Exiting...')
    sys.exit(1)


def _get_option(label: str, option: Any) -> Any:
    pass_ = False
    while not pass_:
        try:
            input_value = input(label)
            if option.default and input_value.strip():
                option._parse(input_value)
                option.set(option._value)
            elif option.default and not input_value.strip():
                option.set(option.default)
            else:
                option.parse(input_value)
                option.set(option._value)
        except KeyboardInterrupt:
            exit()
        except Exception:
            print('* Please enter some text.')
        else:
            pass_ = True
    return option


def _format_value(option: Any) -> str:
    if option.multiple:
        return f'{option.value()}'
    if option.type in (datetime, timedelta):
        return ''
    if option.type is str:
        return f"'{option.value()}'"
    else:
        return f'{option.value()}'


def get_dict_options() -> OrderedDict[str, str]:
    by_group = {}
    for option in opts.values():
        if option.name not in OPTIONS_TO_EXCLUDE:
            by_group.setdefault(option.group_name, []).append(option)
    dict_options = OrderedDict()
    for filename, o in sorted(by_group.items()):
        if filename:
            dict_options[f'#{filename}'] = ''
            print(f'\n\n{filename} options:\n')
        o.sort(key=lambda option: option.name)
        for option in o:
            description = option.help or ''
            lines = textwrap.wrap(description, 79)
            lines.insert(0, '')
            if len(lines) == 0:
                lines.insert(0, '')
            for line in lines:
                print(line)
            metavar, default = '', ''
            if option.metavar:
                metavar = f' ({option.metavar})'
            if option.default is not None and option.default != '':
                default = f' [{option.default}]'
            label = f'> {option.name}{metavar}{default}: '
            dict_options[option.name] = _format_value(_get_option(label, option))
    return dict_options


def generate_configuration_file() -> None:
    dict_options = get_dict_options()
    lines = []
    for name, value in list(dict_options.items()):
        if name.startswith('#'):
            lines.append(f'\n{name} options')
        else:
            lines.append(f'{name} = {value}')
    header = [datetime.strftime(datetime.now(), SCRIPT_HEADER)]
    with open('selene_sample.conf', 'w') as f:
        f.write('\n'.join(header + lines))


def _prompt_yes_no(prompt: str, default: bool = True) -> bool:
    suffix = '[Y/n]' if default else '[y/N]'
    value = input(f'{prompt} {suffix} ').strip().lower()
    if not value:
        return default
    return value in ('y', 'yes')


def _prompt_non_empty(prompt: str) -> str:
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print('* Please enter some text.')


def _prompt_password() -> str:
    while True:
        password = getpass.getpass('> admin password: ')
        confirm = getpass.getpass('> confirm password: ')
        if password and password == confirm:
            return password
        print('* Passwords do not match.')


def bootstrap_database() -> None:
    if not _prompt_yes_no('Create the initial admin user and site settings now?', default=True):
        return
    client = MongoClient(opts.db_uri)
    db = client[opts.db_name]
    site_settings = {'_id': 'site', 'title': opts.title, 'slogan': opts.slogan}
    existing_settings = db.settings.find_one({'_id': 'site'})
    if existing_settings:
        db.settings.update_one({'_id': 'site'}, {'$set': {'title': opts.title, 'slogan': opts.slogan}})
    else:
        db.settings.insert_one(site_settings)
    full_name = _prompt_non_empty('> admin full name: ')
    email = _prompt_non_empty('> admin email: ')
    password = _prompt_password()
    user = {
        'full_name': full_name,
        'email': email,
        'password': bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
        'enabled': True,
        'is_admin': True,
        'join': datetime.now(),
        'locale': opts.default_language,
    }
    existing_user = db.users.find_one({'email': email})
    if existing_user:
        db.users.update_one({'email': email}, {'$set': user})
    else:
        db.users.insert_one(user)
    print('Initial admin user created.')


if __name__ == '__main__':
    try:
        print(WELCOME_MESSAGE)
        options.define_options()
        generate_configuration_file()
        bootstrap_database()
    except KeyboardInterrupt:
        exit()
