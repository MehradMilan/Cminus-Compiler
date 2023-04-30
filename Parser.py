from anytree import Node, RenderTree


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

    def parse(self, non_terminal, token_scanner, level, parent=None):
        for lhs in self.grammar.rule_dict[non_terminal]:
            if self.current_token_value() in self.first_of(lhs[0]) or \
                    'epsilon' in self.first_of(lhs[0]) and self.current_token_value() in self.follow_of(lhs[0]):
                for lexim in lhs:
                    if self.alphabet.lexims[lexim].is_terminal:
                        if lexim == self.current_token_value():
                            Node('(' + self.current_token[0] + ', ' + self.current_token[1] + ')'
                                 , parent=parent)
                            self.current_token = next(token_scanner)
                    else:
                        self.parse(lexim, token_scanner, level + 1, Node(lexim, parent=parent))
                break
            elif 'epsilon' == lhs[0] and self.current_token_value() in self.follow_of(non_terminal):
                Node('epsilon', parent=parent)
