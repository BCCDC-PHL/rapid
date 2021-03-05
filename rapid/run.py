#!/usr/bin/env python3

import argparse
import json
import os
import sys
import subprocess


def run_pipeline(config):
    """
    Initiate pipeline run
    input: {"name": "pipeline-name", "revision": "v0.1.0", "working_directory": "/home/user/analysis", "pipeline_params": {"input": "input_data", "output": "output_data"}}
    output: None
    """
    for flag, value in config['pipeline_params'].items():
        assert value

    command = [
        "nextflow",
        "run",
        config['name'],
        "-revision", config['revision'],
        "-profile", "conda",
        "--cache", os.path.expandvars("${HOME}/.conda/envs"),
    ]
    for flag, value in config['pipeline_params'].items():
        command.append("--" + flag)
        command.append(value)

    try:
        subprocess.call(command, cwd=config['working_directory'])
    except CalledProcessError as e:
        sys.stderr.write("Error running command: " + " ".join(command))

    
def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    args = parser.parse_args()

    for line in sys.stdin:
        pipeline_config = json.loads(line.rstrip())
        run_pipeline(pipeline_config)


if __name__ == '__main__':        
    main()
