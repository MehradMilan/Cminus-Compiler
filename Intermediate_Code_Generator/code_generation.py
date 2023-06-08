from .runtime_memory import Memory, ProgramBlock, Instruction
from .semantic_stack import SemanticStack


class CodeGenerator:
    def __init__(self) -> None:
        memory = Memory(0, 500, 1000)
        self.memory = memory
        self.semantic_stack = SemanticStack()
        self.program_block = memory.PB
        self.data_block = memory.DB
        self.temp_block = memory.TB
        self.symbol_table = {}

    def save_in_semantic_stack(self, current_token):
        self.semantic_stack.push(current_token[1])

    def declare_variable(self, current_token):
        name = self.semantic_stack.pop()
        self.data_block.create_data(name, 'int', self.symbol_table)

    def declare_array(self, current_token):
        array_size = self.semantic_stack.pop()
        name = self.semantic_stack.pop()
        self.data_block.create_data(name, 'int', self.symbol_table, int(array_size))

    def find_address_and_save(self, current_token):
        name = current_token[1]
        address = self.symbol_table[name]
        self.semantic_stack.push(address)

    def multiply(self, current_token):
        temp = self.temp_block.get_temp()
        instruction = Instruction('MULT', self.semantic_stack.pop(), self.semantic_stack.pop(), temp)
        self.semantic_stack.push(temp)
        self.program_block.add_instruction(instruction)
        print(str(instruction))

    def add(self, current_token):
        name = current_token[1]
        address = self.symbol_table[name]
        self.semantic_stack.push(address)

