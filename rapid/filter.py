#!/usr/bin/env python3

import argparse
import json
import sys

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-c", "--config", required=True, help="JSON-formatted template for configuration")
    args = parser.parse_args()

    with open(args.config, 'r') as f:
        config = json.load(f)

    filter_function = eval(config['lambda'])

    for line in sys.stdin:
        try:
            message = json.loads(line.rstrip())
            if 'filter_context' in message and message['filter_context'] is not None:
                if filter_function(message['filter_context']):
                    print(message)
            else:
                print(message)
        except Exception as e:
            raise(e)


if __name__ == '__main__':
    main()
