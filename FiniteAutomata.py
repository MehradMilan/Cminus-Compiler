class CharacterRecognizer:
    ALL_ALPHABET = [x for x in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz']
    LOWERCASE_ALPHABET = [x for x in 'abcdefghijklmnopqrstuvwxyz']
    UPPERCASE_ALPHABET = [x for x in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ']
    WHITESPACE = [x for x in '\r\n\t\f\v  ']
    DIGITS = [x for x in '0123456789']
    SYMBOL = [x for x in '(){}[]+-*=/,:;<']
    STARTERS = ALL_ALPHABET + WHITESPACE + DIGITS + [x for x in '(){}/[]+-*=,:;\x00']
    SIGMA = ALL_ALPHABET + DIGITS + SYMBOL + WHITESPACE + ['\x00']

    def __init__(self, string):
        self.ignore = string[0] == '~'
        self.isInverted = string[0] == '^' or string[0] == '~'
        string = string[1:] if self.isInverted else string
        if string == 'alpha':
            self.chars = self.LOWERCASE_ALPHABET
        elif string == 'ALPHA':
            self.chars = self.UPPERCASE_ALPHABET
        elif string == 'Alpha':
            self.chars = self.ALL_ALPHABET
        elif string == 'Digit':
            self.chars = self.DIGITS
        elif string == 'AlphaDigit':
            self.chars = self.ALL_ALPHABET + self.DIGITS
        elif string == 'Whitespace':
            self.chars = self.WHITESPACE
        else:
            self.chars = [x for x in string]

    def match(self, character):
        return character in self.chars if not self.isInverted else character not in self.chars and \
                                                                   (character in self.SIGMA or self.ignore)


class FiniteAutomata:
    def __init__(self, text_representation):
        self.final_states = []
        self.final_states_with_star = []
        self.current_state = 0

        def process_line(fa_line: str):
            search_result = fa_line.split()
            orig = int(search_result[0])
            trans = search_result[2]
            destination_string = search_result[4]
            is_destination_goal = False
            has_extra_char = False
            if destination_string[-1] == 'g':
                dest = int(destination_string[:-1])
                is_destination_goal = True
            elif destination_string[-1] == 'G':
                dest = int(destination_string[:-1])
                has_extra_char = True
            else:
                dest = int(destination_string)
            return orig, trans, dest, is_destination_goal, has_extra_char

        repr_lines = text_representation.split('\n')
        number_of_states = int(repr_lines.pop(0))
        self.graph = {i: [] for i in range(number_of_states)}
        for line in repr_lines:
            if line == 'end':
                return
            origin, transition, destination, is_goal, has_extra = process_line(line)
            if not (0 <= origin < number_of_states and 0 <= destination < number_of_states):
                raise Exception('Origin Or Destination Number Is Wrong At Line \"' + line + '\"')
            transition_pattern = CharacterRecognizer(transition)
            if is_goal:
                self.final_states.append(destination)
            elif has_extra:
                self.final_states_with_star.append(destination)
            if origin in self.graph.keys():
                self.graph[origin].append((destination, transition_pattern))
            else:
                self.graph[origin] = [(destination, transition_pattern)]

    def get_current_node_adj(self):
        return self.graph[self.current_state]

    def consume_character(self, character):
        adj_list = self.get_current_node_adj()
        for destination, transition in adj_list:
            if transition.match(character):
                self.current_state = destination
                return True
        self.current_state = 0
        return False

    def is_at_final_state(self):
        return self.current_state in self.final_states

    def is_at_final_state_with_star(self):
        return self.current_state in self.final_states_with_star

    def reset(self):
        self.current_state = 0
