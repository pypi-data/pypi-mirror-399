# HubView — Scripting file viewer

A clean, fast, local file viewer with a GitHub‑style UI. Browse folders, preview code with syntax highlighting, render Markdown (tables, task lists, admonitions), show images/video/audio/PDF, and even draw Mermaid diagrams via fenced blocks.

## Example Run Code

1. Create python Script to run hubview

```python

# Example Hubview Run

from hubview import app


scripts = {
    "Python": {
        "python": ".venv/bin/python3",
        "path": "library/pylibs/hubview/example_script.py",
        "args": ["--foo", "bar"],
        "log": "hubview_demo.log",
    },
    "Shell": {

    }
    "Streamlit": {
        "cmd": ["bash", "run_gpc.sh", "--dry-run"],
        "path": "run_gpc.sh",
        "log": "cleanup.log",
    },
}

app.create_hub(root="./", host="0.0.0.0", port=3000, scripts=scripts)

```


2. Create shell script to run python

```shell

# navigate to control directory
cd '/home/pi/Desktop/Code'
py_exec="venv/bin/python3"
py_script="can_hub.py"
echo "============= RUNNING CAN Hub =================="
$py_exec $py_script
/bin/bash
$SHELL

```

Or

1. Run hubview from shell script

```shell

#!/bin/sh
# ------------------------------------
cd '/home/pi/Desktop/Code'
py_exec=".venv/bin/activate"
. $py_exec
echo "============= RUNNING Hubview =================="
hubview --host=0.0.0.0
/bin/bash
$SHELL

```

## Quick start

1. pip install hubview
2. hubview --root 'your directory'
3. open **http://127.0.0.1:5000** in your browser.
