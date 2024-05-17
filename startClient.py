from mencius.client import Client

def main():
    client = Client("127.0.0.1:8070", all_nodes={"server": "127.0.0.1:8080"}, requests=[
        {
            "command": {
                "type": "PUT",
                "key": "A",
                "value": "1",
            },
            "server": "server",
        },
        {
            "command": {
                "type": "GET",
                "key": "A",
            },
            "server": "server",
        },
        {
            "command": {
                "type": "PUT",
                "key": "A",
                "value": "3",
            },
            "server": "server",
        },
        {
            "command": {
                "type": "GET",
                "key": "A",
            },
            "server": "server",
        },
    ])
    client.start_node()

if __name__ == "__main__":
    main()