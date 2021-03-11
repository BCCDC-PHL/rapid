#!/usr/bin/env python3

import argparse
import json
import operator
import sys

from collections import defaultdict


# https://stackoverflow.com/a/37704379
def nested_set(dic, keys, value):
    for key in keys[:-1]:
        dic = dic.setdefault(key, {})
    dic[keys[-1]] = value


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-c", "--config", required=True, help="JSON-formatted template for configuration")
    args = parser.parse_args()

    with open(args.config, 'r') as f:
        config = json.load(f)

    for line in sys.stdin:
        try:
            message = json.loads(line.rstrip())
            nested_set(message, config['keys'], message[config['value']])
            print(message)
            
        except Exception as e:
            raise(e)


if __name__ == '__main__':
    main()
