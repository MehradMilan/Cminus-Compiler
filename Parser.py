from anytree import Node, RenderTree

err = ''
class Lexim:

    def __init__(self, name, is_terminal) -> None:
        self.name = name
        self.is_terminal = is_terminal


class Alphabet:

    def __init__(self, rules, first_sets, follow_sets, predict_sets) -> None:
        self.lexims = {}
        self.rules = rules
        self.first_sets = first_sets
        self.follow_sets = follow_sets
        self.predict_sets = predict_sets

    def add_lexim(self, lexim):
        self.lexims[lexim.name] = lexim

    def extract_lexims_from_rules(self):
        rules = self.rules
        for rule in rules:
            left = rule['left']
            lexim = Lexim(left, False)
            self.add_lexim(lexim)
            for right in rule['right']:
                if right not in self.lexims:
                    lexim = Lexim(right, True)
                    self.add_lexim(lexim)


class Parser:
    def first_of(self, lexim):
        if self.alphabet.lexims[lexim].is_terminal:
            return [lexim]
        return self.grammar.first_sets[lexim]

    def follow_of(self, lexim):
        if self.alphabet.lexims[lexim].is_terminal:
            return []
        return self.grammar.follow_sets[lexim]

    def current_token_value(self):
        return self.current_token[0] if self.current_token[0] in ['ID', 'NUM'] else self.current_token[1]

    def __init__(self, grammar, first_token) -> None:
        self.parse_tree = {0: 'Program'}
        self.grammar = grammar
        alphabet = Alphabet(self.grammar.rules, self.grammar.first_sets, self.grammar.follow_sets,
                            self.grammar.predict_sets)
        alphabet.extract_lexims_from_rules()
        self.alphabet = alphabet
        self.current_token = first_token


    def parse(self, non_terminal, token_scanner_generator, scanner, parent=None, first = False):
        global err
        no_error = True
        for lhs in self.grammar.rule_dict[non_terminal]:
            if self.current_token_value() in self.first_of(lhs[0]) or \
                    'epsilon' in self.first_of(lhs[0]) and self.current_token_value() in self.follow_of(lhs[0]):
                for lexim in lhs:
                    if self.alphabet.lexims[lexim].is_terminal:
                        if lexim == self.current_token_value():
                            Node('(' + self.current_token[0] + ', ' + self.current_token[1] + ')'
                                 , parent=parent)
                            self.current_token = next(token_scanner_generator)
                        else:
                            err += '#' + scanner.get_line_number() + ' : syntax error, missing ' + lexim + '\n'
                            no_error = False
                    else:
                        while not (self.current_token_value() in self.first_of(lexim) \
                                   or \
                                   'epsilon' in self.first_of(
                                    lexim) and self.current_token_value() in self.follow_of(lexim)):
                            if self.current_token_value() in self.follow_of(lexim):
                                err += '#' + scanner.get_line_number() + ' : syntax error, missing ' + lexim + '\n'
                                no_error = False
                                break
                            else:
                                if self.current_token[0] == 'EOF':
                                    err += '#' + scanner.get_line_number() + ' : syntax error, Unexpected EOF' + '\n'
                                    return -1
                                else:
                                    err += '#' + scanner.get_line_number() + ' : syntax error, illegal ' + self.current_token_value() + '\n'
                                    no_error = False
                                    self.current_token = next(token_scanner_generator)
                        else:
                            res = self.parse(lexim, token_scanner_generator, scanner, Node(lexim, parent=parent))
                            if res == -1:
                                if first:
                                    with open('syntax_errors.txt', 'w') as syntax_errors_file:
                                        syntax_errors_file.write(err)
                                return -1

                break
            elif 'epsilon' == lhs[0] and self.current_token_value() in self.follow_of(non_terminal):
                Node('epsilon', parent=parent)
                break

        if first:
            if err == '':
                err += 'There is no syntax error.' + '\n'
            with open('syntax_errors.txt', 'w') as syntax_errors_file:
                syntax_errors_file.write(err)
