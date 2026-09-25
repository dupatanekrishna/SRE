"""Python basics for DevOps/SRE revision."""


def variables_and_types():
    cluster = "prod-eks"
    replicas = 3
    cpu = 75.5
    healthy = True
    result = None

    print(cluster, type(cluster))
    print(replicas, type(replicas))
    print(cpu, type(cpu))
    print(healthy, type(healthy))
    print(result, type(result))


def strings():
    cluster = "prod-eks"

    print(cluster[0])
    print(cluster[-1])

    name = "  PROD-EKS  "
    print(name.strip())
    print(name.strip().lower())
    print(name.strip().upper())

    print(f"Checking cluster: {cluster}")


def lists_and_slicing():
    servers = ["server1", "server2", "server3", "server4", "server5"]

    print(servers[0])
    print(servers[-1])
    print(servers[1:4])
    print(servers[:2])
    print(servers[2:])
    print(servers[:])
    print(servers[::-1])
    print(servers[::2])
    print(servers[:-1])

    servers.append("server6")
    print(servers)

    servers.remove("server6")
    print(servers)


def tuples():
    endpoint = ("10.0.1.25", 8080)
    host, port = endpoint

    print(host)
    print(port)


def dictionaries():
    server = {
        "name": "web01",
        "ip": "10.0.1.10",
        "status": "running",
    }

    print(server["name"])
    print(server.get("instance_id"))
    print(server.get("instance_id", "unknown"))

    server["status"] = "stopped"
    server["region"] = "ap-south-1"

    for key, value in server.items():
        print(key, value)


def sets():
    service_tags = ["api", "web", "api", "worker", "web"]
    unique_tags = set(service_tags)

    print(unique_tags)

    seen = set()

    for tag in service_tags:
        if tag not in seen:
            seen.add(tag)
            print(f"Processing new tag: {tag}")


def type_conversion():
    port = int("8080")
    cpu = float("72.5")
    count = str(10)

    print(port, type(port))
    print(cpu, type(cpu))
    print(count, type(count))


def useful_builtins():
    values = [20, 80, 40]

    print("length:", len(values))
    print("sorted:", sorted(values))
    print("minimum:", min(values))
    print("maximum:", max(values))
    print("any:", any([False, False, True]))
    print("all:", all([True, True, True]))


def main():
    variables_and_types()
    strings()
    lists_and_slicing()
    tuples()
    dictionaries()
    sets()
    type_conversion()
    useful_builtins()


if __name__ == "__main__":
    main()
