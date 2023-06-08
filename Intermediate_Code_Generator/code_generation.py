import runtime_memory

class Code_Generator:
    def __init__(self) -> None:
        memory = runtime_memory.Memory(0, 500, 1000)
        pb = memory.PB
        db = memory.DB
        tb = memory.TB