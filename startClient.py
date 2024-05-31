from mencius.client import Client as MenciusClient
from simple.client import Client as SimpleClient
from multipaxos.client import Client as MultipaxosClient
from mencius_physicaltime.client import Client as RobustMenciusClient
from config import Configs
import argparse
import logging
import os



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
        fh = logging.FileHandler(args.log, mode="w")
        fh.setLevel(args.debug)
        logger.addHandler(fh)

    config = getattr(Configs(), args.config)()
    
    match args.type:
        case "mencius":
            client = MenciusClient(args.name, config=config, logger=logger)
        case "simple":
            client = SimpleClient(args.name, config=config, logger=logger)
        case "multipaxos":
            client = MultipaxosClient(args.name, config=config, logger=logger)
        case "robust_mencius":
            client = RobustMenciusClient(args.name, config=config, logger=logger)
        case _:
            raise ValueError("Invalid type")

    client.start_node()
    server = config[args.name]["publish"][0][0]
    for i in range(2000):
        client.send_request(
            {
                "type": "PUT",
                "key": f"{args.name}",
                "value": i,
            },
            server,
        )
        client.send_request(
            {
                "type": "GET",
                "key": f"{args.name}",
            },
            server,
        )
    logger.info("Client %s has finished", args.name)


if __name__ == "__main__":
    main()
