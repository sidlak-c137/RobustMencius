
class Configs():
    def single_client_single_server(self):
        return {
            "server1": {
                "host": "127.0.0.1",
                "publish": [("client1", "8080")],
                "subscribe": [("client1", "8070")]
            },
            "client1": {
                "host": "127.0.0.1",
                "publish": [("server1", "8070")],
                "subscribe": [("server1", "8080")]
            }
        }
    
    def two_clients_single_server(self):
        return {
            "server1": {
                "host": "127.0.0.1",
                "publish": [("client1", "8080"), ("client2", "8081")],
                "subscribe": [("client1", "8070"), ("client2", "8071")]
            },
            "client1": {
                "host": "127.0.0.1",
                "publish": [("server1", "8070")],
                "subscribe": [("server1", "8080")]
            },
            "client2": {
                "host": "127.0.0.1",
                "publish": [("server1", "8071")],
                "subscribe": [("server1", "8081")]
            }
        }