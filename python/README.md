# Python for DevOps / SRE — Engineering Review Guide

This folder is a practical Python engineering review and automation guide for DevOps/SRE work and day-to-day automation.

The goal is **not** to learn every advanced Python feature. The goal is to become comfortable reading and writing automation scripts for AWS, Kubernetes, Linux, APIs, files, JSON/CSV, CI/CD, and operational tooling.

---

## 1. What a DevOps Engineer Should Know

Core topics:

1. Variables and data types
2. Strings
3. Lists
4. Indexing and slicing
5. Tuples
6. Dictionaries
7. Sets
8. Operators and conditions
9. `if / elif / else`
10. `for` loops
11. `while` loops
12. `range()`
13. `enumerate()`
14. `break`
15. `continue`
16. Nested loops
17. List comprehensions
18. Functions
19. Main function pattern
20. Modules
21. Packages
22. Libraries
23. Standard library vs third-party libraries
24. `requirements.txt`
25. Exception handling
26. File handling
27. JSON
28. CSV
29. Environment variables
30. `os`
31. `sys`
32. `subprocess`
33. `re` / regex
34. `datetime`
35. `requests`
36. `boto3`
37. Type hints
38. Basic classes
39. Virtual environments
40. `pip`

Advanced topics such as metaclasses, complex OOP, descriptors, deep async programming, and advanced decorators are not priorities for most DevOps/SRE automation roles unless the role specifically requires Python development.

---

# 2. Variables and Basic Data Types

Python does not require an explicit type declaration.

```python
name = "prod-eks"
replicas = 3
cpu = 75.5
healthy = True
nothing = None
```

Common types:

```python
print(type(name))      # str
print(type(replicas))  # int
print(type(cpu))       # float
print(type(healthy))   # bool
```

DevOps example:

```python
cluster = "prod-eks"
desired_nodes = 5
current_nodes = 3

if current_nodes < desired_nodes:
    print("Need to scale cluster")
```

---

# 3. Strings

Strings appear everywhere in automation: cluster names, tags, image names, file paths, API values, environment names, etc.

```python
image = "nginx:1.27"
cluster = "prod-eks"
namespace = "monitoring"
```

Indexing starts at zero:

```python
cluster = "prod-eks"

print(cluster[0])   # p
print(cluster[-1])  # s
```

Useful string methods:

```python
name = "  PROD-EKS  "

print(name.strip())   # PROD-EKS
print(name.lower())   #   prod-eks
print(name.upper())   #   PROD-EKS
```

Very common DevOps pattern:

```python
import os

input_mode = os.getenv("INPUT_MODE", "s3").strip().lower()
```

Meaning:

```text
os.getenv() -> read environment variable
.strip()     -> remove surrounding whitespace
.lower()     -> lowercase the result
```

### f-strings

Use f-strings for readable output:

```python
cluster = "prod"

print(f"Checking cluster {cluster}")
```

---

# 4. Lists

A list stores multiple ordered values.

```python
clusters = ["dev-eks", "stage-eks", "prod-eks"]
```

Access values:

```python
print(clusters[0])   # dev-eks
print(clusters[1])   # stage-eks
print(clusters[-1])  # prod-eks
```

Length:

```python
print(len(clusters))
```

Add/remove:

```python
clusters.append("test-eks")
clusters.remove("test-eks")
```

Membership:

```python
if "prod-eks" in clusters:
    print("Production cluster exists")
```

Loop:

```python
for cluster in clusters:
    print(cluster)
```

---

# 5. Indexing and Slicing

General syntax:

```python
list[start:end:step]
```

Important rule:

> The start index is included. The end index is excluded.

Example:

```python
servers = ["server1", "server2", "server3", "server4", "server5"]

print(servers[1:4])
# ['server2', 'server3', 'server4']
```

Common slices:

```python
servers[:2]     # first two
servers[2:]     # from index 2 onward
servers[:]      # copy/all items
servers[::-1]   # reverse
servers[::2]    # every second item
servers[:-1]    # everything except the last item
```

Example:

```python
parts = ["api", "auth", "master"]
parts = parts[:-1]

print(parts)
# ['api', 'auth']

print("-".join(parts))
# api-auth
```

---

# 6. Tuples

A tuple stores a fixed group of related values.

```python
endpoint = ("10.0.1.25", 8080)

print(endpoint[0])
print(endpoint[1])
```

