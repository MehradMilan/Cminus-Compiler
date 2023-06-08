INT_SIZE = 4

class Memory:
    def __init__(self, pb_index, db_index, tb_index) -> None:
        self.PB = Program_Block(pb_index, db_index - 1)

class Program_Block:
    def __init__(self, base, bound) -> None:
        self.base = base
        self.bound = bound
        self.current_index = base
        self.block = {}

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
    
class Temporary_Block:
    def __init__(self, base, bound) -> None:
        self.base = base
        self.bound = bound
        self.current_index = base
        self.block = {}

    def get_temp(self):
        self.current_index += 1
        # TODO
  
class Data:
    def __init__(self, lexeme, type, address):
        self.lexeme = lexeme
        self.address = address
        self.type = type
        if type == 'int':
            self.type_size = INT_SIZE
        
class Data_Block:
    def __init__(self, base, bound) -> None:
        self.base = base
        self.bound = bound
        self.current_index = base
        self.block = {}

    # def init_data_block(self): TODO

    def create_data(self, lexeme, type):
        data = Data(lexeme, type, self.current_index)
        self.block[self.current_index] = data
        self.increase_index(data.type_size)
        return data

    def increase_index(self, size):
        self.current_index += size