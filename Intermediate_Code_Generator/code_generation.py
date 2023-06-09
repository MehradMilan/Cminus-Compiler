from .runtime_memory import *
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

    def save_token_in_semantic_stack(self, current_token):
        self.semantic_stack.push(current_token[1])

    def save_number_in_semantic_stack(self, current_token):
        self.semantic_stack.push('#' + current_token[1])

    def declare_variable(self, current_token):
        name = self.semantic_stack.pop()
        self.data_block.create_data(name, 'int', self.symbol_table)

    def declare_array(self, current_token):
        array_size = self.semantic_stack.pop()
        name = self.semantic_stack.pop()
        self.data_block.create_data(name, 'int', self.symbol_table, int(array_size))

    def find_address_and_save(self, current_token):
        name = current_token[1]
        if name == 'output':
            self.semantic_stack.push('PRINT')
            return
        address = self.symbol_table[name]
        self.semantic_stack.push(address)

    def multiply(self, current_token):
        temp = self.temp_block.get_temp()
        instruction = Instruction('MULT', self.semantic_stack.pop(), self.semantic_stack.pop(), temp)
        self.semantic_stack.push(temp)
        self.program_block.add_instruction(instruction)
        # print(str(instruction))

    def add_or_subtract(self, current_token):
        temp = self.temp_block.get_temp()
        second_operand = self.semantic_stack.pop()
        op = self.semantic_stack.pop()
        first_operand = self.semantic_stack.pop()
        if op == '+':
            op = 'ADD'
        elif op == '-':
            op = 'SUB'
        instruction = Instruction(op, first_operand, second_operand, temp)
        self.semantic_stack.push(temp)
        self.program_block.add_instruction(instruction)
        # print(str(instruction))

    def compare(self, current_token):
        temp = self.temp_block.get_temp()
        second_operand = self.semantic_stack.pop()
        op = self.semantic_stack.pop()
        first_operand = self.semantic_stack.pop()
        if op == '<':
            op = 'LT'
        elif op == '==':
            op = 'EQ'
        instruction = Instruction(op, first_operand, second_operand, temp)
        self.semantic_stack.push(temp)
        self.program_block.add_instruction(instruction)
        # print(str(instruction))

    def add(self, current_token):
        name = current_token[1]
        address = self.symbol_table[name]
        self.semantic_stack.push(address)

    def label(self, current_token):
        idx = self.program_block.current_index
        self.semantic_stack.push(idx)

    def repeat_until_iter(self, current_token):
        temp = self.semantic_stack.pop()

        while type(self.semantic_stack.top()) == str or self.semantic_stack.top() >= self.memory.DB.base:
            self.semantic_stack.pop()
        instr = Instruction('JPF', temp, self.semantic_stack.top(), '')
        self.program_block.add_instruction(instr)
        self.semantic_stack.pop()

        # handle break
        program_block = self.memory.PB
        for address in program_block.block:
            instruction = program_block.block[address]
            if type(instruction) == tuple and instruction[0] == 'break':
                if instruction[1] == program_block.scope + 1:
                    new_instr = Instruction('JP', self.program_block.current_index, '', '')
                    program_block.add_instruction(new_instr, address)

    def save_pb_index(self, current_token):
        idx = self.program_block.current_index
        self.semantic_stack.push(idx)
        self.program_block.increase_index()

    def jpf_save(self, current_token):
        idx = self.program_block.current_index
        while type(self.semantic_stack.top()) == str or self.semantic_stack.top() >= self.memory.DB.base:
            self.semantic_stack.pop()
        address = self.semantic_stack.pop()
        instr = Instruction('JPF', self.semantic_stack.top(), idx + 1, '')
        self.program_block.add_instruction(instr, address)
        self.semantic_stack.pop()
        self.semantic_stack.push(idx)
        self.program_block.increase_index()

    def jp(self, current_token):
        idx = self.program_block.current_index
        instr = Instruction('JP', idx, '', '')
        while type(self.semantic_stack.top()) == str or self.semantic_stack.top() >= self.memory.DB.base:
            self.semantic_stack.pop()
        self.program_block.add_instruction(instr, self.semantic_stack.top())
        self.semantic_stack.pop()

    def assign(self, current_token):
        instr = Instruction('ASSIGN', self.semantic_stack.pop(), self.semantic_stack.top(), '')
        # print(instr)
        self.program_block.add_instruction(instr)

    def print_instruction(self, current_token):
        if not self.semantic_stack.is_empty() and self.semantic_stack.top(1) == 'PRINT':
            operand = self.semantic_stack.pop()
            instr = Instruction(self.semantic_stack.pop(), operand, '', '')
            self.program_block.add_instruction(instr)
            # print(instr)

    def calculate_array_address(self, current_token):
        temp = self.temp_block.get_temp()
        temp2 = self.temp_block.get_temp()
        offset = self.semantic_stack.pop()
        base = self.semantic_stack.pop()
        mult_instruction = Instruction('MULT', '#4', offset, temp)
        self.program_block.add_instruction(mult_instruction)
        add_instruction = Instruction('ADD', '#' + str(base), temp, temp2)
        self.program_block.add_instruction(add_instruction)
        self.semantic_stack.push('@' + str(temp2))

    def end_scope(self, current_token):
        self.memory.PB.dec_scope()

    def begin_scope(self, current_token):
        self.memory.PB.inc_scope()

    def save_break(self, current_token):
        self.program_block.add_instruction(('break', self.memory.PB.scope))
