import time
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


class Timer:
    def __init__(self, timer_type, ms: int, args: dict = {}):
        self.timer_type = timer_type
        self.ms = ms
        self.args = args

    def __str__(self):
        return "{}: {}".format(self.timer_type, self.args)


class Node:
    def __init__(self, name: str, config: dict = {}, logger=None):
        self.name = name
        self.config = config
        self.logger = logger
        self.condition = threading.Condition()
        self.send_queue = []

    def start_node(self):
        class Listen(threading.Thread):
            def run(thread):
                context = zmq.Context()
                socket = context.socket(zmq.SUB)
                # Subscribe to all nodes (except self)
                for name, port in self.config[self.name]["subscribe"]:
                    host = self.config[name]["host"]
                    self.logger.info(f"Subscribing to {name} on {host}:{port}")
                    socket.connect(f"tcp://{host}:{port}")
                    socket.setsockopt(zmq.SUBSCRIBE, b"")
                # Start listening for messages
                while True:
                    message = Message.deserialize(socket.recv())
                    if "wait" in self.config[self.name]:
                        time.sleep(self.config[self.name]["wait"])
                    self.handle_message(message)

        class Send(threading.Thread):
            def run(thread):
                sockets = {}
                for name, port in self.config[self.name]["publish"]:
                    context = zmq.Context()
                    host = self.config[self.name]["host"]
                    socket = context.socket(zmq.PUB)
                    socket.sndhwm = 1100000
                    self.logger.info(f"Publishing to {name} on {host}:{port}")
                    socket.bind(f"tcp://{host}:{port}")
                    sockets[name] = socket
                # Start sending messages
                while True:
                    with self.condition:
                        while len(self.send_queue) == 0:
                            self.condition.wait()
                        message, name = self.send_queue.pop(0)
                        if name not in sockets:
                            continue
                        socket = sockets[name]
                        socket.send(message.serialize())
                        self.logger.debug("-> {}: {}".format(name, message))

        self.listen_thread = Listen()
        self.send_thread = Send()
        self.listen_thread.start()
        self.send_thread.start()

    def send_message(self, message: Message, name: str):
        with self.condition:
            self.send_queue.append((message, name))
            self.condition.notify()
    
    def broadcast_message(self, message: Message, servers: list):
        with self.condition:
            for server in servers:
                self.send_queue.append((message, server))
            self.condition.notify()

    def start_timer(self, timer: Timer):
        class Timer(threading.Thread):
            def run(thread):
                time.sleep(timer.ms / 1000)
                self.handle_timer(timer)

        self.timer_thread = Timer()
        self.timer_thread.start()

    def handle_message(self, message: Message):
        pass
