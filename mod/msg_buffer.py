class MessageBuffer():
    def __init__(self, join_code="\n") -> None:
        self.buffer = []
        self.join_code = join_code

    def append(self, msg: str) -> None:
        self.buffer.append(msg)

    def __str__(self) -> str:

        joined_msgs = ""
        for m in self.buffer:
            joined_msgs += m + self.join_code

        return joined_msgs
