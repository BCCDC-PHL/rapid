#!/usr/bin/env python3

import argparse
import json
import os
import re
import sys

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-c", "--config", required=True, help="JSON-formatted template for configuration")
    parser.add_argument("-m", "--message-type", default='command_creation', help="Only act on this message type (overrides config)")
    args = parser.parse_args()

    with open(args.config, 'r') as f:
        config = json.load(f)

    filter_function = eval(config['lambda'])

    for line in sys.stdin:
        try:
            message = json.loads(line.rstrip())
            if args.message_type:
                message_type = args.message_type
            else:
                message_type = config['message_type']
            if message['message_type'] != message_type:
                continue
            if 'filter_context' in message and message['filter_context'] is not None:
                if filter_function(message['filter_context']):
                    print(json.dumps(message))
            else:
                print(json.dumps(message))
        except Exception as e:
            raise(e)


if __name__ == '__main__':
    main()
