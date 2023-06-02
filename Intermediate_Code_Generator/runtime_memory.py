class Memory:
    def __init__(self, pb_index, db_index, tb_index) -> None:
        self.PB = Program_Block(pb_index, db_index - 1)

class Program_Block:
    def __init__(self, base, bound) -> None:
        self.base = base
        self.bound = bound
        self.length = bound - base + 1
        self.current_index = 0
        self.block = self.length * [None]

    def add_instruction(self, instr=None, index=None):
        if instr == None:
            self.current_index += 1
        else:
            if index == None:
                self.block[self.current_index] = instr
                self.current_index += 1
            else:
                self.block[index] = instr

    def get_output(self):
        output = ''
        for item in self.block:
            output += f'\n{str(item)}'

class Instruction:
    def __init__(self, opcode, op1, op2, op3):
        self.opcode = opcode
        self.op1 = op1
        self.op2 = op2
        self.op3 = op3
    
    def __str__(self) -> str:
        return f'({self.opcode}, {self.op1}, {self.op2}, {self.op3})'