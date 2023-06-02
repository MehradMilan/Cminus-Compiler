class SS:

    def __init__(self) -> None:
        self.stack = list()
        self.sp = 0

    def push(self, addr):
        self.stack.append(addr)
        self.sp += 1

    def pop(self):
        self.sp -= 1
        return self.stack.pop()
    
    def top(self, offset=0):
        return self.stack[self.sp - offset]
