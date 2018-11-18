import configparser
import os


def getConfigParser(file):
    config = configparser.SafeConfigParser()
    if os.path.exists(file):
        config.read(file)
        return config


def writeOption(file, parser, _section, key, value):
    if not parser.has_section(_section):
        parser[_section] = {key: value}

    elif not parser.has_option(_section, key):
        section = parser[_section]
        section[key] = value

    else:
        parser.set(_section, key, value)

    with open(file, "w") as f:
        parser.write(f)

    return
