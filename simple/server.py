from .utils import Node
from .kvstore import AMOKVStore
from .messages import Response
import threading

class Server(Node):
    def __init__(self, name: str, config: dict = {}, logger=None, servers=[]):
        super().__init__(name, config, logger)
        self.functions = {
            "Request": self.handle_request,
        }
        self.application = AMOKVStore()
        self.lock = threading.Lock()
    
    def handle_message(self, message):
        self.functions[message.message_type](**message.args)
    
    def handle_request(self, AMOCommand: dict):
        with self.lock:
            response = Response({
                "AMOCommand": AMOCommand,
                "AMOResponse": self.application.execute(AMOCommand),
            })
            self.send_message(response, AMOCommand["client"])