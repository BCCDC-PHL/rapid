#!/usr/bin/env python3

import argparse
import datetime
import glob
import json
import os
import shutil
import sys
import subprocess
import uuid

def run_command(message):
    """
    Initiate pipeline run
    input: 
      message: {"base_command": "nextflow", "subcommand": "run", "command_invocation_directory": "/home/user/analysis", ...}
    output: {message}
    """
    now = datetime.datetime.now()
    today_iso8601_str = now.strftime('%Y-%m-%d') 
    message['command_invocation_id'] = str(uuid.uuid4())

    command = [
        message['base_command']
    ]

    if 'subcommand' in message:
        command.append(message['subcommand'])

    if 'positional_arguments_before_flagged_arguments' in message:
        for argument in message['positional_arguments_before_flagged_arguments']:
            command.append(argument)

    if 'flags' in message:
        for flag in message['flags']:
            command.append(flag)

    if 'flagged_arguments' in message:
        for flag, value in message['flagged_arguments'].items():
            if '$' in value:
                value = os.path.expandvars(value)
                message['flagged_arguments'][flag] = value
            if value is not None:
                command.append(flag)
                command.append(value)

    if 'positional_arguments_after_flagged_arguments' in message:
        for argument in message['positional_arguments_before_flagged_arguments']:
            command.append(argument)

    if 'positional_arguments' in message:
        for argument in message['positional_arguments']:
            command.append(argument)

    exit_code = None
    try:
        message['timestamp_command_invoked'] = datetime.datetime.now().isoformat()
        exit_code = subprocess.check_call(command, cwd=message['command_invocation_directory'])
    except subprocess.CalledProcessError as e:
        sys.stderr.write("Error running command: " + " ".join(command))

    message['timestamp_command_invocation_completed'] = datetime.datetime.now().isoformat()
    message['command_exit_code'] = exit_code

    return message


def remove_nextflow_work_dir(message):
    if '-work-dir' in message['flagged_arguments']:
        work_dir_path = message['flagged_arguments']['-work-dir']
    else:
        work_dir_path = os.path.join(message['command_invocation_directory'], 'work')
    try:
        shutil.rmtree(work_dir_path)
    except Exception as e:
        pass


def remove_nextflow_logs(message):
    nextflow_logs = glob.glob(os.path.join(message['command_invocation_directory'], ".nextflow*"))
    for log in nextflow_logs:
        try:
            if os.path.isdir(log):
                shutil.rmtree(log)
            elif os.path.isfile(log):
                os.remove(log)
            else:
                pass
        except Exception as e:
            pass


def nextflow_cleanup(message):
    if 'remove_pipeline_work_dir' in message and message['remove_pipeline_work_dir']:
        remove_pipeline_work_dir(message)

    if 'remove_nextflow_logs' in message and message['remove_nextflow_logs']:
        remove_nextflow_logs(message)


def cleanup(message):
    if 'base_command' in message and message['base_command'] == 'nextflow':
        nextflow_cleanup(message)


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    args = parser.parse_args()

    for line in sys.stdin:
        try:
            message = json.loads(line.rstrip())
            if message['message_type'] == 'command':
                message = run_command(message)
                cleanup(message)
            elif message['message_type'] == 'sentinel':
                pass
            print(json.dumps(message))
        except Exception as e:
            cleanup(message)


if __name__ == '__main__':        
    main()
