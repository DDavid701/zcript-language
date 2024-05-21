import os
import re
import sys

libraries_list =  {
    "standard":         "os, time, sys",
    "platform_tools":   "platform",
}


def tokenize_source_code(source_code):
    global keywords_list
    keywords = {
        "use":         "identifier",
        "var":         "identifier",
        "input":       "identifier",
        "print":       "identifier",
        "if":          "identifier",
        "else":        "identifier",
        "elseif":      "identifier",
        "end":         "identifier",
        "func":        "identifier",
        "wait":        "identifier",
    }
    keywords_list = [
                     "use",
                     "var",
                     "input",
                     "print",
                     "if",
                     "else",
                     "elseif",
                     "end",
                     "func",
                     "wait",
                     ]
    token_types = [
        "identifier",
        "integer",
        "float",
        "string",
        "list",
        "lparen",
        "rparen",
        "after_statement",
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
                Tokens.append(f':|after_statement')
                if len(parts) > 1 and parts[1] != '':
                    Tokens.append(f'{parts[1]}|string')
            else:
                Tokens.append(f'{string_token}|string')
        elif len(source_code[cur_char]) >= 2 and ((source_code[cur_char][0] == "'" and source_code[cur_char][-1] == "'") or \
             (source_code[cur_char][0] == '"' and source_code[cur_char][-1] == '"')):
            Tokens.append(f'{source_code[cur_char]}|string')
        elif len(source_code[cur_char]) >= 2 and ((source_code[cur_char][0] == "[" and source_code[cur_char][-1] == "]")):
            Tokens.append(f'{source_code[cur_char]}|list')
        elif source_code[cur_char] in '=+-*/':
            Tokens.append(f'{source_code[cur_char]}|operator')
        elif source_code[cur_char] == ';':
            Tokens.append(f'{source_code[cur_char]}|after_statement')
        elif source_code[cur_char] == ':':
            Tokens.append(f'{source_code[cur_char]}|after_statement')
        elif source_code[cur_char] == '(':
            Tokens.append(f'{source_code[cur_char]}|lparen')
        elif source_code[cur_char] == ')':
            Tokens.append(f'{source_code[cur_char]}|rparen')
        elif re.match('[0-9]', source_code[cur_char]):
            Tokens.append(f'{source_code[cur_char]}|integer')
        cur_char += 1
        print(Tokens)
    compiler(Tokens, unedited_source_code)
    return Tokens

def parse_source_code():
    pass

def compiler(Tokens, source_code):
    global Is_In_IF_statement
    global Is_In_FUNC
    global imported_standard
    try:
        key_ = Tokens[1].split("|")
        key_ = key_[0]
    except Exception:
        key_=None
    print(key_)
    print(Is_In_IF_statement, Is_In_FUNC)
    try:
        if "use" in Tokens[0]:
            library = Tokens[1].split("|")
            library = library[0]
            if library in libraries_list:
                if 'after_statement' in Tokens[2]:
                    with open("compiled.py", "a") as file:
                        file.write(f"import {libraries_list[library]}\n")
                        if library == "standard":
                            imported_standard = True
                        pass
                else:
                    print("Error: Invalid Syntax. No ':'?")
            else:
                print("Error: Library is does not exist or isn't supported in Zcript")

        elif key_ not in keywords_list and 'identifier' in Tokens[0]:
            print("HEEgr5tgtergtrege")
            func_name = Tokens[0].split("|")
            func_name = func_name[0]
            print(Tokens[1])
            if 'list' in Tokens[1]:
                print(Tokens[1])
                func_reqs = Tokens[1].split("|")
                func_reqs = func_reqs[0]
                print(func_reqs)
                func_reqs = func_reqs.replace("[", "")
                func_reqs = func_reqs.replace("]", "")
                if 'after_statement' in Tokens[2]:
                    with open("compiled.py", "a") as file:
                        file.write(f"{func_name}({func_reqs})\n")
                    pass
                else:
                    print("Error: Invalid Syntax. No ':'?")
            else:
                print("Error: No [] available.")

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
                        if 'after_statement' in Tokens[4]:
                            if Is_In_IF_statement == True and Is_In_FUNC == False:
                                with open("compiled.py", "a") as file:
                                    file.write(f"    {variable_name} {variable_operator} {variable_value}\n")
                            elif Is_In_FUNC == True and Is_In_IF_statement == False:
                                with open("compiled.py", "a") as file:
                                    file.write(f"    {variable_name} {variable_operator} {variable_value}\n")
                            elif Is_In_IF_statement == True and Is_In_FUNC == True:
                                with open("compiled.py", "a") as file:
                                    file.write(f"        {variable_name} {variable_operator} {variable_value}\n")
                            else:
                                with open("compiled.py", "a") as file:
                                    file.write(f"{variable_name} {variable_operator} {variable_value}\n")
                    else:
                        print("Error: Invalid Value '" + Tokens[3] + "'")
                else:
                    print("Error: Invalid Variable Operator '" + Tokens[3] + "'")
            else:
                print("Error: Invalid Variable name '" + Tokens[1] + "'")

        elif "input" in Tokens[0]:
            if 'identifier' in Tokens[1]:
                input_variable_name = Tokens[1].split("|")
                input_variable_name = input_variable_name[0]
                if 'operator' in Tokens[2]:
                    intput_variable_operator = Tokens[2].split("|")
                    input_variable_operator = intput_variable_operator[0]
                    if 'string' in Tokens[3]:
                        input_variable_value = Tokens[3].split("|")
                        input_variable_value = input_variable_value[0]
                        if 'after_statement' in Tokens[4]:
                            if Is_In_IF_statement == True and Is_In_FUNC == False:
                                with open("compiled.py", "a") as file:
                                    file.write(f"    {input_variable_name} {input_variable_operator} input({input_variable_value})\n")
                            elif Is_In_FUNC == True and Is_In_IF_statement == False:
                                with open("compiled.py", "a") as file:
                                    file.write(f"    {input_variable_name} {input_variable_operator} input({input_variable_value})\n")
                            elif Is_In_IF_statement == True and Is_In_FUNC == True:
                                with open("compiled.py", "a") as file:
                                    file.write(f"        {input_variable_name} {input_variable_operator} input({input_variable_value})\n")
                            else:
                                with open("compiled.py", "a") as file:
                                    file.write(f"{input_variable_name} {input_variable_operator} input({input_variable_value})\n")
                    else:
                        print("Error: Invalid Value '" + Tokens[3] + "'. Value must be a String!")
                else:
                    print("Error: Invalid Variable Operator '" + Tokens[3] + "'")
            else:
                print("Error: Invalid Variable name '" + Tokens[1] + "'")

        elif "print" in Tokens[0]:
            if 'string' in Tokens[1] or 'identifier' in Tokens[1] or 'integer' in Tokens[1]:
                print_value = Tokens[1].split("|")
                print_value = print_value[0]
                if 'after_statement' in Tokens[2]:
                    if Is_In_IF_statement == True and Is_In_FUNC == False:
                        with open("compiled.py", "a") as file:
                            file.write(f"    print({print_value})\n")
                    elif Is_In_FUNC == True and Is_In_IF_statement == False:
                        with open("compiled.py", "a") as file:
                            file.write(f"    print({print_value})\n")
                    elif Is_In_IF_statement == True and Is_In_FUNC == True:
                        with open("compiled.py", "a") as file:
                            file.write(f"        print({print_value})\n")
                    else:
                        with open("compiled.py", "a") as file:
                            file.write(f"print({print_value})\n")
                else:
                    print("Error: Invalid Syntax. No ':'?")
            else:
                print("Error: Invalid Value '" + Tokens[1] + "'")

        elif "wait" in Tokens[0] and imported_standard == True:
            if 'integer' in Tokens[1]:
                wait_value = Tokens[1].split("|")
                wait_value = wait_value[0]
                if 'after_statement' in Tokens[2]:
                    if Is_In_IF_statement == True and Is_In_FUNC == False:
                        with open("compiled.py", "a") as file:
                            file.write(f"    time.sleep({wait_value})\n")
                    elif Is_In_FUNC == True and Is_In_IF_statement == False:
                        with open("compiled.py", "a") as file:
                            file.write(f"    time.sleep({wait_value})\n")
                    elif Is_In_IF_statement == True and Is_In_FUNC == True:
                        with open("compiled.py", "a") as file:
                            file.write(f"        time.sleep({wait_value})\n")
                    else:
                        with open("compiled.py", "a") as file:
                            file.write(f"time.sleep({wait_value})\n")
                else:
                    print("Error: Invalid Syntax. No ':'?")
            else:
                print("Error: Invalid Value '" + Tokens[1] + "'")

        elif "end" in Tokens[0]:
            if 'after_statement' in Tokens[1]:
                if Is_In_IF_statement == True and Is_In_FUNC == False:
                    Is_In_IF_statement = False
                elif Is_In_FUNC == True and Is_In_IF_statement == False:
                    Is_In_FUNC = False
                elif Is_In_FUNC == True and Is_In_IF_statement == True:
                    Is_In_IF_statement = False
            else:
                print("Error: Invalid Syntax. No ':'?")

        elif "elseif" in Tokens[0]:
            if 'string' in Tokens[1] or 'integer' in Tokens[1] or 'identifier' in Tokens[1]:
                elseif_statement_one = Tokens[1].split("|")
                elseif_statement_one = elseif_statement_one[0]
                if 'operator' in Tokens[2]:
                    elseif_statement_operator = Tokens[2].split("|")
                    elseif_statement_operator = elseif_statement_operator[0]
                    if 'string' in Tokens[3] or 'integer' in Tokens[3] or 'identifier' in Tokens[3]:
                        elseif_statement_two = Tokens[3].split("|")
                        elseif_statement_two = elseif_statement_two[0]
                        if 'after_statement' in Tokens[4]:
                            if Is_In_IF_statement == True:
                                if Is_In_FUNC == True:
                                    with open("compiled.py", "a") as file:
                                        file.write(f"    elif {elseif_statement_one} {elseif_statement_operator}= {elseif_statement_two}:\n")
                                else:
                                    with open("compiled.py", "a") as file:
                                        file.write(f"elif {elseif_statement_one} {elseif_statement_operator}= {elseif_statement_two}:\n")
                            else:
                                print(f"Error: 'elseif' Statement is not in an 'if' Statement!")
                    else:
                        print("Error: Invalid variable '" + Tokens[3] + "'")
                else:
                    print("Error: Invalid Operator '" + Tokens[2] + "'")
            else:
                print("Error: Invalid variable '" + Tokens[1] + "'")

        elif "func" in Tokens[0]:
            if 'identifier' in Tokens[1]:
                func_name = Tokens[1].split("|")
                func_name = func_name[0]
                if 'list' in Tokens[2]:
                    func_reqs = Tokens[2].split("|")
                    func_reqs = func_reqs[0]
                    func_reqs = func_reqs.replace("[", "")
                    func_reqs = func_reqs.replace("]", "")
                    if 'after_statement' in Tokens[3]:
                        Is_In_FUNC = True
                        with open("compiled.py", "a") as file:
                            file.write(f"def {func_name}({func_reqs}):\n")
                    else:
                        print("Error: Invalid Syntax. No ':'?")
                else:
                    print("Error: No [] available.")
            else:
                print("Error: Invalid Function Name")

        elif "else" in Tokens[0]:
            if 'after_statement' in Tokens[1]:
                if Is_In_IF_statement == True:
                    if Is_In_FUNC == True:
                        with open("compiled.py", "a") as file:
                            file.write(f"    else:\n")
                    else:
                        with open("compiled.py", "a") as file:
                            file.write(f"else:\n")
                else:
                    print(f"Error: 'else' Statement is not in an 'if' Statement!")
            else:
                print("Error: Invalid Syntax. No ':'?")

        elif "if" in Tokens[0]:
            if 'string' in Tokens[1] or 'integer' in Tokens[1] or 'identifier' in Tokens[1]:
                if_statement_one = Tokens[1].split("|")
                if_statement_one = if_statement_one[0]
                if 'operator' in Tokens[2]:
                    if_statement_operator = Tokens[2].split("|")
                    if_statement_operator = if_statement_operator[0]
                    if 'string' in Tokens[3] or 'integer' in Tokens[3] or 'identifier' in Tokens[3]:
                        if_statement_two = Tokens[3].split("|")
                        if_statement_two = if_statement_two[0]
                        if 'after_statement' in Tokens[4]:
                            Is_In_IF_statement = True
                            if Is_In_FUNC == True:
                                with open("compiled.py", "a") as file:
                                    file.write(f"    if {if_statement_one} {if_statement_operator}= {if_statement_two}:\n")
                            else:
                                with open("compiled.py", "a") as file:
                                    file.write(f"if {if_statement_one} {if_statement_operator}= {if_statement_two}:\n")
                    else:
                        print("Error: Invalid variable '" + Tokens[3] + "'")
                else:
                    print("Error: Invalid Operator '" + Tokens[2] + "'")
            else:
                print("Error: Invalid variable '" + Tokens[1] + "'")

        else:
            raise Exception

        print(Is_In_IF_statement, Is_In_FUNC)
    except IndexError:
        with open("compiled.py", "a") as file:
            file.write(" \n")
    except Exception:
        print(f"Error: Invalid Syntax '" + str(source_code) + "'")
        os.remove("compiled.py")
        quit()

def interpreter(file):
    print("Interpreter is not available yet!")

if __name__ == '__main__':
    Is_In_IF_statement   = False
    Is_In_FUNC           = False
    imported_standard    = False
    arg1 = sys.argv[1]
    try:
        arg2 = sys.argv[2]
    except IndexError:
        arg2=None
    if arg2 == "--compiler":
        with open("compiled.py", "w") as file:
            file.write("")
        token_list = []
        with open(arg1, "r") as file:
            content = file.readlines()
        for cont in content:
            # print(cont)
            tokens = tokenize_source_code(cont)
            token_list.append(tokens)
        #print(token_list)
        print(f"{arg1} successfully compiled as compiled.py")
    elif arg2 == "--interpreter":
        interpreter(arg1)
    else:
        interpreter(arg1)