### Tuple unpacking

```python
def server_info():
    return "prod", "10.0.1.5", 443

env, ip, port = server_info()

print(env)
print(ip)
print(port)
```

This pattern is common when a function returns multiple values.

---

# 7. Dictionaries

A dictionary stores key-value pairs.

```python
server = {
    "name": "web01",
    "ip": "10.0.1.10",
    "status": "running"
}
```

Access:

```python
print(server["name"])
```

Change:

```python
server["status"] = "stopped"
```

Add:

```python
server["region"] = "ap-south-1"
```

### .get()

Very useful for API responses:

```python
instance_id = server.get("instance_id")
```

If the key does not exist, `.get()` returns `None` by default instead of throwing `KeyError`.

```python
instance_id = server.get("instance_id", "unknown")
```

### .items()

```python
for key, value in server.items():
    print(key, value)
```

---

# 8. List of Dictionaries

This is extremely common in AWS/Kubernetes/API responses.

```python
instances = [
    {"id": "i-001", "state": "running"},
    {"id": "i-002", "state": "stopped"}
]

for instance in instances:
    print(instance["id"])
```

Filter running instances:

```python
for instance in instances:
    if instance["state"] == "running":
        print(instance["id"])
```

---

# 9. Sets

A set stores unique values.

```python
clusters = {"prod", "dev", "prod"}

print(clusters)
# {'prod', 'dev'}
```

Useful de-duplication pattern:

```python
seen = set()

for tag in ["api", "web", "api"]:
    if tag not in seen:
        seen.add(tag)
        print(tag)
```

---

# 10. Core Mental Model for Data Structures

```text
Single value
    -> variable

Multiple ordered values
    -> list []

Fixed grouped values
    -> tuple ()

key -> value information
    -> dictionary {}

unique values
    -> set()
```

---

# 11. Operators and Conditions

Comparison operators:

```python
==   # equal
!=   # not equal
>    # greater than
<    # less than
>=   # greater than or equal
<=   # less than or equal
```

Logical operators:

```python
and
or
not
```

Membership:

```python
in
not in
```

Example:

```python
status = "running"
region = "us-east-1"

if status == "running" and region == "us-east-1":
    print("Process instance")
```

---

# 12. if / elif / else

```python
cpu = 85

if cpu > 90:
    print("Critical")
elif cpu > 70:
    print("Warning")
else:
    print("Normal")
```

---

# 13. for Loop

Most common loop in DevOps automation.

```python
servers = ["web1", "web2", "web3"]

for server in servers:
    print(server)
```

Think:

```text
take each item one by one
```

---

# 14. range()

```python
for i in range(5):
    print(i)
```

Output:

```text
0
1
2
3
4
```

Start/end:

```python
for i in range(1, 6):
    print(i)
```

Step:

```python
for i in range(0, 10, 2):
    print(i)
```

---

# 15. enumerate()

Useful when you need index + value.

```python
servers = ["web1", "web2", "web3"]

for index, server in enumerate(servers):
    print(index, server)
```

Start at one:

```python
for index, server in enumerate(servers, start=1):
    print(index, server)
```

---

# 16. while Loop

Runs while a condition is true.

```python
count = 1

while count <= 5:
    print(count)
    count += 1
```

DevOps use cases:

- retry API calls
- wait for service readiness
- poll deployment status
- wait for pod state
- wait for instance state

Example:

```python
attempt = 1

while attempt <= 3:
    print(f"Attempt {attempt}")
    attempt += 1
```

---

# 17. break

Stops the loop completely.

```python
servers = ["dev", "stage", "prod", "test"]

for server in servers:
    if server == "prod":
        break

    print(server)
```

Output:

```text
dev
stage
```

---

# 18. continue

Skips the current iteration and goes to the next item.

```python
servers = ["dev", "stage", "prod"]

for server in servers:
    if server == "stage":
        continue

    print(server)
```

Useful example:

```python
for instance in instances:
    if instance["state"] == "terminated":
        continue

    print(instance["id"])
```

---

# 19. Nested Loops

```python
clusters = [
    ["pod1", "pod2"],
    ["pod3", "pod4"]
]

for cluster in clusters:
    for pod in cluster:
        print(pod)
```

AWS style example:

```python
for reservation in response["Reservations"]:
    for instance in reservation["Instances"]:
        print(instance["InstanceId"])
```

