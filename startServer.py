from mencius.server import Server
from config import Configs
import sys

def main():
    config = Configs().two_clients_single_server()
    server = Server(sys.argv[1], config=config) 
    server.start_node()

if __name__ == "__main__":
    main()