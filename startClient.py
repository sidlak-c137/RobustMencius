from mencius.client import Client
from config import Configs
import sys

def main():
    config = Configs().two_clients_single_server()
    client = Client(sys.argv[1], config=config)
    client.start_node()
    for i in range(10000):
        client.send_request({
            "type": "PUT",
            "key": "B",
            "value": i,
        }, "server1")
        client.send_request({
            "type": "GET",
            "key": "B",
        }, "server1")

if __name__ == "__main__":
    main()