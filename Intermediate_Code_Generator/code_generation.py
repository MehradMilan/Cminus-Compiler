from .runtime_memory import *
from .semantic_stack import SemanticStack


class CodeGenerator:
    def __init__(self, parser) -> None:
        memory = Memory(0, 500, 1000)
        self.parser = parser
        self.semantic_errors = {}
        self.memory = memory
        self.semantic_stack = SemanticStack()
        self.program_block = memory.PB
        self.data_block = memory.DB
        self.temp_block = memory.TB
        self.global_symbol_table = {}
        self.current_symbol_table = self.global_symbol_table
        self.symbol_table_stack = []

    def do_types_match(self, first_operand, second_operand):
        first_type = 'int'
        second_type = 'int'
        try:
            address = int(first_operand)
            first_type = self.memory.DB.block[address].type
        except:
            first_type = 'int'
        try:
            address = int(second_operand)
            second_type = self.memory.DB.block[address].type
        except:
            second_type = 'int'
        return first_type, second_type, first_type == second_type

    def save_token_in_semantic_stack(self, current_token):
        self.semantic_stack.push(current_token[1])

    def save_number_in_semantic_stack(self, current_token):
        self.semantic_stack.push('#' + current_token[1])

    def declare_variable(self, current_token):
        name = self.semantic_stack.pop()
        data_type = self.semantic_stack.pop()
        if data_type == 'void':
            self.semantic_errors[int(self.parser.scanner.get_line_number()) - 1] = \
                "Semantic Error! Illegal type of void for '" + name + "'"
            self.memory.PB.has_error = True
        else:
            self.data_block.create_data(name, 'int', self.current_symbol_table)

    def declare_array(self, current_token):
        array_size = self.semantic_stack.pop()
        name = self.semantic_stack.pop()
        self.data_block.create_data(name, 'array', self.current_symbol_table, int(array_size))

    def get_data_by_name(self, name):
        if name in self.current_symbol_table:
            return self.current_symbol_table[name]
        elif name in self.global_symbol_table:
            return self.global_symbol_table[name]
        else: raise Exception("name not found!")

    def find_address_and_save(self, current_token):
        name = current_token[1]
        if name == 'output':
            self.semantic_stack.push('PRINT')
            return
        
        try:
            address = self.get_data_by_name(name).address
            # address = self.current_symbol_table[name].address
            self.semantic_stack.push(address)
        except:
            self.semantic_errors[int(self.parser.scanner.get_line_number())] = \
                "Semantic Error! '" + name + "' is not defined."
            self.memory.PB.has_error = True
            print(self.semantic_errors)

    def multiply(self, current_token):
        temp = self.temp_block.get_temp()
        second = self.semantic_stack.pop()
        first = self.semantic_stack.pop()
        first_type, second_type, match = self.do_types_match(first, second)
        if match:
            instruction = Instruction('MULT', first, second, temp)
            self.semantic_stack.push(temp)
            self.program_block.add_instruction(instruction)
        else:
            self.semantic_errors[int(self.parser.scanner.get_line_number())] = \
                f"Semantic Error! Type mismatch in operands, Got {second_type} instead of {first_type}."
            self.memory.PB.has_error = True
            print(self.semantic_errors)
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
        first_type, second_type, match = self.do_types_match(first_operand, second_operand)
        if match:
            instruction = Instruction(op, first_operand, second_operand, temp)
            self.semantic_stack.push(temp)
            self.program_block.add_instruction(instruction)
        else:
            self.semantic_errors[int(self.parser.scanner.get_line_number())] = \
                f"Semantic Error! Type mismatch in operands, Got {second_type} instead of {first_type}."
            self.memory.PB.has_error = True
            print(self.semantic_errors)

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

    # def add(self, current_token):
    #     name = current_token[1]
    #     address = self.current_symbol_table[name]
    #     self.semantic_stack.push(address)

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
        if self.memory.PB.scope > 0:
            self.program_block.add_instruction(('break', self.memory.PB.scope))
        else:
            self.semantic_errors[int(self.parser.scanner.get_line_number()) - 1] = \
                "Semantic Error! No 'repeat ... until' found for 'break'."
            self.memory.PB.has_error = True
            print(self.semantic_errors)
