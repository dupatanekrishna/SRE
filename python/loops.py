"""Looping examples for DevOps/SRE revision."""


def for_loop():
    servers = ["web1", "web2", "web3"]

    for server in servers:
        print(server)


def range_examples():
    for i in range(5):
        print(i)

    for i in range(1, 6):
        print(i)

    for i in range(0, 10, 2):
        print(i)


def enumerate_example():
    servers = ["web1", "web2", "web3"]

    for index, server in enumerate(servers, start=1):
        print(index, server)


def while_loop():
    attempt = 1

    while attempt <= 3:
        print(f"Deployment attempt {attempt}")
        attempt += 1


def break_example():
    environments = ["dev", "stage", "prod", "test"]

    for environment in environments:
        if environment == "prod":
            print("Found production. Stopping search.")
            break

        print(environment)


def continue_example():
    instances = [
        {"id": "i-001", "state": "running"},
        {"id": "i-002", "state": "terminated"},
        {"id": "i-003", "state": "stopped"},
    ]

    for instance in instances:
        if instance["state"] == "terminated":
            continue

        print(instance["id"])


def nested_loop():
    response = {
        "Reservations": [
            {
                "Instances": [
                    {"InstanceId": "i-001"},
                    {"InstanceId": "i-002"},
                ]
            },
            {
                "Instances": [
                    {"InstanceId": "i-003"},
                ]
            },
        ]
    }

    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            print(instance["InstanceId"])


def list_comprehension():
    instances = [
        {"id": "i-001", "state": "running"},
        {"id": "i-002", "state": "stopped"},
        {"id": "i-003", "state": "running"},
    ]

    running = [
        instance
        for instance in instances
        if instance["state"] == "running"
    ]

    print(running)


def main():
    for_loop()
    range_examples()
    enumerate_example()
    while_loop()
    break_example()
    continue_example()
    nested_loop()
    list_comprehension()


if __name__ == "__main__":
    main()
