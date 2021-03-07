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

def run_command(config):
    """
    Initiate pipeline run
    input: 
      config: {"name": "pipeline-name", "revision": "v0.1.0", "pipeline_launch_dir": "/home/user/analysis", "pipeline_params": {"input": "input_data", "output": "output_data"}}
    output: ({config}, 0)
    """
    

    now = datetime.datetime.now()
    today_iso8601_str = now.strftime('%Y-%m-%d') 
    config['command_invocation_id'] = str(uuid.uuid4())

    command = [
        config['base_command']
    ]

    if 'subcommand' in config:
        command.append(config['subcommand'])

    if 'positional_arguments_before_flagged_arguments' in config:
        for argument in config['positional_arguments_before_flagged_arguments']:
            command.append(argument)

    if 'flags' in config:
        for flag in config['flags']:
            command.append(flag)

    if 'flagged_arguments' in config:
        for flag, value in config['flagged_arguments'].items():
            assert value
            command.append(flag)
            command.append(value)

    if 'positional_arguments_after_flagged_arguments' in config:
        for argument in config['positional_arguments_before_flagged_arguments']:
            command.append(argument)

    if 'positional_arguments' in config:
        for argument in config['positional_arguments']:
            command.append(argument)

    exit_code = None
    try:
        config['timestamp_command_invoked'] = datetime.datetime.now().isoformat()
        exit_code = subprocess.check_call(command, cwd=config['command_invocation_directory'])
    except subprocess.CalledProcessError as e:
        sys.stderr.write("Error running command: " + " ".join(command))

    config['timestamp_command_invocation_completed'] = datetime.datetime.now().isoformat()
    config['command_exit_code'] = exit_code

    return config


def remove_nextflow_work_dir(config):
    if '-work-dir' in config['flagged_arguments']:
        work_dir_path = config['flagged_arguments']['-work-dir']
    else:
        work_dir_path = os.path.join(config['command_invocation_directory'], 'work')
    print("removing pipeline work dir")
    try:
        shutil.rmtree(work_dir_path)
    except Exception as e:
        print(e)


def remove_nextflow_logs(config):
    nextflow_logs = glob.glob(os.path.join(config['command_invocation_directory'], ".nextflow*"))
    print("removing nextflow logs")
    for log in nextflow_logs:
        try:
            if os.path.isdir(log):
                shutil.rmtree(log)
            elif os.path.isfile(log):
                os.remove(log)
            else:
                pass
        except Exception as e:
            print(e)


def nextflow_cleanup(config):
    if 'remove_pipeline_work_dir' in config and config['remove_pipeline_work_dir']:
        remove_pipeline_work_dir(config)

    if 'remove_nextflow_logs' in config and config['remove_nextflow_logs']:
        remove_nextflow_logs(config)


def cleanup(config):
    if config['base_command'] == 'nextflow':
        nextflow_cleanup(config)


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    args = parser.parse_args()

    for line in sys.stdin:
        try:
            command_config = json.loads(line.rstrip())
            command_config = run_command(command_config)
            cleanup(command_config)
            print(json.dumps(command_config))
        except Exception as e:
            cleanup(command_config)


if __name__ == '__main__':        
    main()
