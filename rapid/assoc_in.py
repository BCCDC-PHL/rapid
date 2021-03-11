#!/usr/bin/env python3

import argparse
import json
import os
import re
import sys

from collections import defaultdict


# https://stackoverflow.com/a/37704379
def nested_get(dic, keys):    
    for key in keys:
        dic = dic[key]
    return dic

# https://stackoverflow.com/a/37704379
def nested_set(dic, keys, value):
    for key in keys[:-1]:
        dic = dic.setdefault(key, {})
    dic[keys[-1]] = value


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-c", "--config", help="JSON-formatted template for configuration")
    parser.add_argument("-m", "--message-type", default='command_creation', help="Message type to act on (overrides config)")
    parser.add_argument("-k", "--keys", action='append', help="Keys used to navigate into message (overrides config)")
    parser.add_argument("-v", "--value", help="Value to be inserted (overrides config)")
    args = parser.parse_args()

    config = None
    if args.config:
        with open(args.config, 'r') as f:
            config = json.load(f)

    for line in sys.stdin:
        try:
            message = json.loads(line.rstrip())
            if args.message_type:
                message_type = args.message_type
            else:
                message_type = config['message_type']
            if message['message_type'] != message_type:
                continue
            if args.value:
                value_to_assoc = args.value
            else:
                if 'value' in config and config['value'] is not None:
                    value_to_assoc = config['value']
                elif 'message_keys' in config and config['message_keys'] is not None:
                    value_to_assoc = nested_get(message, config['message_keys'])
                    if 'lambda' in config and 'lambda' is not None:
                        transform_function = eval(config['lambda'])
                        value_to_assoc = transform_function(value_to_assoc)

            if args.keys:
                keys_to_nav = args.keys
            else:
                keys_to_nav = config['keys']
                
            nested_set(message, keys_to_nav, value_to_assoc)
            print(json.dumps(message))
            
        except Exception as e:
            raise(e)


if __name__ == '__main__':
    main()
