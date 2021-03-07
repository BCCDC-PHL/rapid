<p align="center">
  <img src="docs/images/RAPID_logo.png">
</p>

# RAPID Analysis and Processing of Incoming Data

A system for automatically running arbitrary Nextflow pipelines.

## Usage

The `rapid-run` command takes a [JSON Lines](https://jsonlines.org/)-formatted input from standard input. That file specifies one pipeline run per line, as follows:

```json
{ "name": "BCCDC-PHL/routine-sequence-qc", "revision": "v0.1.2", "working_directory": "/home/user/analyses", pipeline_params: {"input": "/path/to/input1", "output": "/path/to/output1", ...}}
{ "name": "BCCDC-PHL/routine-sequence-qc", "revision": "v0.1.2", "working_directory": "/home/user/analyses", pipeline_params: {"input": "/path/to/input2", "output": "/path/to/output2", ...}}
...
```

Pipe the list of pipeline run instances into the `rapid-run` program.

```
cat pipeline-runs.jsonl | rapid-run
```

Each pipeline run will be invoked when the previous one completes.
