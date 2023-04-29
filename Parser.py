import grammar

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

    def __init__(self, grammar) -> None:
        self.grammar = grammar
        alphabet = Alphabet(self.grammar.rules, self.grammar.first_sets, self.grammar.follow_sets, self.grammar.predict_sets)
        alphabet.extract_lexims_from_rules()
        self.alphabet = alphabet

parser = Parser(grammar)