
class Configs():
    WORKLOAD_SIZE = 100000

    def single_client_single_server(self):
        '''
        C <--> S
        '''

        return {
            "server1": {
                "publish": [("client1", "127.0.0.1:8080")],
                "subscribe": [("client1", "127.0.0.1:8070")]
            },
            "client1": {
                "publish": [("server1", "127.0.0.1:8070")],
                "subscribe": [("server1", "127.0.0.1:8080")],
            }
        }
    
    def single_client_single_server_cl(self):
        '''
        C <--> S
        '''

        return {
            "server1": {
                "publish": [("client1", "10.10.4.2:8080")],
                "subscribe": [("client1", "10.10.4.1:8070")]
            },
            "client1": {
                "publish": [("server1", "10.10.4.1:8070")],
                "subscribe": [("server1", "10.10.4.2:8080")],
            }
        }
    
    def two_clients_single_server(self):
        '''
        C1 <--> S
        C2 <--> S
        '''
        return {
            "server1": {
                "publish": [("client1", "127.0.0.1:8080"), ("client2", "127.0.0.1:8081")],
                "subscribe": [("client1", "127.0.0.1:8070"), ("client2", "127.0.0.1:8071")]
            },
            "client1": {
                "publish": [("server1", "127.0.0.1:8070")],
                "subscribe": [("server1", "127.0.0.1:8080")]
            },
            "client2": {
                "publish": [("server1", "127.0.0.1:8071")],
                "subscribe": [("server1", "127.0.0.1:8081")]
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
            "tiling": [0, 1, 2],
            "server1": {
                "wait": 0.003,
                "publish": [("server2", "127.0.0.1:8080"), ("server3", "127.0.0.1:8081"), ("client1", "127.0.0.1:8082")],
                "subscribe": [("server2", "127.0.0.1:8070"), ("server3", "127.0.0.1:8071"), ("client1", "127.0.0.1:8072")]
            },
            "server2": {
                "publish": [("server1", "127.0.0.1:8070"), ("server3", "127.0.0.1:8083"), ("client2", "127.0.0.1:8084")],
                "subscribe": [("server1", "127.0.0.1:8080"), ("server3", "127.0.0.1:8073"), ("client2", "127.0.0.1:8074")]
            },
            "server3": {
                "publish": [("server1", "127.0.0.1:8071"), ("server2", "127.0.0.1:8073"), ("client3", "127.0.0.1:8085")],
                "subscribe": [("server1", "127.0.0.1:8081"), ("server2", "127.0.0.1:8083"), ("client3", "127.0.0.1:8075")]
            },
            "client1": {
                "publish": [("server1", "127.0.0.1:8072")],
                "subscribe": [("server1", "127.0.0.1:8082")]
            },
            "client2": {
                "publish": [("server2", "127.0.0.1:8074")],
                "subscribe": [("server2", "127.0.0.1:8084")]
            },
            "client3": {
                "publish": [("server3", "127.0.0.1:8075")],
                "subscribe": [("server3", "127.0.0.1:8085")]
            },
        }
    
    def three_clients_three_servers_cl(self):
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
            "tiling": [0, 1, 2],
            "server1": {
                "publish": [("server2", "10.10.1.1:8080"), ("server3", "10.10.2.1:8081"), ("client1", "10.10.4.2:8082")],
                "subscribe": [("server2", "10.10.1.2:8070"), ("server3", "10.10.2.2:8071"), ("client1", "10.10.4.1:8072")]
            },
            "server2": {
                "publish": [("server1", "10.10.1.2:8070"), ("server3", "10.10.3.1:8083"), ("client2", "10.10.5.2:8084")],
                "subscribe": [("server1", "10.10.1.1:8080"), ("server3", "10.10.3.2:8073"), ("client2", "10.10.5.1:8074")]
            },
            "server3": {
                "publish": [("server1", "10.10.2.2:8071"), ("server2", "10.10.3.2:8073"), ("client3", "10.10.6.2:8085")],
                "subscribe": [("server1", "10.10.2.1:8081"), ("server2", "10.10.3.1:8083"), ("client3", "10.10.6.1:8075")]
            },
            "client1": {
                "publish": [("server1", "10.10.4.1:8072")],
                "subscribe": [("server1", "10.10.4.2:8082")]
            },
            "client2": {
                "publish": [("server2", "10.10.5.1:8074")],
                "subscribe": [("server2", "10.10.5.2:8084")]
            },
            "client3": {
                "publish": [("server3", "10.10.6.1:8075")],
                "subscribe": [("server3", "10.10.6.2:8085")]
            },
        }
    
    def three_clients_three_servers_cl_slow_0(self):
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
            "tiling": [0, 1, 2],
            "server1": {
                "publish": [("server2", "10.10.1.1:8080"), ("server3", "10.10.2.1:8081"), ("client1", "10.10.4.2:8082")],
                "subscribe": [("server2", "10.10.1.2:8070"), ("server3", "10.10.2.2:8071"), ("client1", "10.10.4.1:8072")]
            },
            "server2": {
                "publish": [("server1", "10.10.1.2:8070"), ("server3", "10.10.3.1:8083"), ("client2", "10.10.5.2:8084")],
                "subscribe": [("server1", "10.10.1.1:8080"), ("server3", "10.10.3.2:8073"), ("client2", "10.10.5.1:8074")]
            },
            "server3": {
                "wait": 0.005,
                "publish": [("server1", "10.10.2.2:8071"), ("server2", "10.10.3.2:8073"), ("client3", "10.10.6.2:8085")],
                "subscribe": [("server1", "10.10.2.1:8081"), ("server2", "10.10.3.1:8083"), ("client3", "10.10.6.1:8075")]
            },
            "client1": {
                "publish": [("server1", "10.10.4.1:8072")],
                "subscribe": [("server1", "10.10.4.2:8082")]
            },
            "client2": {
                "publish": [("server2", "10.10.5.1:8074")],
                "subscribe": [("server2", "10.10.5.2:8084")]
            },
            "client3": {
                "publish": [("server3", "10.10.6.1:8075")],
                "subscribe": [("server3", "10.10.6.2:8085")]
            },
        }
    
    def three_clients_three_servers_cl_slow_1(self):
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
            "tiling": [0, 1, 0, 1, 0, 1, 2, 0, 1, 0, 1],
            "server1": {
                "publish": [("server2", "10.10.1.1:8080"), ("server3", "10.10.2.1:8081"), ("client1", "10.10.4.2:8082")],
                "subscribe": [("server2", "10.10.1.2:8070"), ("server3", "10.10.2.2:8071"), ("client1", "10.10.4.1:8072")]
            },
            "server2": {
                "publish": [("server1", "10.10.1.2:8070"), ("server3", "10.10.3.1:8083"), ("client2", "10.10.5.2:8084")],
                "subscribe": [("server1", "10.10.1.1:8080"), ("server3", "10.10.3.2:8073"), ("client2", "10.10.5.1:8074")]
            },
            "server3": {
                "wait": 0.005,
                "publish": [("server1", "10.10.2.2:8071"), ("server2", "10.10.3.2:8073"), ("client3", "10.10.6.2:8085")],
                "subscribe": [("server1", "10.10.2.1:8081"), ("server2", "10.10.3.1:8083"), ("client3", "10.10.6.1:8075")]
            },
            "client1": {
                "publish": [("server1", "10.10.4.1:8072")],
                "subscribe": [("server1", "10.10.4.2:8082")]
            },
            "client2": {
                "publish": [("server2", "10.10.5.1:8074")],
                "subscribe": [("server2", "10.10.5.2:8084")]
            },
            "client3": {
                "publish": [("server3", "10.10.6.1:8075")],
                "subscribe": [("server3", "10.10.6.2:8085")]
            },
        }
    
    def three_clients_three_servers_cl_slow_2(self):
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
            "tiling": [0, 1, 0, 1, 0, 1, 2, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
            "server1": {
                "publish": [("server2", "10.10.1.1:8080"), ("server3", "10.10.2.1:8081"), ("client1", "10.10.4.2:8082")],
                "subscribe": [("server2", "10.10.1.2:8070"), ("server3", "10.10.2.2:8071"), ("client1", "10.10.4.1:8072")]
            },
            "server2": {
                "publish": [("server1", "10.10.1.2:8070"), ("server3", "10.10.3.1:8083"), ("client2", "10.10.5.2:8084")],
                "subscribe": [("server1", "10.10.1.1:8080"), ("server3", "10.10.3.2:8073"), ("client2", "10.10.5.1:8074")]
            },
            "server3": {
                "wait": 0.005,
                "publish": [("server1", "10.10.2.2:8071"), ("server2", "10.10.3.2:8073"), ("client3", "10.10.6.2:8085")],
                "subscribe": [("server1", "10.10.2.1:8081"), ("server2", "10.10.3.1:8083"), ("client3", "10.10.6.1:8075")]
            },
            "client1": {
                "publish": [("server1", "10.10.4.1:8072")],
                "subscribe": [("server1", "10.10.4.2:8082")]
            },
            "client2": {
                "publish": [("server2", "10.10.5.1:8074")],
                "subscribe": [("server2", "10.10.5.2:8084")]
            },
            "client3": {
                "publish": [("server3", "10.10.6.1:8075")],
                "subscribe": [("server3", "10.10.6.2:8085")]
            },
        }