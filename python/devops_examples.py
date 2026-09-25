"""Practical Python patterns for DevOps/SRE interview revision."""

import json
import os
import re
import subprocess
from datetime import datetime, timedelta


def environment_variables():
    region = os.getenv("AWS_REGION", "ap-south-1")
    environment = os.getenv("ENVIRONMENT", "dev").strip().lower()

    print(f"Region: {region}")
    print(f"Environment: {environment}")


def file_handling():
    file_name = "/tmp/python-devops-example.txt"

    with open(file_name, "w", encoding="utf-8") as file:
        file.write("deployment=successful\n")

    with open(file_name, "r", encoding="utf-8") as file:
        content = file.read()

    print(content)


def json_example():
    payload = {
        "cluster": "prod-eks",
        "replicas": 3,
        "healthy": True,
    }

    json_string = json.dumps(payload, indent=2)
    print(json_string)

    decoded = json.loads(json_string)
    print(decoded["cluster"])


def subprocess_example():
    result = subprocess.run(
        ["python", "--version"],
        text=True,
        capture_output=True,
        check=False,
    )

    print("return code:", result.returncode)
    print("stdout:", result.stdout.strip())
    print("stderr:", result.stderr.strip())


def regex_example():
    image_tag = "api-master-42-1"

    numbers = re.findall(r"\d+", image_tag)
    print(numbers)


def datetime_example():
    now = datetime.now()
    yesterday = now - timedelta(days=1)

    print("today:", now.strftime("%Y%m%d"))
    print("yesterday:", yesterday.strftime("%Y%m%d"))


def safe_api_style_processing():
    response = {
        "Reservations": [
            {
                "Instances": [
                    {
                        "InstanceId": "i-001",
                        "State": {"Name": "running"},
                    },
                    {
                        "InstanceId": "i-002",
                        "State": {"Name": "stopped"},
                    },
                ]
            }
        ]
    }

    running_instances = []

    for reservation in response.get("Reservations", []):
        for instance in reservation.get("Instances", []):
            if instance.get("State", {}).get("Name") == "running":
                running_instances.append(instance.get("InstanceId"))

    print(running_instances)


def exception_handling():
    items = ["10", "bad", "30"]

    for item in items:
        try:
            number = int(item)
            print(number)
        except ValueError as exc:
            print(f"Skipping invalid value {item}: {exc}")
            continue
        finally:
            print(f"Finished attempt for {item}")


def boto3_example():
    """
    Example only.

    Requires:
        pip install boto3
        valid AWS credentials

    Uncomment to run:

    import boto3

    ec2 = boto3.client("ec2", region_name="ap-south-1")
    response = ec2.describe_instances()

    for reservation in response.get("Reservations", []):
        for instance in reservation.get("Instances", []):
            print(
                instance.get("InstanceId"),
                instance.get("State", {}).get("Name"),
            )
    """


def requests_example():
    """
    Example only.

    Requires:
        pip install requests

    Uncomment to run:

    import requests

    response = requests.get(
        "https://example.com",
        timeout=10,
    )

    print(response.status_code)
    print(response.text)
    """


def kubernetes_example():
    """
    Example only.

    Requires:
        pip install kubernetes
        kubeconfig access

    Uncomment to run:

    from kubernetes import client, config

    config.load_kube_config()

    v1 = client.CoreV1Api()
    pods = v1.list_pod_for_all_namespaces()

    for pod in pods.items:
        print(
            pod.metadata.namespace,
            pod.metadata.name,
        )
    """


def main():
    environment_variables()
    file_handling()
    json_example()
    subprocess_example()
    regex_example()
    datetime_example()
    safe_api_style_processing()
    exception_handling()


if __name__ == "__main__":
    main()