---

# 20. List Comprehensions

Normal approach:

```python
numbers = []

for i in range(5):
    numbers.append(i)
```

Comprehension:

```python
numbers = [i for i in range(5)]
```

Filtering:

```python
running = [
    instance
    for instance in instances
    if instance["state"] == "running"
]
```

Understand normal loops first; comprehensions are just a shorter expression.

---

# 21. Functions

A function is a reusable block of code.

```python
def greet():
    print("Hello")
```

Call it:

```python
greet()
```

Parameters:

```python
def greet(name):
    print(f"Hello {name}")

greet("DevOps")
```

Return value:

```python
def add(a, b):
    return a + b

result = add(10, 20)
print(result)
```

DevOps structure:

```python
def get_instances():
    pass

def stop_instances():
    pass

def send_notification():
    pass
```

### Default arguments

```python
def connect(region="us-east-1"):
    print(region)

connect()
connect("ap-south-1")
```

### *args

Accept many positional arguments:

```python
def show_servers(*servers):
    for server in servers:
        print(server)

show_servers("web1", "web2", "web3")
```

### **kwargs

Accept named keyword arguments:

```python
def show_config(**config):
    for key, value in config.items():
        print(key, value)

show_config(region="us-east-1", environment="prod")
```

---

# 22. main() and __name__

Python does not require a `main()` function, but it is a clean standard structure.

```python
def main():
    print("Starting program")


if __name__ == "__main__":
    main()
```

Meaning:

> Run `main()` only when this Python file is executed directly.

If you run:

```bash
python script.py
```

then:

```python
__name__ == "__main__"
```

is true.

If another file imports `script.py`, the main block does not automatically execute.

DevOps example:

```python
import boto3


def get_running_instances():
    ec2 = boto3.client("ec2")
    return ec2.describe_instances()


def process_instances(response):
    print("Processing instances")


def main():
    response = get_running_instances()
    process_instances(response)


if __name__ == "__main__":
    main()
```

Mental model:

```text
functions
   -> individual jobs

main()
   -> controls overall workflow
```

---

# 23. Module

A Python file is a module.

Example:

```text
aws_utils.py
```

Inside:

```python
def get_instances():
    print("Getting EC2 instances")
```

Use it from another file:

```python
import aws_utils

aws_utils.get_instances()
```

Or:

```python
from aws_utils import get_instances

get_instances()
```

---

# 24. Package

A package is normally a folder containing related Python modules.

Example:

```text
devops_tools/
├── aws.py
├── kubernetes.py
├── linux.py
└── utils.py
```

Import example:

```python
from devops_tools.aws import get_instances
```

---

# 25. Library

A library is reusable functionality, normally made up of one or more modules/packages.

Examples:

- boto3
- requests
- pandas
- kubernetes
- PyYAML

Mental model:

```text
Function
   -> reusable block

Module
   -> one .py file

Package
   -> collection of modules

Library
   -> reusable package/functionality
```

---

# 26. Standard Library vs Third-Party Library

### Standard library

Ships with Python.

Examples:

```python
import os
import sys
import json
import csv
import re
import subprocess
from datetime import datetime
```

Normally no `pip install` is required.

### Third-party library

Installed separately.

Examples:

```text
boto3
requests
pandas
PyYAML
kubernetes
```

Install:

```bash
python -m pip install boto3
```

Use:

```python
import boto3
```

### How to tell the difference

Practical rule:

```text
Ships with Python
-> standard library

Installed through pip / requirements.txt
-> third-party
```

Check installed package:

```bash
python -m pip show boto3
python -m pip list
```

Inspect location:

```python
import boto3

print(boto3.__file__)
```

Third-party packages commonly appear under `site-packages`.

---

# 27. requirements.txt

`requirements.txt` installs external dependencies.

Example:

```text
boto3
requests
PyYAML
kubernetes
```

Install:

```bash
python -m pip install -r requirements.txt
```

Important distinction:

```text
requirements.txt
    -> installs the package

import
    -> loads/uses the package in Python code
```

You still need:

```python
import boto3
import requests
```

even if they were installed through `requirements.txt`.

Do **not** normally add standard library modules such as `os`, `json`, `csv`, `re`, `subprocess`, or `datetime` to `requirements.txt`.

Package name and import name can differ:

