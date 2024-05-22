from mencius.server import Server
from config import Configs
import argparse
import logging


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-n", "--name", type=str, required=True, help="The name of the server"
    )
    parser.add_argument(
        "-g", "--debug", type=str, required=False, help="The name of the server"
    )
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

    config = Configs().three_clients_three_servers()
    servers = []
    for k in config:
        if k.startswith("server"):
            servers.append(k)
    server = Server(args.name, config=config, logger=logger, servers=servers)
    server.start_node()


if __name__ == "__main__":
    main()
