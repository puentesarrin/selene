# -*- coding: utf-8 *-*
import sys
import textwrap

from collections import OrderedDict
from datetime import datetime, timedelta
from tornado.options import options as opts
from selene import options, version

wellcome_message = """Welcome to the Selene %s configuration utility.

Please enter values for the following options (just press Enter to
accept a default value, if one is given in brackets).

Consider that this utility generates a sample configuration file named
"selene_sample.conf", you should rename it to "selene.conf".

"""

header_script = """# -*- coding: utf-8 *-*
# Selene configuration file, created by configure.py script on
# %a %b %d %H:%M:%S %Y.
"""

options_to_exclude = ['help', 'logging', 'log_to_stderr', 'log_file_prefix',
                      'log_file_max_size', 'log_file_num_backups']


def exit():
    print 'Exiting...'
    sys.exit(1)


def _get_option(label, option):
    pass_ = False
    while not pass_:
        try:
            input_value = raw_input(label)
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
        except:
            print '* Please enter some text.'
        else:
            pass_ = True
    return option


def _format_value(option):
    if option.multiple:
        return '%s' % option.value()
    _format_string = {
#        TODO: Improves to format type
        datetime: '',
        timedelta: '',
        str: "'%s'",
    }.get(option.type, '%s')
    return _format_string % option.value()


def get_dict_options():
    by_group = {}
    for option in opts.values():
        if option.name not in options_to_exclude:
            by_group.setdefault(option.group_name, []).append(option)
    dict_options = OrderedDict()
    for filename, o in sorted(by_group.items()):
        if filename:
            dict_options['#%s' % filename] = ''
            print("\n\n%s options:\n" % filename)
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
                metavar = ' (%s)' % option.metavar
            if option.default is not None and option.default != '':
                default = ' [%s]' % option.default
            label = '> %s%s%s: ' % (option.name, metavar, default)
            dict_options[option.name] = _format_value(_get_option(label,
                                                                  option))
    return dict_options


def generate_configuration_file():
    dict_options = get_dict_options()
    lines = []
    for name, value in dict_options.iteritems():
        if name.startswith('#'):
            lines.append('\n%s options' % name)
        else:
            lines.append('%s = %s' % (name, value))
    header = [datetime.strftime(datetime.now(), header_script)]
    with open('selene_sample.conf', 'w') as f:
        f.write('\n'. join(header + lines))

if __name__ == '__main__':
    try:
        print wellcome_message % version
        options.define_options()
        generate_configuration_file()
    except KeyboardInterrupt:
        exit()