```text
requirements.txt:
PyYAML
```

Python:

```python
import yaml
```

Another example:

```text
requirements.txt:
beautifulsoup4
```

Python:

```python
from bs4 import BeautifulSoup
```

---

# 28. Virtual Environments

Create:

```bash
python3 -m venv venv
```

Activate macOS/Linux:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Deactivate:

```bash
deactivate
```

Why use a venv?

It isolates dependencies for one project from the global Python installation.

---

# 29. Exception Handling

Basic:

```python
try:
    result = 10 / 0
except Exception as e:
    print(f"Error: {e}")
```

With finally:

```python
try:
    print("Doing work")
except Exception as e:
    print(e)
finally:
    print("Cleanup always runs")
```

A common DevOps pattern:

```python
for item in items:
    try:
        do_something(item)
    except Exception as e:
        print(f"Failed for {item}: {e}")
        continue
```

---

# 30. File Handling

Read complete file:

```python
with open("config.txt", "r", encoding="utf-8") as f:
    content = f.read()

print(content)
```

Read lines:

```python
with open("servers.txt", "r", encoding="utf-8") as f:
    for line in f:
        print(line.strip())
```

Write:

```python
with open("output.txt", "w", encoding="utf-8") as f:
    f.write("Deployment complete\n")
```

`with` automatically closes the file.

---

# 31. JSON

Very important because APIs, AWS and Kubernetes return structured data.

```python
import json

json_string = '{"name": "prod", "replicas": 3}'
data = json.loads(json_string)

print(data["name"])
```

Dictionary -> JSON string:

```python
data = {
    "name": "prod",
    "replicas": 3
}

json_string = json.dumps(data, indent=2)
print(json_string)
```

Read JSON file:

```python
with open("config.json", "r", encoding="utf-8") as f:
    data = json.load(f)
```

---

# 32. CSV

```python
import csv

with open("servers.csv", "r", encoding="utf-8") as f:
    reader = csv.reader(f)

    for row in reader:
        print(row)
```

Using named columns:

```python
import csv

with open("servers.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        print(row["name"], row["ip"])
```

---

# 33. Environment Variables

```python
import os

region = os.getenv("AWS_REGION", "us-east-1")

print(region)
```

Set from shell:

```bash
export AWS_REGION=ap-south-1
python script.py
```

This is preferable to hardcoding secrets/configuration.

---

# 34. os Module

Common uses:

```python
import os

print(os.getcwd())
print(os.getenv("HOME"))

path = os.path.join("/tmp", "report.csv")
print(path)
```

---

# 35. sys Module

Common uses:

```python
import sys

print(sys.version)
print(sys.argv)
```

Command-line argument example:

```bash
python script.py prod
```

```python
import sys

environment = sys.argv[1]
print(environment)
```

For larger CLI tools, prefer `argparse`.

---

# 36. subprocess

Very important in DevOps when interacting with CLI tools.

```python
import subprocess

result = subprocess.run(
    ["kubectl", "get", "pods"],
    capture_output=True,
    text=True
)

print(result.stdout)
print(result.stderr)
print(result.returncode)
```

Check errors automatically:

```python
result = subprocess.run(
    ["kubectl", "get", "pods"],
    text=True,
    capture_output=True,
    check=True
)
```

Prefer argument lists instead of shell strings when possible.

---

# 37. Regex with re

Useful for filenames, logs, tags, build numbers, etc.

```python
import re

match = re.search(r"\d+", "build-123")

if match:
    print(match.group())
```

Output:

```text
123
```

Find all numbers:

```python
numbers = re.findall(r"\d+", "api-12-build-45")
print(numbers)
```

---

# 38. datetime

```python
from datetime import datetime, timedelta

now = datetime.now()

print(now)
print(now.strftime("%Y%m%d"))

yesterday = now - timedelta(days=1)
print(yesterday)
```

Useful for logs, reports, S3 file naming, scan/build tags, retention, and scheduling logic.

---

# 39. None

`None` means no value.

```python
result = None

if result is None:
    print("No result")
```

Prefer:

```python
if result is None:
```

rather than:

```python
if result == None:
```

---

# 40. Boolean Values

```python
healthy = True
maintenance = False

if healthy and not maintenance:
    print("Service available")
```

---

# 41. Useful Built-ins

### len()

