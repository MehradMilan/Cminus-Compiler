from anytree import RenderTree, Node

from FiniteAutomata import FiniteAutomata, CharacterRecognizer
import grammar
from Parser import Parser

num_fa_str = open('FAs/NUM.py').read()
symbol_fa_str = open('FAs/SYMBOL.py').read()
whitespace_fa_str = open('FAs/WHITESPACE.py').read()
id_fa_str = open('FAs/ID.py').read()
comment_fa_str = open('FAs/COMMENT.py').read()


def simulate(fa, input_string):
    global line_number
    number_of_lines = 0
    current_recognized_string = ''
    for i in range(len(input_string)):
        ch = input_string[i]
        if ch == '\n':
            number_of_lines += 1
        res = fa.consume_character(ch)
        if not res:
            return False, False, '', 0
        current_recognized_string += ch
        if fa.is_at_final_state():
            line_number += number_of_lines
            return True, True, current_recognized_string, i
        elif fa.is_at_final_state_with_star():
            line_number += number_of_lines
            if len(current_recognized_string) > 0 and current_recognized_string[-1] == '\n':
                line_number -= 1
            return True, True, current_recognized_string[:-1], i - 1
    return True, False, current_recognized_string, i


index = 0

error = ''
error_started_at = 0
identified_comment_or_ws = False

fas = {'COMMENT': FiniteAutomata(comment_fa_str),
       'NUM': FiniteAutomata(num_fa_str),
       'SYMBOL': FiniteAutomata(symbol_fa_str),
       'WHITESPACE': FiniteAutomata(whitespace_fa_str),
       'ID': FiniteAutomata(id_fa_str)
       }

inp = open('./input.txt').read() + chr(0)

line_number = 1
tokens = {}
lexical_errors = {}
symbol_table = ['break', 'else', 'if', 'int', 'repeat', 'return', 'until', 'void']


def scanner():
    global index, error, error_started_at, identified_comment_or_ws, fas, inp, line_number, tokens, lexical_errors, symbol_table
    while index != len(inp):
        for fa_name in fas:
            commnet_started_at = 0
            if fa_name == 'COMMENT':
                commnet_started_at = line_number
            fa = fas[fa_name]
            simulates_successfully, ends_in_final_state, string, offset = simulate(fa, inp[index:])
            fa.reset()
            if simulates_successfully and not ends_in_final_state and fa_name == 'COMMENT':
                if len(string) > 7:
                    res = (string[:7] + '...', 'Unclosed comment')
                    lexical_errors[commnet_started_at] = lexical_errors[commnet_started_at] + [
                        res] if line_number in lexical_errors else [res]
                else:
                    res = (string, 'Unclosed comment')
                    lexical_errors[error_started_at] = lexical_errors[error_started_at] + [
                        res] if line_number in lexical_errors else [res]
                index += offset
                break
            if ends_in_final_state:
                index += offset + 1
                if error != '':
                    if error == '*/':
                        res = (error, 'Unmatched comment')
                        lexical_errors[error_started_at] = lexical_errors[error_started_at] + [
                            res] if line_number in lexical_errors else [res]
                    else:
                        res = (error, 'Invalid input')
                        lexical_errors[error_started_at] = lexical_errors[error_started_at] + [
                            res] if line_number in lexical_errors else [res]
                    error = ''
                if fa_name != 'WHITESPACE' and fa_name != 'COMMENT':
                    if fa_name == 'ID':
                        if string in ['if', 'else', 'void', 'int', 'repeat', 'break', 'until', 'return']:
                            res = ('KEYWORD', string)
                            tokens[line_number] = tokens[line_number] + [res] if line_number in tokens else [res]
                            yield res
                            break
                        if line_number in tokens and len(tokens[line_number]) > 0 and \
                                not identified_comment_or_ws and \
                                tokens[line_number][-1][0] == 'NUM':
                            identified_comment_or_ws = False
                            last = tokens[line_number].pop()
                            res = (last[1] + string[0], 'Invalid number')
                            lexical_errors[line_number] = lexical_errors[line_number] + [
                                res] if line_number in lexical_errors else [res]
                            if len(string) > 1:
                                res = (fa_name, string[1:])
                                tokens[line_number] = tokens[line_number] + [res] if line_number in tokens else [res]
                                if string[1:] not in symbol_table:
                                    symbol_table.append(string[1:])
                                yield res
                            break
                    res = (fa_name, string)
                    tokens[line_number] = tokens[line_number] + [res] if line_number in tokens else [res]
                    yield res
                    if fa_name == 'ID':
                        if string not in symbol_table:
                            symbol_table.append(string)
                    identified_comment_or_ws = False
                else:
                    identified_comment_or_ws = True
                break
        else:
            if not ends_in_final_state:
                if error == '':
                    error_started_at = line_number
                error += inp[index]
                if error == '/' and index + 1 < len(inp) and inp[index + 1] == '/':
                    res = (error, 'Invalid input')
                    lexical_errors[error_started_at] = lexical_errors[error_started_at] + [
                        res] if line_number in lexical_errors else [res]
                    error = ''
                if len(error) >= 1 and inp[index] not in CharacterRecognizer.STARTERS:
                    if error == '*/':
                        res = (error, 'Unmatched comment')
                        lexical_errors[error_started_at] = lexical_errors[error_started_at] + [
                            res] if line_number in lexical_errors else [res]
                    else:
                        res = (error, 'Invalid input')
                        lexical_errors[error_started_at] = lexical_errors[error_started_at] + [
                            res] if line_number in lexical_errors else [res]
                        error = ''
                if inp[index] == '\n':
                    line_number += 1
                index += 1
    yield ('EOF', '$')


# scanner()
# with open('tokens.txt', 'w') as f:
#     for i in tokens:
#         line = str(i) + '.\t'
#         for x in tokens[i]:
#             line += '(' + x[0] + ', ' + x[1] + ') '
#         f.write(line + '\n')
#
# with open('lexical_errors.txt', 'w') as f:
#     if lexical_errors:
#         for i in lexical_errors:
#             line = str(i) + '.\t'
#             for x in lexical_errors[i]:
#                 line += '(' + x[0] + ', ' + x[1] + ') '
#             f.write(line + '\n')
#     else:
#         f.write('There is no lexical error.')
#
# with open('symbol_table.txt', 'w') as f:
#     for i in range(len(symbol_table)):
#         line = str(i + 1) + '.\t' + symbol_table[i]
#         f.write(line + '\n')

token_scanner = scanner()
parser = Parser(grammar, next(token_scanner))
root = Node('Program')
parser.parse('Program', token_scanner, 1, root)
Node('$', parent=root)
with open('parse_tree.txt', 'w') as f:
    for pre, fill, node in RenderTree(root):
        f.write("%s%s" % (pre, node.name) + '\n')
