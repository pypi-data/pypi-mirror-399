## TestRift Server (`testrift-server`)

Python server for TestRift real-time test runs: live log streaming, result storage, and a web UI for browsing and analysis.

### Install

```bash
pip install testrift-server
```

### Run

```bash
testrift-server
```

Or:

```bash
python -m testrift_server
```

### Configuration

- The server loads configuration from either:
  - `testrift_server.yaml` in the directory you run `testrift-server` from, or
  - `TESTRIFT_SERVER_CONFIG` (a filesystem path to a YAML config file; absolute path recommended).