```python
instances = ["i-1", "i-2"]
print(len(instances))
```

### sorted()

```python
servers = ["web3", "web1", "web2"]

print(sorted(servers))
```

### min() / max()

```python
cpu = [20, 80, 40]

print(min(cpu))
print(max(cpu))
```

### any()

True if at least one item is truthy.

```python
statuses = [False, False, True]

print(any(statuses))
```

### all()

True only if all items are truthy.

```python
statuses = [True, True, True]

print(all(statuses))
```

---

# 42. Type Conversion

```python
port = int("8080")
cpu = float("72.5")
count = str(10)
enabled = bool(1)
```

---

# 43. Type Hints

Useful for readability and larger automation scripts.

```python
def get_servers(environment: str) -> list[str]:
    return ["web1", "web2"]
```

Another example:

```python
def add(a: int, b: int) -> int:
    return a + b
```

Type hints do not normally enforce types at runtime; they help developers, IDEs, and static analysis tools.

---

# 44. Basic Classes

For DevOps, understand the basics; do not over-focus initially.

```python
class Server:
    def __init__(self, name: str, ip: str):
        self.name = name
        self.ip = ip

    def show(self):
        print(f"{self.name}: {self.ip}")


server = Server("web01", "10.0.1.10")
server.show()
```

Know:

- class
- object
- `__init__`
- `self`
- attributes
- methods

---

# 45. requests

External library for HTTP APIs.

Install:

```bash
python -m pip install requests
```

Example:

```python
import requests

response = requests.get(
    "https://example.com",
    timeout=10
)

print(response.status_code)
print(response.text)
```

JSON API:

```python
data = response.json()
```

Always consider timeout and error handling in real automation.

---

# 46. boto3

AWS SDK for Python.

Install:

```bash
python -m pip install boto3
```

Example:

```python
import boto3

ec2 = boto3.client(
    "ec2",
    region_name="ap-south-1"
)

response = ec2.describe_instances()

for reservation in response["Reservations"]:
    for instance in reservation["Instances"]:
        print(
            instance["InstanceId"],
            instance["State"]["Name"]
        )
```

A safer version:

```python
for reservation in response.get("Reservations", []):
    for instance in reservation.get("Instances", []):
        print(
            instance.get("InstanceId"),
            instance.get("State", {}).get("Name")
        )
```

---

# 47. Kubernetes Python Client

Install:

```bash
python -m pip install kubernetes
```

Example:

```python
from kubernetes import client, config

config.load_kube_config()

v1 = client.CoreV1Api()

pods = v1.list_pod_for_all_namespaces()

for pod in pods.items:
    print(pod.metadata.namespace, pod.metadata.name)
```

---

# 48. Practical DevOps Python Pattern

A large amount of automation looks like this:

```python
for item in items:
    if should_skip(item):
        continue

    try:
        result = process(item)

        if result:
            print(f"Success: {item}")

    except Exception as e:
        print(f"Failed: {item}: {e}")
```

The core flow:

```text
input
  ↓
list/dict
  ↓
loop
  ↓
condition
  ↓
function/API call
  ↓
exception handling
  ↓
output
```

---

# 49. Clean DevOps Project Structure

```text
automation/
├── main.py
├── aws_utils.py
├── k8s_utils.py
├── config.py
└── requirements.txt
```

Example `aws_utils.py`:

```python
import boto3


def get_instances():
    ec2 = boto3.client("ec2")
    return ec2.describe_instances()
```

Example `main.py`:

```python
from aws_utils import get_instances


def main():
    response = get_instances()
    print(response)


if __name__ == "__main__":
    main()
```

---

# 50. Standard Dependency Flow

```text
requirements.txt
      ↓
python -m pip install -r requirements.txt
      ↓
package installed into environment
      ↓
import package
      ↓
use its functions/classes
```

