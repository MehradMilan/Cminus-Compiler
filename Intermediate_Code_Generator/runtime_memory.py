import sys

INT_SIZE = 4
MAX_BLOCK = 1000


class Memory:
    def __init__(self, pb_index, db_index, tb_index) -> None:
        self.PB = ProgramBlock(pb_index, db_index - 1)
        self.DB = Data_Block(db_index, tb_index - 1)
        self.TB = Temporary_Block(tb_index, MAX_BLOCK - 1)


class ProgramBlock:
    def __init__(self, base, bound) -> None:
        self.has_error = False
        self.base = base
        self.bound = bound
        self.current_index = base + 1 #main call
        self.block = {}
        self.scope = 0

    def add_instruction(self, instr=None, index=None):
        if instr == None:
            self.current_index += 1
        else:
            if index == None:
                self.block[self.current_index] = instr
                self.increase_index()
            else:
                self.block[index] = instr

    def increase_index(self, count=1):
        self.current_index += count

    def inc_scope(self):
        self.scope += 1

    def dec_scope(self):
        self.scope -= 1

    def get_output(self):
        output = ''
        for item in self.block:
            output += f'\n{str(item)}'

    def get_dump(self, file_name):
        original_stdout = sys.stdout
        with open(file_name, 'w') as f:
            sys.stdout = f
            if not self.has_error:
                for address in sorted(list(self.block.keys())):
                    print(str(address) + '\t' + str(self.block[address]))
            else:
                print("The output code has not been generated.")
        sys.stdout = original_stdout


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
        idx = self.current_index
        self.current_index += INT_SIZE
        return idx


class Data:
    def __init__(self, lexeme, type, address):
        self.lexeme = lexeme
        self.address = address
        self.type = type
        self.attrs = {}
        if type == 'int' or type == 'array':
            self.type_size = INT_SIZE


class Data_Block:
    def __init__(self, base, bound) -> None:
        self.base = base
        self.bound = bound
        self.current_index = base
        self.block = {}

    # def init_data_block(self): TODO

    def create_data(self, lexeme, data_type, symbol_table, array_size=1):
        for i in range(array_size):
            data = Data(lexeme, data_type, self.current_index)
            if i == 0:
                symbol_table[lexeme] = data
            self.block[self.current_index] = data
            self.increase_index(data.type_size)

    def increase_index(self, data_size):
        self.current_index += data_size

class Activation_Record:

    def __init__(self, argument_values, symbol_table, access_link, return_addr) -> None:
        self.argument_values = argument_values
        self.symbol_table = symbol_table
        self.access_link = access_link
        self.return_addr = return_addr

    def add_arguments(self):
        pass

