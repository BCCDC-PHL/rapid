#!/usr/bin/env python3

import argparse
import datetime
import glob
import json
import os
import re
import sys
import subprocess
import uuid


def create_completion_message(messages):
    num_commands_invoked_by_base_command = {}
    commands = [message for message in messages if message['message_type'] == 'command_invocation']
    for command in commands:
        if command['base_command'] in num_commands_invoked_by_base_command:
            num_commands_invoked_by_base_command[command['base_command']] += 1
        else:
            num_commands_invoked_by_base_command[command['base_command']] = 1

    commands_by_command_invocation_id = {command['command_invocation_id']: command for command in commands}

    timestamp_completed = datetime.datetime.now().isoformat()
    completion_message = {
        "message_id": str(uuid.uuid4()),
        "timestamp_completed": timestamp_completed,
        "num_commands_invoked": len(commands),
        "num_commands_invoked_by_base_command": num_commands_invoked_by_base_command,
        "commands_by_command_invocation_id": commands_by_command_invocation_id,
    }

    return completion_message


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    args = parser.parse_args()

    messages = []
    for line in sys.stdin:
        try:
            message = json.loads(line.rstrip())
            if message['message_type'] == 'sentinel':
                completion_message = create_completion_message(messages)
                completion_message['correlation_id'] = message['correlation_id']
                with open(message['context']['completion_marker_file'], 'w') as f:
                    json.dump(completion_message, f, indent=4, sort_keys=True)
                messages = []
            else:
                messages.append(message)
        except Exception as e:
            pass


if __name__ == '__main__':
    main()
