from mencius.server import Server as MenciusServer
from multipaxos.server import Server as MultipaxosServer
from simple.server import Server as SimpleServer
from mencius_physicaltime.server import Server as RobustMenciusServer

from config import Configs
import argparse
import logging
import os


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-n", "--name", type=str, required=True, help="The name of the server"
    )
    parser.add_argument(
        "-t", "--type", type=str, required=True, help="The type of the server"
    )
    parser.add_argument(
        "-c", "--config", type=str, required=False, help="The config"
    )
    parser.add_argument(
        "-g", "--debug", type=str, required=False, help="The name of the server"
    )
    parser.add_argument(
        "-l", "--log", type=str, required=False, help="The name of the file to log to"
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
    if args.log:
        os.makedirs(os.path.dirname(args.log), exist_ok=True)
        fh = logging.FileHandler(args.log)
        logger.addHandler(fh)

    config = getattr(Configs(), args.config)()

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
        case "robust_mencius":
            server = RobustMenciusServer(args.name, config=config, logger=logger, servers=servers)
        case _:
            raise ValueError("Invalid type")
    server.start_node()


if __name__ == "__main__":
    main()
