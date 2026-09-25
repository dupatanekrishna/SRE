"""Functions, modules, imports, and main() pattern."""


def greet(name: str) -> None:
    print(f"Hello {name}")


def add(a: int, b: int) -> int:
    return a + b


def connect(region: str = "us-east-1") -> None:
    print(f"Connecting to region: {region}")


def show_servers(*servers: str) -> None:
    for server in servers:
        print(server)


def show_config(**config: str) -> None:
    for key, value in config.items():
        print(key, value)


def server_info() -> tuple[str, str, int]:
    return "prod", "10.0.1.5", 443


def main():
    greet("DevOps")

    result = add(10, 20)
    print(result)

    connect()
    connect("ap-south-1")

    show_servers("web1", "web2", "web3")

    show_config(
        region="us-east-1",
        environment="prod",
    )

    environment, ip_address, port = server_info()

    print(environment)
    print(ip_address)
    print(port)


if __name__ == "__main__":
    main()

# Important:
#
# When this file is executed directly:
#
#     python functions_modules.py
#
# __name__ == "__main__" is True, so main() runs.
#
# If another Python file imports this module:
#
#     import functions_modules
#
# the main() block is not automatically executed.
