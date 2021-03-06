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

def run_pipeline(config):
    """
    Initiate pipeline run
    input: {"name": "pipeline-name", "revision": "v0.1.0", "pipeline_launch_dir": "/home/user/analysis", "pipeline_params": {"input": "input_data", "output": "output_data"}}
    output: None
    """
    for flag, value in config['pipeline_params'].items():
        assert value

    now = datetime.datetime.now()
    today_iso8601_str = now.strftime('%Y-%m-%d') 
    pipeline_run_id = str(uuid.uuid4())
    pipeline_run_name = config['name'].replace('/', '_') + "--" + pipeline_run_id

    config['work_dir_basename'] = "work." + pipeline_run_name
    
    command = [
        "nextflow",
        "run",
        config['name'],
        "-revision", config['revision'],
        "-profile", "conda",
        "--cache", os.path.expandvars("${HOME}/.conda/envs"),
        "-work-dir", config['work_dir_basename'],
    ]
    
    if 'create_trace' in config and config['create_trace']:
        trace_dir = os.path.join("rapid_analysis_logs", "nextflow_traces")
        trace_filename = today_iso8601_str + "_" + pipeline_run_name + "--trace.txt"
        command.extend([
            "-with-trace", os.path.join(trace_dir, trace_filename)
        ])

    if 'create_report' in config and config['create_report']:
        report_dir = os.path.join("rapid_analysis_logs", "nextflow_reports")
        report_filename = today_iso8601_str + "_" + pipeline_run_name + "--report.html"
        command.extend([
            "-with-report", os.path.join(report_dir, report_filename)
        ])
        
    for flag, value in config['pipeline_params'].items():
        command.append("--" + flag)
        command.append(value)

    pipeline_exit_code = None
    try:
        pipeline_exit_code = subprocess.check_call(command, cwd=config['pipeline_launch_dir'])
    except subprocess.CalledProcessError as e:
        sys.stderr.write("Error running command: " + " ".join(command))

    return (config, pipeline_exit_code)


def remove_pipeline_work_dir(config):
    work_dir_path = os.path.join(config['pipeline_launch_dir'], config['work_dir_basename'])
    print("removing pipeline work dir")
    try:
        shutil.rmtree(work_dir_path)
    except Exception as e:
        print(e)


def remove_nextflow_logs(config):
    nextflow_logs = glob.glob(os.path.join(config['pipeline_launch_dir'], ".nextflow*"))
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


def cleanup(config):
    if 'remove_pipeline_work_dir' in config and config['remove_pipeline_work_dir']:
        remove_pipeline_work_dir(config)

    if 'remove_nextflow_logs' in config and config['remove_nextflow_logs']:
        remove_nextflow_logs(config)


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    args = parser.parse_args()

    for line in sys.stdin:
        try:
            pipeline_config = json.loads(line.rstrip())
            (pipeline_config, exit_code) = run_pipeline(pipeline_config)
            cleanup(pipeline_config)
        except Exception as e:
            cleanup(pipeline_config)
            print(e)
        


if __name__ == '__main__':        
    main()
