import zmq
import pickle
import threading

class Message:
    def __init__(self, message_type, args: dict = {}):
        self.message_type = message_type
        self.args = args

    def __str__(self):
        return "{}: {}".format(self.message_type, self.args)

    def serialize(self):
        return pickle.dumps({"type": self.message_type, "args": self.args})

    def deserialize(serialized_message: bytes):
        obj = pickle.loads(serialized_message)
        return Message(obj["type"], obj["args"])


class Node():
    def __init__(self, name: str, all_nodes: dict = {}):
        self.name = name
        self.all_nodes = all_nodes
        self.send_queue = []
    
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
                while True:
                    if len(self.send_queue) == 0:
                        continue
                    context = zmq.Context()
                    socket = context.socket(zmq.REQ)
                    message, name = self.send_queue.pop(0)
                    context = zmq.Context()
                    socket = context.socket(zmq.REQ)
                    if name in self.all_nodes:
                        name = self.all_nodes[name]
                    socket.connect("tcp://{}".format(name))
                    socket.send(message.serialize())
                    print("Sent: {}".format(message))
                    socket.close()

        self.listen_thread = Listen()
        self.send_thread = Send()
        self.listen_thread.start()
        self.send_thread.start()
    
    def send_message(self, message: Message, name: str):
        self.send_queue.append((message, name))
    
    def handle(self, message: Message):
        pass

            
    
