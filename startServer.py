from mencius.server import Server as MenciusServer
from multipaxos.server import Server as MultipaxosServer
from simple.server import Server as SimpleServer

from config import Configs
import argparse
import logging


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-n", "--name", type=str, required=True, help="The name of the client"
    )
    parser.add_argument(
        "-t", "--type", type=str, required=True, help="The type of the client"
    )
    parser.add_argument(
        "-c", "--config", type=str, required=False, help="The config"
    )
    parser.add_argument(
        "-g", "--debug", type=str, required=False, help="The name of the client"
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
            raise ValueError("Invalid debug level")
    logger = logging.getLogger()

    match args.config:
        case "three_clients_three_servers":
            config = Configs().three_clients_three_servers()
        case "single_client_single_server":
            config = Configs().single_client_single_server()
        case "two_clients_single_server":
            config = Configs().two_clients_single_server()
        case "single_client_single_server_cl":
            config = Configs().single_client_single_server_cl()
        case "three_clients_three_servers_cl":
            config = Configs().three_clients_three_servers_cl()
        case "three_clients_three_servers_cl_slow":
            config = Configs().three_clients_three_servers_cl_slow()
        case _:
            raise ValueError("Invalid config")
    servers = []
    for k in config:
        if k.startswith("server"):
            servers.append(k)
    match args.type:
        case "mencius":
            server = MenciusServer(args.name, config=config, logger=logger, servers=servers)
        case "simple":
            server = SimpleServer(args.name, config=config, logger=logger)
        case "multipaxos":
            server = MultipaxosServer(args.name, config=config, logger=logger, servers=servers)
        case _:
            raise ValueError("Invalid type")
    server.start_node()


if __name__ == "__main__":
    main()