Example:

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
python devops_examples.py
```

---

# 51. What to Master vs What to Know

## Master well

- variables
- strings
- lists
- slicing
- dictionaries
- sets
- conditions
- loops
- functions
- exceptions
- JSON
- files
- environment variables
- subprocess
- boto3

## Comfortable understanding

- tuples
- CSV
- regex
- datetime
- list comprehensions
- type hints
- requests
- Kubernetes Python client

## Basic understanding initially

- classes
- `*args`
- `**kwargs`
- lambda
- map/filter
- decorators
- generators
- async

---

# 52. Quick Engineering Review

### What is a list?

An ordered, mutable collection that can contain multiple values.

### What is a tuple?

An ordered collection normally used for fixed grouped values. Tuples are immutable.

### Difference between list and tuple?

A list is mutable; a tuple is immutable.

### What is a dictionary?

A key-value data structure.

### What is a set?

An unordered collection of unique values.

### What is slicing?

Selecting part of a sequence using:

```python
sequence[start:end:step]
```

### What does `servers[:-1]` mean?

Everything from the beginning up to, but excluding, the final element.

### Difference between break and continue?

- `break` exits the whole loop.
- `continue` skips only the current iteration.

### What is enumerate?

It provides an index and value while looping.

### What is a function?

A reusable block of logic defined with `def`.

### What does return do?

Returns a value from a function to the caller.

### What is main()?

A common function used to orchestrate program execution.

### What is `if __name__ == "__main__"`?

It ensures the main execution block runs only when the file is executed directly, not when it is imported.

### What is a module?

A Python `.py` file containing reusable code.

### What is a package?

A collection/folder of Python modules.

### What is a library?

Reusable functionality distributed as one or more modules/packages.

### What is the standard library?

Modules that ship with Python itself, for example `os`, `json`, `csv`, `re`, and `subprocess`.

### What is a third-party library?

A library installed separately, normally through `pip`, for example `boto3` or `requests`.

### What is requirements.txt?

A dependency manifest used by pip to install project dependencies.

### Difference between requirements.txt and import?

`requirements.txt` installs dependencies; `import` loads/uses them inside the Python program.

### What is a virtual environment?

An isolated Python environment used to keep project dependencies separate.

### What is exception handling?

Handling runtime failures with `try`, `except`, and optionally `finally`.

### Why use with open()?

It automatically closes the file after the block completes.

### Why is JSON important in DevOps?

Most REST APIs, cloud SDK responses, and configuration workflows use JSON-like structured data.

### Why use environment variables?

To separate runtime configuration and secrets from source code.

### Why use subprocess?

To execute operating-system commands or CLI tools such as `kubectl`, `terraform`, or `docker`.

### Why use boto3?

It is the AWS SDK for Python and allows programmatic interaction with AWS services.

---

# 53. Final DevOps Python Mental Model

If you can confidently understand code like this, your Python base is strong enough for many DevOps/SRE automation tasks:

```python
import os
import boto3


def get_running_instances(region: str) -> list[str]:
    ec2 = boto3.client("ec2", region_name=region)

    response = ec2.describe_instances()

    running_instances = []

    for reservation in response.get("Reservations", []):
        for instance in reservation.get("Instances", []):
            if instance.get("State", {}).get("Name") == "running":
                running_instances.append(instance.get("InstanceId"))

    return running_instances


def main():
    region = os.getenv("AWS_REGION", "ap-south-1")

    try:
        instances = get_running_instances(region)

        for index, instance_id in enumerate(instances, start=1):
            print(f"{index}. {instance_id}")

    except Exception as exc:
        print(f"Failed to query EC2: {exc}")


if __name__ == "__main__":
    main()
```

That single example combines:

- imports
- standard vs third-party modules
- functions
- parameters
- type hints
- environment variables
- boto3
- dictionaries
- lists
- nested loops
- `.get()`
- conditions
- append
- return
- enumerate
- try/except
- main function

---

## What You Should Be Able to Explain After Completing This Lab

- Core Python data types and when to use lists, tuples, dictionaries, and sets.
- How loops, conditions, functions, exceptions, and modules fit together in automation scripts.
- How to read and write JSON, CSV, files, and environment variables safely.
- When to use `subprocess`, `requests`, `boto3`, and the Kubernetes Python client.
- Why virtual environments and `requirements.txt` matter for reproducible automation.
- How to structure a small DevOps/SRE automation project cleanly.

---

## Files in this folder

- `README.md` — complete engineering review guide
- `basics.py` — variables, strings, lists, tuples, dicts, sets, slicing
- `loops.py` — loops, range, enumerate, break, continue, comprehensions
- `functions_modules.py` — functions, main pattern, modules, imports
- `devops_examples.py` — practical examples
- `knowledge-check.md` — concise knowledge check
- `requirements.txt` — common third-party dependencies

Use these files for hands-on engineering review and practice.
