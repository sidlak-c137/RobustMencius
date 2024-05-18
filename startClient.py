from simple.client import Client
from config import Configs
import argparse
import logging

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--name', type=str, required=True, help="The name of the client")
    parser.add_argument('-g', '--debug', type=str, required=False, help="The name of the client")
    args = parser.parse_args()

    match args.debug:
        case "DEBUG":
            logging.basicConfig(level=logging.DEBUG)
        case "INFO":
            logging.basicConfig(level=logging.INFO)
        case "WARNING":
            logging.basicConfig(level=logging.WARNING)
        case "ERROR":
            logging.basicConfig(level=logging.ERROR)
        case "CRITICAL":
            logging.basicConfig(level=logging.CRITICAL)
        case _:
            logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()

    config = Configs().two_clients_single_server()
    client = Client(args.name, config=config, logger=logger)
    client.start_node()
    for i in range(5):
        client.send_request({
            "type": "PUT",
            "key": "B",
            "value": i,
        }, "server1")
        client.send_request({
            "type": "GET",
            "key": "B",
        }, "server1")
    logger.info("Client %s has finished", args.name)
if __name__ == "__main__":
    main()