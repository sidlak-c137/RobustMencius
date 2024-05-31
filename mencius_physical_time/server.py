import time
import numpy as np
from .utils import Node
from .kvstore import AMOKVStore
from .messages import ProposeRequest, Response, ProposeReply, Heartbeat, Ping
from .timers import HeartbeatCheckTimer, HeartbeatTimer, ProposeTimer
import threading


class Server(Node):
    def __init__(self, name: str, config: dict = {}, logger=None, servers=[]):
        super().__init__(name, config, logger)
        self.servers = servers
        self.servers_minus_self = [server for server in servers if server != name]
        self.N = len(servers)
        self.M = 1000
        self.functions = {
            "Request": self.handle_request,
            "ProposeRequest": self.handle_propose_request,
            "ProposeReply": self.handle_propose_reply,
            "Heartbeat": self.handle_heartbeat,
            "Ping": self.handle_ping,
        }
        self.timers = {
            "HeartbeatTimer": self.handle_heartbeat_timer,
            "ProposeTimer": self.handle_propose_timer,
        }

        self.tilings = {0: [0, 1, 2]}
        self.tiling_lens = {k: len(self.tilings[k]) for k in self.tilings}
        self.log = {}

        self.application = AMOKVStore()
        self.lock = threading.RLock()
        self.slot_out = 0
        self.slot_in = self.servers.index(name)
        self.local_garbage = 0
        self.garbage_map = {}
        self.proposal_replies = {}
        self.heartbeat_timer = {k: None for k in self.servers}

    def start_node(self):
        super().start_node()
        self.start_timer(ProposeTimer({}))

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

    def handle_propose_reply(
        self, slot: int, slot_out: int, skip_till: int, sender: str
    ):
        with self.lock:
            while skip_till >= self.slot_out:
                skip_till = self.get_prev_slot(sender, skip_till)
                if skip_till not in self.log and skip_till >= self.slot_out:
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

    def handle_ping(self, sender: str, tilings: dict, heartbeat_timer: dict):
        with self.lock:
            if len(tilings) > len(self.tilings):
                self.tilings = tilings
                self.tiling_lens = {k: len(self.tilings[k]) for k in self.tilings}
            if self.servers.index(self.name) == 0 and self.slot_in > max(self.tilings.keys()) + self.M // 2:
                probs = [0] * self.N
                for i in range(self.N):
                    if self.heartbeat_timer[self.servers[i]] is not None:
                        probs[i] = self.heartbeat_timer[self.servers[i]][2] / self.heartbeat_timer[self.servers[i]][1]
                    else:
                        probs[i] = heartbeat_timer[self.servers[i]][2] / heartbeat_timer[self.servers[i]][1]
                probs = [1 / p for p in probs]
                probs = [p / sum(probs) for p in probs]
                self.logger.info(f"probs: {probs}")
                self.tilings[max(self.tilings.keys()) + self.M] = self.generate_random_list_with_probabilities([i for i in range(self.N)], probs, 100)
                self.tiling_lens = {k: len(self.tilings[k]) for k in self.tilings}

            if self.heartbeat_timer[sender] is None:
                self.heartbeat_timer[sender] = (time.time(), 0, 0)
            else:
                t = time.time()
                self.heartbeat_timer[sender] = (
                    t,
                    self.heartbeat_timer[sender][1] + 1,
                    self.heartbeat_timer[sender][2]
                    + t
                    - self.heartbeat_timer[sender][0],
                )

    def handle_propose_timer(self):
        with self.lock:
            self.send_all_proposes()
            self.broadcast_message(Ping({"sender": self.name, "tilings": self.tilings, "heartbeat_timer": self.heartbeat_timer}), self.servers_minus_self)
            self.start_timer(ProposeTimer({}))
            self.logger.info(f"tilings: {self.tilings}")

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
        curr_tiling = max(i // self.M * self.M, 0)
        idx = self.servers.index(server)
        mod = i % self.tiling_lens[curr_tiling]
        i -= 1
        curr_tiling = max(i // self.M * self.M, 0)
        while (i % self.tiling_lens[curr_tiling]) != mod and self.tilings[curr_tiling][(i %self.M) % self.tiling_lens[curr_tiling]] != idx:
            i -= 1
            curr_tiling = max(i // self.M * self.M, 0)
        return i

    def get_next_slot(self, server, i):
        curr_tiling = max(i // self.M * self.M, 0)
        idx = self.servers.index(server)
        mod = i % self.tiling_lens[curr_tiling]
        i += 1
        curr_tiling = max(i // self.M * self.M, 0)
        while (i % self.tiling_lens[curr_tiling]) != mod and self.tilings[curr_tiling][(i % self.M) % self.tiling_lens[curr_tiling]] != idx:
            i += 1
            curr_tiling = max(i // self.M * self.M, 0)
        return i

    def is_leader(self, server, i):
        curr_tiling = max(i // self.M * self.M, 0)
        return self.tilings[curr_tiling][(i % self.M) % self.tiling_lens[curr_tiling]] == self.servers.index(server)

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
    
    def generate_random_list_with_probabilities(self, numbers, probabilities, total_length):
        if len(numbers) != len(probabilities):
            raise ValueError("Numbers and probabilities must have the same length.")
        if not np.isclose(sum(probabilities), 1.0):
            raise ValueError("Probabilities must sum to 1.")
        
        probabilities = np.array(probabilities)
        expected_counts = probabilities * total_length
        integer_counts = np.floor(expected_counts).astype(int)
        result = self.generate(integer_counts.tolist())

        return result

    def generate(self, item_counts):
        '''item_counts is a list of counts of "types" of items. E.g., [3, 1, 0, 2] represents
            a list containing [1, 1, 1, 2, 4, 4] (3 types of items/distinct values). Generate
            a new list with evenly spaced values.'''
        # Sort number of occurrences by decreasing value.
        item_counts.sort(reverse=True)
        # Count the total elements in the final list.
        unplaced = sum(item_counts)
        # Create the final list.
        placements = [None] * unplaced

        # For each type of item, place it into the list item_count times.
        for item_type, item_count in enumerate(item_counts):
            # The number of times the item has already been placed
            instance = 0
            # Evenly divide the item amongst the remaining unused spaces, starting with
            # the first unused space encountered.
            # blank_count is the number of unused spaces seen so far and is reset for each
            # item type.
            blank_count = -1
            for position in range(len(placements)):
                if placements[position] is None:
                    blank_count += 1
                    # Use an anti-aliasing technique to prevent bunching of values.
                    if blank_count * item_count // unplaced == instance:
                        placements[position] = item_type
                        instance += 1
            # Update the count of number of unplaced items.
            unplaced -= item_count

        return placements
