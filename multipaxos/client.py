from .utils import Message, Node, Timer
from .messages import Request
from .timers import RequestTimer
import zmq
import threading


class Client(Node):
    def __init__(self, name: str, config: dict = {}, logger=None):
        super().__init__(name, config, logger)
        self.functions = {
            "Response": self.handle_response,
        }
        self.timers = {
            "RequestTimer": self.handle_request_timer,
        }
        self.seq_num = 0
        self.condition = threading.Condition()

    def send_request(self, req, server):
        with self.condition:
            message = Request(
                {
                    "AMOCommand": {
                        "command": req,
                        "client": self.name,
                        "seqNum": self.seq_num,
                    }
                }
            )
            self.send_message(message, server)
            self.start_timer(
                RequestTimer(
                    {
                        "message": message,
                        "name": server,
                    }
                )
            )
            while message.args["AMOCommand"]["seqNum"] >= self.seq_num:
                self.condition.wait()

    def handle_message(self, message):
        self.functions[message.message_type](**message.args)

    def handle_response(self, AMOCommand: str, AMOResponse: str):
        with self.condition:
            if AMOCommand["seqNum"] == self.seq_num:
                self.seq_num += 1
                self.condition.notify()

    def handle_timer(self, timer: Timer):
        self.timers[timer.timer_type](**timer.args)

    def handle_request_timer(self, message, name):
        if message.args["AMOCommand"]["seqNum"] >= self.seq_num:
            self.send_message(message, name)
            self.start_timer(RequestTimer({"message": message, "name": name}))
