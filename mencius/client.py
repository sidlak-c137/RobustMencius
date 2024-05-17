from mencius.utils import Message
from .utils import Node
from .messages import Request
import zmq
import threading

class Client(Node):
    def __init__(self, name: str, all_nodes: dict = {}, requests: list = []):
        super().__init__(name, all_nodes)
        self.requests = requests
        self.functions = {
            "Response": self.handle_response,
        }
        self.seq_num = 0
    
    def start_node(self):
        class Listen(threading.Thread):
            def run(thread):
                while True:
                    context = zmq.Context()
                    socket = context.socket(zmq.REP)
                    if self.name in self.all_nodes:
                        name = self.all_nodes[self.name]
                    else:
                        name = self.name
                    socket.bind("tcp://{}".format(name))
                    message = Message.deserialize(socket.recv())
                    print("Received: {}".format(message))
                    self.handle(message)
        
        class Send(threading.Thread):
            def run(thread):
                context = zmq.Context()
                socket = context.socket(zmq.REQ)
                for i in range(len(self.requests)):
                    command = Request({
                        "AMOCommand": {
                            "command": self.requests[self.seq_num]["command"],
                            "clientAddr": self.name,
                            "seqNum": self.seq_num,
                        }
                    })
                    message, name = command, self.requests[self.seq_num]["server"]
                    context = zmq.Context()
                    socket = context.socket(zmq.REQ)
                    if name in self.all_nodes:
                        name = self.all_nodes[name]
                    socket.connect("tcp://{}".format(name))
                    socket.send(message.serialize())
                    print("Sent: {}".format(message))
                    socket.close()
                    while i != self.seq_num - 1:
                        continue

        self.listen_thread = Listen()
        self.send_thread = Send()
        self.listen_thread.start()
        self.send_thread.start()
            

    def handle(self, message):
        self.functions[message.message_type](**message.args)
    
    def handle_response(self, AMOCommand: str, AMOResponse: str):
        if AMOCommand["seqNum"] == self.seq_num:
            self.seq_num += 1