class AMOKVStore:
    def __init__(self):
        self.kvstore = KVStore()
        self.clientMap = {}

    def alreadyExecuted(self, AMOCommand):
        assert (
            "client" in AMOCommand
            and "seqNum" in AMOCommand
            and "command" in AMOCommand
        )
        if AMOCommand["client"] in self.clientMap:
            if AMOCommand["seqNum"] <= self.clientMap[AMOCommand["client"]]["seqNum"]:
                return True

    def execute(self, AMOCommand):
        if self.alreadyExecuted(AMOCommand):
            return self.clientMap[AMOCommand["client"]]["response"]
        else:
            match AMOCommand["command"]["type"]:
                case "GET":
                    assert "key" in AMOCommand["command"]
                    response = self.kvstore.get(AMOCommand["command"]["key"])
                case "PUT":
                    assert "key" in AMOCommand["command"]
                    response = self.kvstore.put(
                        AMOCommand["command"]["key"], AMOCommand["command"]["value"]
                    )
                case "APPEND":
                    assert (
                        "key" in AMOCommand["command"]
                        and "value" in AMOCommand["command"]
                    )
                    response = self.kvstore.append(
                        AMOCommand["command"]["key"], AMOCommand["command"]["value"]
                    )
                case "DELETE":
                    assert "key" in AMOCommand["command"]
                    response = self.kvstore.delete(AMOCommand["command"]["key"])
                case _:
                    raise ValueError("Invalid command")
            self.clientMap[AMOCommand["client"]] = {
                "seqNum": AMOCommand["seqNum"],
                "response": response,
            }
            return response


class KVStore:
    def __init__(self):
        self.store = {}

    def get(self, key):
        return self.store.get(key)

    def put(self, key, value):
        self.store[key] = value
        return self.store[key]

    def append(self, key, value):
        self.store[key] += value
        return self.store[key]

    def delete(self, key):
        if key in self.store:
            del self.store[key]
        return None
