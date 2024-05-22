from .utils import Node
from .kvstore import AMOKVStore
from .messages import ProposeRequest, Response, ProposeReply, Heartbeat, HeartbeatReply
from .timers import HeartbeatCheckTimer, HeartbeatTimer, ProposeTimer
import threading


class Server(Node):
    def __init__(self, name: str, config: dict = {}, logger=None, servers=[]):
        super().__init__(name, config, logger)
        self.servers = servers
        self.servers_minus_self = [server for server in servers if server != name]
        self.N = len(servers)
        self.functions = {
            "Request": self.handle_request,
            "ProposeRequest": self.handle_propose_request,
            "ProposeReply": self.handle_propose_reply,
            "Heartbeat": self.handle_heartbeat,
            "HeartbeatReply": self.handle_heartbeat_reply,
        }
        self.timers = {
            "HeartbeatTimer": self.handle_heartbeat_timer,
            "ProposeTimer": self.handle_propose_timer,
        }

        self.tiling = [0, 1, 2]
        self.tiling_len = 3
        self.log = {}

        self.application = AMOKVStore()
        self.lock = threading.RLock()
        self.slot_out = 0
        self.slot_in = self.servers.index(name)
        self.local_garbage = 0
        self.garbage_map = {}
        self.proposal_replies = {}

    def start_node(self):
        super().start_node()
        self.start_timer(ProposeTimer({}))

    def handle_message(self, message):
        self.functions[message.message_type](**message.args)

    def handle_timer(self, timer):
        self.timers[timer.timer_type](**timer.args)

    def handle_request(self, AMOCommand: dict):
        with self.lock:
            if self.application.alreadyExecuted(AMOCommand) or self.N == 1:
                response = Response(
                    {
                        "AMOCommand": AMOCommand,
                        "AMOResponse": self.application.execute(AMOCommand),
                    }
                )
                self.send_message(response, AMOCommand["client"])
            else:
                if (AMOCommand, "ACCEPTED") in self.log.values() or (
                    AMOCommand,
                    "CHOSEN",
                ) in self.log.values():
                    return
                self.log[self.slot_in] = (AMOCommand, "ACCEPTED")
                self.proposal_replies[self.slot_in] = set()
                self.proposal_replies[self.slot_in].add(self.name)
                old_slot = self.slot_in
                self.slot_in = self.get_next_slot(self.name, self.slot_in)
                self.broadcast_message(
                    ProposeRequest(
                        {
                            "slot": old_slot,
                            "command": AMOCommand,
                            "sender": self.name,
                        }
                    ),
                    self.servers_minus_self,
                )

    def handle_propose_request(self, slot: int, command: dict, sender: str):
        with self.lock:
            if slot >= self.slot_out and (
                slot not in self.log or self.log[slot][1] != "CHOSEN"
            ):
                self.log[slot] = (command, "ACCEPTED")
                old_slot = self.slot_in
                self.slot_in = max(self.slot_in, self.get_next_slot(self.name, slot))
                for i in range(old_slot, self.slot_in):
                    if self.is_leader(self.name, i):
                        self.log[i] = (None, "CHOSEN")
                self.executeAll()
                self.garbage_map[self.name] = self.slot_out
                self.garbage_collect(self.get_min_slot())
                self.send_message(
                    ProposeReply(
                        {
                            "slot": slot,
                            "slot_out": self.slot_out,
                            "skip_till": self.slot_in,
                            "sender": self.name,
                        }
                    ),
                    sender,
                )

    def handle_propose_reply(self, slot: int, slot_out: int, skip_till: int, sender: str):
        with self.lock:
            while skip_till >= self.slot_out:
                skip_till = self.get_prev_slot(sender, skip_till)
                if skip_till not in self.log and skip_till >= self.slot_out:
                    self.logger.debug(f"Skipping slot {skip_till}")
                    self.log[skip_till] = (None, "CHOSEN")
            self.executeAll()
            self.garbage_map[self.name] = self.slot_out
            self.garbage_map[sender] = max(self.garbage_map.get(sender, 0), slot_out)
            self.garbage_collect(self.get_min_slot())
            if (
                self.is_leader(self.name, slot)
                and slot in self.log
                and self.log[slot][1] == "ACCEPTED"
            ):
                self.proposal_replies[slot].add(sender)
                if len(self.proposal_replies[slot]) > self.N // 2:
                    if slot >= self.slot_out and self.log[slot][1] == "ACCEPTED":
                        self.log[slot] = (self.log[slot][0], "CHOSEN")
                        self.executeAll()
                        self.garbage_map[self.name] = self.slot_out
                        self.garbage_collect(self.get_min_slot())
                        self.broadcast_message(
                            Heartbeat(
                                {
                                    "log": self.log,
                                    "slot_out": self.slot_out,
                                    "sender": self.name,
                                }
                            ),
                            self.servers_minus_self,
                        )


    def handle_heartbeat(self, log: dict, slot_out: int, sender: str):
        with self.lock:
            self.received_heartbeat = True
            for slot in range(self.slot_out, self.slot_in):
                if slot in log:
                    entry = log[slot]
                    if entry[1] == "CHOSEN":
                        self.log[slot] = entry
            self.executeAll()
            self.garbage_map[sender] = max(self.garbage_map.get(sender, 0), slot_out)
            self.garbage_map[self.name] = self.slot_out
            self.garbage_collect(self.get_min_slot())

    def handle_heartbeat_reply(self, slot_out: int, sender: str):
        with self.lock:
            self.garbage_map[sender] = max(self.garbage_map.get(sender, 0), slot_out)
            self.garbage_collect(self.get_min_slot())

    def handle_propose_timer(self):
        with self.lock:
            self.send_all_proposes()
            self.start_timer(ProposeTimer({}))

    def handle_heartbeat_timer(self):
        with self.lock:
            min_slot_out = self.get_min_slot()
            self.broadcast_message(
                Heartbeat(
                    {
                        "log": self.log,
                        "min_slot_out": min_slot_out,
                        "sender": self.name,
                    }
                ),
                self.servers_minus_self,
            )
            self.start_timer(HeartbeatTimer({}))

    # Utils
    def get_prev_slot(self, server, i):
        with self.lock:
            idx = self.servers.index(server)
            mod = i % self.tiling_len
            i -= 1
            while (i % self.tiling_len) != mod and self.tiling[
                i % self.tiling_len
            ] != idx:
                i -= 1
            return i

    def get_next_slot(self, server, i):
        with self.lock:
            idx = self.servers.index(server)
            mod = i % self.tiling_len
            i += 1
            while (i % self.tiling_len) != mod and self.tiling[
                i % self.tiling_len
            ] != idx:
                i += 1
            return i

    def is_leader(self, server, i):
        with self.lock:
            return self.tiling[i % self.tiling_len] == self.servers.index(server)

    def executeAll(self):
        with self.lock:
            i = self.slot_out
            while i in self.log and self.log[i][1] == "CHOSEN":
                if self.log[i][0] is not None:
                    response = Response(
                        {
                            "AMOCommand": self.log[i][0],
                            "AMOResponse": self.application.execute(self.log[i][0]),
                        }
                    )
                    self.send_message(response, self.log[i][0]["client"])
                i += 1
            self.slot_out = i

    def send_all_proposes(self):
        with self.lock:
            for slot, entry in self.log.items():
                if (
                    slot >= self.slot_out
                    and self.is_leader(self.name, slot)
                    and entry[1] == "ACCEPTED"
                ):
                    self.broadcast_message(
                        ProposeRequest(
                            {
                                "slot": slot,
                                "command": entry[0],
                                "sender": self.name,
                            }
                        ),
                        self.servers_minus_self,
                    )

    def garbage_collect(self, min_slot_out):
        with self.lock:
            for i in range(self.local_garbage, min_slot_out):
                self.log.pop(i, None)
                self.proposal_replies.pop(i, None)
            self.local_garbage = max(self.local_garbage, min_slot_out)

    def get_min_slot(self):
        with self.lock:
            if len(self.garbage_map) == len(self.servers):
                return min(self.garbage_map.values())
            return 0
