from .utils import Node
from .kvstore import AMOKVStore
from .messages import (
    Request,
    Response,
    ProposeRequest,
    ProposeReply,
    Heartbeat,
    HeartbeatReply,
    PrepareRequest,
    PrepareReply,
)
from .timers import HeartbeatCheckTimer, HeartbeatTimer, PrepareTimer, ProposeTimer
import threading
import time


class Server(Node):
    def __init__(self, name: str, config: dict = {}, logger=None, servers=[]):
        super().__init__(name, config, logger)
        self.servers = servers
        self.servers_minus_self = [server for server in servers if server != name]
        self.functions = {
            "Request": self.handle_request,
            "PrepareRequest": self.handle_prepare_request,
            "PrepareReply": self.handle_prepare_reply,
            "ProposeRequest": self.handle_propose_request,
            "ProposeReply": self.handle_propose_reply,
            "Heartbeat": self.handle_heartbeat,
            "HeartbeatReply": self.handle_heartbeat_reply,
        }
        self.timers = {
            "HeartbeatTimer": self.handle_heartbeat_timer,
            "HeartbeatCheckTimer": self.handle_heartbeat_check_timer,
            "PrepareTimer": self.handle_prepare_timer,
            "ProposeTimer": self.handle_propose_timer,
        }
        self.application = AMOKVStore()
        self.lock = threading.RLock()

        self.log = {}
        self.ballot = (0, name)
        self.slot_out = 0
        self.local_garbage = 0
        self.slot_in = 1
        self.is_leader = False
        self.received_heartbeat = False
        self.votes = set()
        self.proposal_replies = {}
        self.garbage_map = {}

    def start_node(self):
        super().start_node()
        self.start_timer(HeartbeatCheckTimer({}))

    def handle_message(self, message):
        with self.lock:
            if "wait" in self.config[self.name]:
                    time.sleep(self.config[self.name]["wait"])
            self.functions[message.message_type](**message.args)

    def handle_timer(self, timer):
        with self.lock:
            if "wait" in self.config[self.name]:
                    time.sleep(self.config[self.name]["wait"])
            self.timers[timer.timer_type](**timer.args)

    def handle_request(self, AMOCommand: dict):
        with self.lock:
            if self.application.alreadyExecuted(AMOCommand) or len(self.servers) == 1:
                response = Response(
                    {
                        "AMOCommand": AMOCommand,
                        "AMOResponse": self.application.execute(AMOCommand),
                    }
                )
                self.send_message(response, AMOCommand["client"])
            else:
                if self.is_leader:
                    self.log[self.slot_in] = (self.ballot, AMOCommand, "ACCEPTED")
                    self.slot_in += 1
                    self.handle_propose_request(
                        self.ballot, self.slot_in - 1, AMOCommand, self.name
                    )
                    self.broadcast_message(
                        ProposeRequest(
                            {
                                "ballot": self.ballot,
                                "slot": self.slot_in - 1,
                                "command": AMOCommand,
                                "sender": self.name,
                            }
                        ),
                        self.servers_minus_self,
                    )
                elif self.ballot[1] != self.name:
                    self.send_message(Request({
                        "AMOCommand": AMOCommand
                    }), self.ballot[1])


    def handle_prepare_request(self, ballot: tuple, sender: str):
        with self.lock:
            ballot_compare = self.compare_ballots(ballot, self.ballot)
            if ballot_compare > 0:
                self.ballot = ballot
                self.received_heartbeat = True
                self.is_leader = False
                self.proposal_replies.clear()
                self.votes.clear()
            if ballot_compare == 0:
                self.received_heartbeat = True
                if sender == self.name:
                    self.handle_prepare_reply(self.ballot, self.log, self.name)
                else:
                    self.send_message(
                        PrepareReply(
                            {
                                "ballot": self.ballot,
                                "log": self.log,
                                "sender": self.name,
                            }
                        ),
                        sender,
                    )

    def handle_prepare_reply(self, ballot: tuple, log: dict, sender: str):
        with self.lock:
            if (
                self.compare_ballots(ballot, self.ballot) == 0
                and self.name == self.ballot[1]
                and not self.is_leader
            ):
                self.votes.add(sender)
                if self.name != sender:
                    # Merge logs
                    for slot, entry in log.items():
                        if slot > self.slot_out:
                            if (
                                (slot not in self.log)
                                or (
                                    self.compare_ballots(entry[0], self.log[slot][0])
                                    > 0
                                    and self.log[slot][2] != "CHOSEN"
                                )
                                or (entry[2] == "CHOSEN")
                            ):
                                self.log[slot] = entry
                                self.slot_in = max(self.slot_in, slot + 1)
                # Check for majority
                if len(self.votes) > len(self.servers) // 2 and not self.is_leader:
                    self.is_leader = True
                    for slot in range(self.slot_out + 1, self.slot_in):
                        if slot not in self.log:
                            self.log[slot] = (self.ballot, None, "ACCEPTED")
                            self.handle_propose_request(
                                self.ballot, slot, None, self.name
                            )
                        elif self.log[slot][2] == "ACCEPTED":
                            self.log[slot] = (
                                self.ballot,
                                self.log[slot][1],
                                "ACCEPTED",
                            )
                            self.handle_propose_request(
                                self.ballot, slot, self.log[slot][1], self.name
                            )

                self.executeAll()
                self.send_all_proposes()
                self.start_timer(
                    HeartbeatTimer(
                        {
                            "ballot": self.ballot,
                        }
                    )
                )
                self.start_timer(
                    ProposeTimer(
                        {
                            "ballot": self.ballot,
                        }
                    )
                )

    def handle_propose_request(
        self, ballot: tuple, slot: int, command: dict, sender: str
    ):
        with self.lock:
            ballot_compare = self.compare_ballots(ballot, self.ballot)
            if ballot_compare > 0:
                self.ballot = ballot
                self.received_heartbeat = True
                self.is_leader = False
                self.proposal_replies.clear()
                self.votes.clear()
            if ballot_compare == 0 and slot > self.slot_out:
                self.received_heartbeat = True
                if self.name == sender:
                    self.handle_propose_reply(self.ballot, slot, self.name)
                else:
                    if slot not in self.log or self.log[slot][2] != "CHOSEN":
                        self.log[slot] = (self.ballot, command, "ACCEPTED")
                    self.send_message(
                        ProposeReply(
                            {
                                "ballot": self.ballot,
                                "slot": slot,
                                "sender": self.name,
                            }
                        ),
                        sender,
                    )

    def handle_propose_reply(self, ballot: tuple, slot: int, sender: str):
        with self.lock:
            if self.compare_ballots(ballot, self.ballot) == 0 and self.is_leader:
                if slot not in self.proposal_replies:
                    self.proposal_replies[slot] = set()
                self.proposal_replies[slot].add(sender)
                if len(self.proposal_replies[slot]) > len(self.servers) // 2:
                    if slot > self.slot_out and self.log[slot][2] == "ACCEPTED":
                        self.proposal_replies[slot] = set()
                        self.log[slot] = (self.ballot, self.log[slot][1], "CHOSEN")
                        self.broadcast_message(
                            Heartbeat(
                                {
                                    "ballot": self.ballot,
                                    "log": {slot: self.log[slot]},
                                    "min_slot_out": self.local_garbage,
                                    "sender": self.name,
                                }
                            ),
                            self.servers_minus_self,
                        )
                    self.executeAll()
                    self.garbage_map[self.name] = self.slot_out

    def handle_heartbeat(
        self, ballot: tuple, log: dict, min_slot_out: int, sender: str
    ):
        with self.lock:
            ballot_compare = self.compare_ballots(ballot, self.ballot)
            if ballot_compare > 0:
                self.ballot = ballot
                self.received_heartbeat = True
                self.is_leader = False
                self.proposal_replies.clear()
                self.votes.clear()
            if ballot_compare == 0:
                self.received_heartbeat = True
                if ballot_compare == 0 and not self.is_leader:
                    for slot, entry in log.items():
                        if slot > self.slot_out and entry[2] == "CHOSEN":
                            self.log[slot] = entry
                            self.slot_in = max(self.slot_in, slot + 1)
                self.executeAll()
                self.garbage_collect(min_slot_out)
                if self.name != sender:
                    self.send_message(
                        HeartbeatReply(
                            {
                                "ballot": self.ballot,
                                "slot_out": self.slot_out,
                                "sender": self.name,
                            }
                        ),
                        sender,
                    )

    def handle_heartbeat_reply(self, ballot: tuple, slot_out: int, sender: str):
        with self.lock:
            if self.compare_ballots(ballot, self.ballot) == 0 and self.is_leader:
                self.garbage_map[sender] = max(
                    self.garbage_map.get(sender, 0), slot_out
                )
                self.garbage_collect(self.get_min_slot())

    def handle_heartbeat_timer(self, ballot: tuple):
        with self.lock:
            if self.is_leader and self.compare_ballots(ballot, self.ballot) == 0:
                min_slot_out = self.get_min_slot()
                self.broadcast_message(
                    Heartbeat(
                        {
                            "ballot": self.ballot,
                            "log": self.log,
                            "min_slot_out": min_slot_out,
                            "sender": self.name,
                        }
                    ),
                    self.servers_minus_self,
                )
                self.start_timer(
                    HeartbeatTimer(
                        {
                            "ballot": self.ballot,
                        }
                    )
                )

    def handle_heartbeat_check_timer(self):
        with self.lock:
            if not self.received_heartbeat and not self.is_leader:
                self.ballot = (self.ballot[0] + 1, self.name)
                self.votes.clear()
                self.handle_prepare_request(self.ballot, self.name)
                self.broadcast_message(
                    PrepareRequest(
                        {
                            "ballot": self.ballot,
                            "sender": self.name,
                        }
                    ),
                    self.servers_minus_self,
                )
                self.start_timer(
                    PrepareTimer(
                        {
                            "ballot": self.ballot,
                        }
                    )
                )
            self.received_heartbeat = False
            self.start_timer(HeartbeatCheckTimer({}))

    def handle_prepare_timer(self, ballot: tuple):
        with self.lock:
            if not self.is_leader and self.compare_ballots(ballot, self.ballot) == 0:
                self.handle_prepare_request(self.ballot, self.name)
                self.broadcast_message(
                    PrepareRequest(
                        {
                            "ballot": self.ballot,
                            "sender": self.name,
                        }
                    ),
                    self.servers_minus_self,
                )
                self.start_timer(
                    PrepareTimer(
                        {
                            "ballot": self.ballot,
                        }
                    )
                )

    def handle_propose_timer(self, ballot: tuple):
        with self.lock:
            if self.is_leader and self.compare_ballots(ballot, self.ballot) == 0:
                self.send_all_proposes()
                self.start_timer(
                    ProposeTimer(
                        {
                            "ballot": self.ballot,
                        }
                    )
                )

    # Utils
    def compare_ballots(self, ballot1: tuple, ballot2: tuple):
        if ballot1[0] > ballot2[0]:
            return 1
        elif ballot1[0] < ballot2[0]:
            return -1
        else:
            if ballot1[1] > ballot2[1]:
                return 1
            elif ballot1[1] < ballot2[1]:
                return -1
            else:
                return 0

    def executeAll(self):
        i = self.slot_out + 1
        while i in self.log and self.log[i][2] == "CHOSEN":
            if self.log[i][1] is not None:
                response = Response(
                    {
                        "AMOCommand": self.log[i][1],
                        "AMOResponse": self.application.execute(self.log[i][1]),
                    }
                )
                self.send_message(response, self.log[i][1]["client"])
            i += 1
        self.slot_out = i - 1

    def send_all_proposes(self):
        if self.is_leader:
            for slot, entry in self.log.items():
                if slot >= self.slot_out and entry[2] == "ACCEPTED":
                    self.broadcast_message(
                        ProposeRequest(
                            {
                                "ballot": self.ballot,
                                "slot": slot,
                                "command": entry[1],
                                "sender": self.name,
                            }
                        ),
                        self.servers_minus_self,
                    )

    def garbage_collect(self, min_slot_out):
        for i in range(self.local_garbage, min_slot_out + 1):
            self.log.pop(i, None)
            self.proposal_replies.pop(i, None)
        self.local_garbage = max(self.local_garbage, min_slot_out)

    def get_min_slot(self):
        if len(self.garbage_map) == len(self.servers):
            return min(self.garbage_map.values())
        return 0
