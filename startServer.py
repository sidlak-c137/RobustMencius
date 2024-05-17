from mencius.server import Server

def main():
    server = Server("server", all_nodes={"server": "127.0.0.1:8080"}) 
    server.start_node()

if __name__ == "__main__":
    main()