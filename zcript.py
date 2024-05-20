import os
import re
import sys

def tokenize_source_code(source_code):
    keywords = {
        "var": "identifier",
        "print": "identifier",
    }
    token_types = [
        "identifier",
        "integer",
        "float",
        "string",
        "lparen",
        "rparen",
        "end_statement",
        "operator",
    ]

    unedited_source_code=source_code
    source_code = source_code.split()
    cur_char = 0
    Tokens = []

    while cur_char < len(source_code):
        code = source_code[cur_char]

        if ':' in code and code != ':':
            parts = code.split(':')
            source_code[cur_char] = parts[0]
            source_code.insert(cur_char + 1, ':')
            if len(parts) > 1 and parts[1] != '':
                source_code.insert(cur_char + 2, parts[1])

        if source_code[cur_char] in keywords:
            Tokens.append(f'{source_code[cur_char]}|{keywords[source_code[cur_char]]}')
        elif re.match('[a-zA-Z]', source_code[cur_char]) and source_code[cur_char] not in keywords:
            Tokens.append(f'{source_code[cur_char]}|identifier')
        elif (source_code[cur_char].startswith("'") and not source_code[cur_char].endswith("'")) or \
             (source_code[cur_char].startswith('"') and not source_code[cur_char].endswith('"')):
            string_token = source_code[cur_char]
            cur_char += 1
            while cur_char < len(source_code):
                code = source_code[cur_char]
                string_token += f' {code}'
                if (code.endswith("'") and string_token.startswith("'")) or \
                   (code.endswith('"') and string_token.startswith('"')):
                    break
                cur_char += 1
            if ':' in string_token:
                parts = string_token.split(':')
                string_token = parts[0]
                Tokens.append(f'{string_token}|string')
                Tokens.append(f':|end_statement')
                if len(parts) > 1 and parts[1] != '':
                    Tokens.append(f'{parts[1]}|string')
            else:
                Tokens.append(f'{string_token}|string')
        elif len(source_code[cur_char]) >= 2 and ((source_code[cur_char][0] == "'" and source_code[cur_char][-1] == "'") or \
             (source_code[cur_char][0] == '"' and source_code[cur_char][-1] == '"')):
            Tokens.append(f'{source_code[cur_char]}|string')
        elif source_code[cur_char] in '=+-*/':
            Tokens.append(f'{source_code[cur_char]}|operator')
        elif source_code[cur_char] == ';':
            Tokens.append(f'{source_code[cur_char]}|end_statement')
        elif source_code[cur_char] == ':':
            Tokens.append(f'{source_code[cur_char]}|end_statement')
        elif source_code[cur_char] == '(':
            Tokens.append(f'{source_code[cur_char]}|lparen')
        elif source_code[cur_char] == ')':
            Tokens.append(f'{source_code[cur_char]}|rparen')
        elif re.match('[0-9]', source_code[cur_char]):
            Tokens.append(f'{source_code[cur_char]}|integer')
        cur_char += 1
        #print(Tokens)
    compiler(Tokens, unedited_source_code)
    return Tokens

def parse_source_code():
    pass

def compiler(Tokens, source_code):
    try:
        if "var" in Tokens[0]:
            if 'identifier' in Tokens[1]:
                variable_name = Tokens[1].split("|")
                variable_name = variable_name[0]
                if 'operator' in Tokens[2]:
                    variable_operator = Tokens[2].split("|")
                    variable_operator = variable_operator[0]
                    if 'string' in Tokens[3] or 'integer' in Tokens[3]:
                        variable_value = Tokens[3].split("|")
                        variable_value = variable_value[0]
                        if 'end_statement' in Tokens[4]:
                            with open("compiled.py", "a") as file:
                                file.write(f"{variable_name} {variable_operator} {variable_value}\n")
                    else:
                        print("Error: Invalid Value '" + Tokens[3] + "'")
                else:
                    print("Error: Invalid Variable Operator '" + Tokens[3] + "'")
            else:
                print("Error: Invalid Variable name '" + Tokens[1] + "'")

        elif "print" in Tokens[0]:
            if 'string' in Tokens[1] or 'identifier' in Tokens[1] or 'integer' in Tokens[1]:
                print_value = Tokens[1].split("|")
                print_value = print_value[0]
                if 'end_statement' in Tokens[2]:
                    with open("compiled.py", "a") as file:
                        file.write(f"print({print_value})\n")
                else:
                    print("Error: Invalid Syntax. No ':'?")
            else:
                print("Error: Invalid Value '" + Tokens[1] + "'")
        else:
            raise Exception
    except IndexError:
        with open("compiled.py", "a") as file:
            file.write(" \n")
    except Exception:
        print(f"Error: Invalid Syntax '" + str(source_code) + "'")
        os.remove("compiled.py")
        quit()

def interpreter(file):
    print("Interpreter")

if __name__ == '__main__':
    arg1 = sys.argv[1]
    try:
        arg2 = sys.argv[2]
    except IndexError:
        arg2=None
    if arg2 == "compiler":
        with open("compiled.py", "w") as file:
            file.write("")
        token_list = []
        with open(arg1, "r") as file:
            content = file.readlines()
        for cont in content:
            # print(cont)
            tokens = tokenize_source_code(cont)
            token_list.append(tokens)
        print(f"{arg1} successfully compiled as compiled.py")
    elif arg2 == "interpreter":
        interpreter(arg1)
    else:
        interpreter(arg1)