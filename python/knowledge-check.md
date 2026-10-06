# Python for DevOps/SRE — Knowledge Check

Use this file to validate your understanding after completing the Python labs.

## Core

### 1. What are common Python data types?

- str
- int
- float
- bool
- None
- list
- tuple
- dict
- set

### 2. List vs tuple?

- List: mutable
- Tuple: immutable

### 3. Dictionary?

Key-value data structure.

```python
server = {
    "name": "web01",
    "status": "running"
}
```

### 4. Set?

Stores unique values.

### 5. What is slicing?

```python
sequence[start:end:step]
```

End is excluded.

```python
servers[:-1]
```

means everything except the last item.

---

## Loops

### 6. for vs while?

`for`: process items in an iterable.

`while`: repeat while a condition remains true.

### 7. break?

Exit the entire loop.

### 8. continue?

Skip current iteration.

### 9. enumerate?

Returns index + value while looping.

```python
for index, server in enumerate(servers, start=1):
    print(index, server)
```

### 10. range?

Generates a sequence of integers.

```python
range(start, stop, step)
```

---

## Functions

### 11. What is a function?

Reusable code defined with `def`.

### 12. What does return do?

Returns a value to the caller.

### 13. What are default arguments?

```python
def connect(region="us-east-1"):
    pass
```

### 14. What are *args and **kwargs?

`*args`: variable number of positional arguments.

`**kwargs`: variable number of keyword arguments.

---

## main

### 15. Why use main()?

To keep the program's execution flow organized.

### 16. What does this mean?

```python
if __name__ == "__main__":
    main()
```

It runs `main()` only when the file is executed directly.

---

## Modules / Libraries

### 17. What is a module?

A Python `.py` file.

### 18. What is a package?

A folder/collection of Python modules.

### 19. What is a library?

Reusable functionality distributed as modules/packages.

### 20. Standard library vs third-party?

Standard library ships with Python.

Examples:

- os
- sys
- json
- csv
- re
- subprocess
- datetime

Third-party libraries are separately installed.

Examples:

- boto3
- requests
- pandas
- PyYAML
- kubernetes

### 21. How do you identify a third-party package?

Often installed with pip and visible with:

```bash
python -m pip show boto3
python -m pip list
```

Third-party modules commonly live under `site-packages`.

---

## requirements.txt

### 22. What does requirements.txt do?

Defines external Python dependencies.

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

### 23. requirements.txt vs import?

`requirements.txt` installs.

`import` loads/uses.

---

## Exceptions

### 24. try / except?

```python
try:
    do_work()
except Exception as e:
    print(e)
```

### 25. finally?

Runs whether the operation succeeds or fails.

Common use: cleanup.

---

## Files / JSON / CSV

### 26. Why with open()?

It automatically closes the file.

### 27. Why JSON is important?

Cloud SDKs, APIs and automation tools commonly use JSON-like structured data.

### 28. json.loads vs json.dumps?

`loads`: JSON string -> Python object.

`dumps`: Python object -> JSON string.

### 29. csv.reader vs csv.DictReader?

`csv.reader`: rows as lists.

`csv.DictReader`: rows as dictionaries using header names.

---

## DevOps modules

### 30. os?

Operating-system interaction, environment variables and paths.

### 31. sys?

Python runtime information and CLI arguments.

### 32. subprocess?

Runs external CLI/OS commands.

### 33. re?

Regular expressions for matching/parsing strings.

### 34. datetime?

Date/time manipulation.

### 35. requests?

HTTP client library.

### 36. boto3?

AWS SDK for Python.

### 37. kubernetes?

Python client for Kubernetes API interaction.

---

## Important built-ins

### 38. len()?

Number of items.

### 39. sorted()?

Returns sorted values.

### 40. min()/max()?

Smallest/largest values.

### 41. any()?

True when at least one value is truthy.

### 42. all()?

True when all values are truthy.

### 43. .get() on dictionary?

Safely retrieves a key.

```python
state = instance.get("State", {}).get("Name")
```

---

## Practical Automation Example

Be able to explain this:

```python
import os
import boto3


def get_running_instances(region: str) -> list[str]:
    ec2 = boto3.client("ec2", region_name=region)
    response = ec2.describe_instances()

    result = []

    for reservation in response.get("Reservations", []):
        for instance in reservation.get("Instances", []):
            if instance.get("State", {}).get("Name") == "running":
                result.append(instance.get("InstanceId"))

    return result


def main():
    region = os.getenv("AWS_REGION", "ap-south-1")

    try:
        instances = get_running_instances(region)

        for index, instance_id in enumerate(instances, start=1):
            print(f"{index}. {instance_id}")

    except Exception as exc:
        print(f"Error: {exc}")


if __name__ == "__main__":
    main()
```

Concepts demonstrated:

- import
- standard library
- third-party library
- function
- arguments
- return
- type hints
- boto3
- environment variables
- list
- dictionary
- nested loop
- conditions
- .get()
- append()
- try/except
- enumerate()
- main()
