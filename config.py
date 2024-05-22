
class Configs():
    def single_client_single_server(self):
        '''
        C <--> S
        '''
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
        '''
        C1 <--> S
        C2 <--> S
        '''
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
    
    def three_clients_three_servers(self):
        '''
        Typical WAN configuration
        S1 <--> S2
        S1 <--> S3
        S2 <--> S3
        C1 <--> S1
        C2 <--> S2
        C3 <--> S3
        '''
        return {
            "server1": {
                "host": "127.0.0.1",
                "wait": 0.003,
                "publish": [("server2", "8080"), ("server3", "8081"), ("client1", "8082")],
                "subscribe": [("server2", "8070"), ("server3", "8071"), ("client1", "8072")]
            },
            "server2": {
                "host": "127.0.0.1",
                "publish": [("server1", "8070"), ("server3", "8083"), ("client2", "8084")],
                "subscribe": [("server1", "8080"), ("server3", "8073"), ("client2", "8074")]
            },
            "server3": {
                "host": "127.0.0.1",
                "publish": [("server1", "8071"), ("server2", "8073"), ("client3", "8085")],
                "subscribe": [("server1", "8081"), ("server2", "8083"), ("client3", "8075")]
            },
            "client1": {
                "host": "127.0.0.1",
                "publish": [("server1", "8072")],
                "subscribe": [("server1", "8082")]
            },
            "client2": {
                "host": "127.0.0.1",
                "publish": [("server2", "8074")],
                "subscribe": [("server2", "8084")]
            },
            "client3": {
                "host": "127.0.0.1",
                "publish": [("server3", "8075")],
                "subscribe": [("server3", "8085")]
            },
        }