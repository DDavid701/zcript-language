#!/usr/bin/env python
import os
import re
import sys
import tempfile
import platform

PLATFORM = platform.system()
PYTHON = platform.python_version()

libraries_list =  {
    "standard":         "os, time, sys",
    "platform_tools":   "platform",
}

def tokenize_source_code(source_code, reason, fileName):
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
        "loop":        "identifier",
        "endloop":     "identifier",
        "breakloop":   "identifier",
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
                     "loop",
                     "endloop",
                     "breakloop",
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
    if reason == "comp":
        compiler(Tokens, unedited_source_code)
        code = Tokens
        return str(code)
    elif reason == "interp":
        interpret(Tokens, unedited_source_code, fileName)
        code = Tokens
        return str(code)
    else:
        print("Language Syntax Error: Can't Compile or interpret!")
        quit()

def interpret(Tokens, source_code, fileName):
    global Is_In_IF_statement
    global Is_In_FUNC
    global Is_In_LOOP
    global imported_standard
    try:
        key_ = Tokens[0].split("|")
        key_ = key_[0]
    except Exception:
        key_=None
    #print(key_)
    #print(Is_In_IF_statement, Is_In_FUNC, Is_In_LOOP)
    try:
        if "use" in Tokens[0]:
            library = Tokens[1].split("|")
            library = library[0]
            if library in libraries_list:
                if 'after_statement' in Tokens[2]:
                    with open(fileName, "a") as file:
                        file.write(f"import {libraries_list[library]}\n")
                        if library == "standard":
                            imported_standard = True
                        pass
                else:
                    print("Error: Invalid Syntax. No ':'?")
            else:
                print("Error: Library is does not exist or isn't supported in Zcript")

        elif key_ not in keywords_list and 'identifier' in Tokens[0]:
            func_name = Tokens[0].split("|")
            func_name = func_name[0]
            if 'list' in Tokens[1]:
                func_reqs = Tokens[1].split("|")
                func_reqs = func_reqs[0]
                func_reqs = func_reqs.replace("[", "")
                func_reqs = func_reqs.replace("]", "")
                if 'after_statement' in Tokens[2]:
                    with open(fileName, "a") as file:
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
                            if Is_In_IF_statement == True and Is_In_FUNC == True and Is_In_LOOP == True:
                                with open(fileName, "a") as file:
                                    file.write(f"            {variable_name} {variable_operator} {variable_value}\n")
                            elif Is_In_IF_statement == True and Is_In_FUNC == False:
                                with open(fileName, "a") as file:
                                    file.write(f"    {variable_name} {variable_operator} {variable_value}\n")
                            elif Is_In_FUNC == True and Is_In_IF_statement == False:
                                with open(fileName, "a") as file:
                                    file.write(f"    {variable_name} {variable_operator} {variable_value}\n")
                            elif Is_In_IF_statement == True and Is_In_FUNC == True:
                                with open(fileName, "a") as file:
                                    file.write(f"        {variable_name} {variable_operator} {variable_value}\n")
                            elif Is_In_LOOP == True and Is_In_FUNC == True:
                                with open(fileName, "a") as file:
                                    file.write(f"        {variable_name} {variable_operator} {variable_value}\n")
                            elif Is_In_LOOP == True:
                                with open(fileName, "a") as file:
                                    file.write(f"    {variable_name} {variable_operator} {variable_value}\n")

                            else:
                                with open(fileName, "a") as file:
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
                            if Is_In_IF_statement == True and Is_In_FUNC == True and Is_In_LOOP == True:
                                with open(fileName, "a") as file:
                                    file.write(f"            {input_variable_name} {input_variable_operator} input({input_variable_value})\n")
                            elif Is_In_IF_statement == True and Is_In_FUNC == False:
                                with open(fileName, "a") as file:
                                    file.write(f"    {input_variable_name} {input_variable_operator} input({input_variable_value})\n")
                            elif Is_In_LOOP == True and Is_In_FUNC == True:
                                with open(fileName, "a") as file:
                                    file.write(f"        {input_variable_name} {input_variable_operator} input({input_variable_value})\n")
                            elif Is_In_FUNC == True and Is_In_IF_statement == False:
                                with open(fileName, "a") as file:
                                    file.write(f"    {input_variable_name} {input_variable_operator} input({input_variable_value})\n")
                            elif Is_In_IF_statement == True and Is_In_FUNC == True:
                                with open(fileName, "a") as file:
                                    file.write(f"        {input_variable_name} {input_variable_operator} input({input_variable_value})\n")
                            elif Is_In_LOOP == True:
                                with open(fileName, "a") as file:
                                    file.write(f"    {input_variable_name} {input_variable_operator} input({input_variable_value})\n")

                            else:
                                with open(fileName, "a") as file:
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
                    if Is_In_IF_statement == True and Is_In_FUNC == True and Is_In_LOOP == True:
                        with open(fileName, "a") as file:
                            file.write(f"            print({print_value})\n")
                    elif Is_In_IF_statement == True and Is_In_FUNC == False:
                        with open(fileName, "a") as file:
                            file.write(f"    print({print_value})\n")
                    elif Is_In_LOOP == True and Is_In_FUNC == True:
                        with open(fileName, "a") as file:
                            file.write(f"        print({print_value})\n")
                    elif Is_In_FUNC == True and Is_In_IF_statement == False:
                        with open(fileName, "a") as file:
                            file.write(f"    print({print_value})\n")
                    elif Is_In_IF_statement == True and Is_In_FUNC == True:
                        with open(fileName, "a") as file:
                            file.write(f"        print({print_value})\n")
                    elif Is_In_LOOP == True:
                        with open(fileName, "a") as file:
                            file.write(f"    print({print_value})\n")
                    else:
                        with open(fileName, "a") as file:
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
                    if Is_In_IF_statement == True and Is_In_FUNC == True and Is_In_LOOP == True:
                        with open(fileName, "a") as file:
                            file.write(f"            time.sleep({wait_value})\n")
                    elif Is_In_IF_statement == True and Is_In_FUNC == False:
                        with open(fileName, "a") as file:
                            file.write(f"    time.sleep({wait_value})\n")
                    elif Is_In_FUNC == True and Is_In_IF_statement == False:
                        with open(fileName, "a") as file:
                            file.write(f"    time.sleep({wait_value})\n")
                    elif Is_In_IF_statement == True and Is_In_FUNC == True:
                        with open(fileName, "a") as file:
                            file.write(f"        time.sleep({wait_value})\n")
                    elif Is_In_LOOP == True and Is_In_FUNC == True:
                        with open(fileName, "a") as file:
                            file.write(f"        time.sleep({wait_value})\n")
                    elif Is_In_LOOP == True:
                        with open(fileName, "a") as file:
                            file.write(f"    time.sleep({wait_value})\n")
                    else:
                        with open(fileName, "a") as file:
                            file.write(f"time.sleep({wait_value})\n")
                else:
                    print("Error: Invalid Syntax. No ':'?")
            else:
                print("Error: Invalid Value '" + Tokens[1] + "'")

        elif "end" == key_:
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
                                if Is_In_FUNC == True and Is_In_LOOP == True:
                                    with open(fileName, "a") as file:
                                        file.write(f"        elif {elseif_statement_one} {elseif_statement_operator}= {elseif_statement_two}:\n")
                                elif Is_In_FUNC == True:
                                    with open(fileName, "a") as file:
                                        file.write(f"    elif {elseif_statement_one} {elseif_statement_operator}= {elseif_statement_two}:\n")
                                elif Is_In_LOOP == True:
                                    with open(fileName, "a") as file:
                                        file.write(f"    elif {elseif_statement_one} {elseif_statement_operator}= {elseif_statement_two}:\n")
                                else:
                                    with open(fileName, "a") as file:
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
                        with open(fileName, "a") as file:
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
                    if Is_In_FUNC == True and Is_In_LOOP == True:
                        with open(fileName, "a") as file:
                            file.write(f"        else:\n")
                    elif Is_In_FUNC == True:
                        with open(fileName, "a") as file:
                            file.write(f"    else:\n")
                    elif Is_In_LOOP == True:
                        with open(fileName, "a") as file:
                            file.write(f"    else:\n")
                    else:
                        with open(fileName, "a") as file:
                            file.write(f"else:\n")
                else:
                    print(f"Error: 'else' Statement is not in an 'if' Statement!")
            else:
                print("Error: Invalid Syntax. No ':'?")

        elif "loop" == key_:
            if 'after_statement' in Tokens[1]:
                Is_In_LOOP = True
                if Is_In_FUNC == True:
                    with open(fileName, "a") as file:
                        file.write(f"    while True:\n")
                else:
                    with open(fileName, "a") as file:
                        file.write("while True:\n")
            else:
                print("Error: Invalid Syntax. No ':'?")

        elif "endloop" == key_:
            if 'after_statement' in Tokens[1]:
                if Is_In_LOOP == True:
                    Is_In_LOOP = False
                else:
                    print("Error: 'endloop' Statement is not in an 'loop' Statement!")
            else:
                print("Error: Invalid Syntax. No ':'?")

        elif "breakloop" == key_:
            if 'after_statement' in Tokens[1]:
                if Is_In_FUNC == True and Is_In_LOOP == True:
                    with open(fileName, "a") as file:
                        file.write(f"            break\n")
                elif Is_In_FUNC == True and Is_In_LOOP == True:
                    with open(fileName, "a") as file:
                        file.write(f"        break\n")
                elif Is_In_LOOP == True:
                    with open(fileName, "a") as file:
                        file.write(f"    break\n")
                else:
                    print("Error: 'breakloop' Statement is not in an 'loop' Statement!")
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
                            if Is_In_FUNC == True and Is_In_LOOP == True:
                                with open(fileName, "a") as file:
                                    file.write(f"        if {if_statement_one} {if_statement_operator}= {if_statement_two}:\n")
                            elif Is_In_FUNC == True:
                                with open(fileName, "a") as file:
                                    file.write(f"    if {if_statement_one} {if_statement_operator}= {if_statement_two}:\n")
                            elif Is_In_LOOP == True:
                                with open(fileName, "a") as file:
                                    file.write(f"    if {if_statement_one} {if_statement_operator}= {if_statement_two}:\n")
                            else:
                                with open(fileName, "a") as file:
                                    file.write(f"if {if_statement_one} {if_statement_operator}= {if_statement_two}:\n")
                    else:
                        print("Error: Invalid variable '" + Tokens[3] + "'")
                else:
                    print("Error: Invalid Operator '" + Tokens[2] + "'")
            else:
                print("Error: Invalid variable '" + Tokens[1] + "'")

        else:
            raise Exception

        #print(Is_In_IF_statement, Is_In_FUNC, Is_In_LOOP)
    except IndexError:
        with open(fileName, "a") as file:
            file.write(" \n")
    except Exception:
        print(f"Error: Invalid Syntax '" + str(source_code) + "'")
        os.remove("compiled.py")
        quit()

def compiler(Tokens, source_code):
    global Is_In_IF_statement
    global Is_In_FUNC
    global Is_In_LOOP
    global imported_standard
    try:
        key_ = Tokens[0].split("|")
        key_ = key_[0]
    except Exception:
        key_=None
    #print(key_)
    #print(Is_In_IF_statement, Is_In_FUNC, Is_In_LOOP)
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
            func_name = Tokens[0].split("|")
            func_name = func_name[0]
            if 'list' in Tokens[1]:
                func_reqs = Tokens[1].split("|")
                func_reqs = func_reqs[0]
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
                            if Is_In_IF_statement == True and Is_In_FUNC == True and Is_In_LOOP == True:
                                with open("compiled.py", "a") as file:
                                    file.write(f"            {variable_name} {variable_operator} {variable_value}\n")
                            elif Is_In_IF_statement == True and Is_In_FUNC == False:
                                with open("compiled.py", "a") as file:
                                    file.write(f"    {variable_name} {variable_operator} {variable_value}\n")
                            elif Is_In_FUNC == True and Is_In_IF_statement == False:
                                with open("compiled.py", "a") as file:
                                    file.write(f"    {variable_name} {variable_operator} {variable_value}\n")
                            elif Is_In_IF_statement == True and Is_In_FUNC == True:
                                with open("compiled.py", "a") as file:
                                    file.write(f"        {variable_name} {variable_operator} {variable_value}\n")
                            elif Is_In_LOOP == True and Is_In_FUNC == True:
                                with open("compiled.py", "a") as file:
                                    file.write(f"        {variable_name} {variable_operator} {variable_value}\n")
                            elif Is_In_LOOP == True:
                                with open("compiled.py", "a") as file:
                                    file.write(f"    {variable_name} {variable_operator} {variable_value}\n")

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
                            if Is_In_IF_statement == True and Is_In_FUNC == True and Is_In_LOOP == True:
                                with open("compiled.py", "a") as file:
                                    file.write(f"            {input_variable_name} {input_variable_operator} input({input_variable_value})\n")
                            elif Is_In_IF_statement == True and Is_In_FUNC == False:
                                with open("compiled.py", "a") as file:
                                    file.write(f"    {input_variable_name} {input_variable_operator} input({input_variable_value})\n")
                            elif Is_In_LOOP == True and Is_In_FUNC == True:
                                with open("compiled.py", "a") as file:
                                    file.write(f"        {input_variable_name} {input_variable_operator} input({input_variable_value})\n")
                            elif Is_In_FUNC == True and Is_In_IF_statement == False:
                                with open("compiled.py", "a") as file:
                                    file.write(f"    {input_variable_name} {input_variable_operator} input({input_variable_value})\n")
                            elif Is_In_IF_statement == True and Is_In_FUNC == True:
                                with open("compiled.py", "a") as file:
                                    file.write(f"        {input_variable_name} {input_variable_operator} input({input_variable_value})\n")
                            elif Is_In_LOOP == True:
                                with open("compiled.py", "a") as file:
                                    file.write(f"    {input_variable_name} {input_variable_operator} input({input_variable_value})\n")

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
                    if Is_In_IF_statement == True and Is_In_FUNC == True and Is_In_LOOP == True:
                        with open("compiled.py", "a") as file:
                            file.write(f"            print({print_value})\n")
                    elif Is_In_IF_statement == True and Is_In_FUNC == False:
                        with open("compiled.py", "a") as file:
                            file.write(f"    print({print_value})\n")
                    elif Is_In_LOOP == True and Is_In_FUNC == True:
                        with open("compiled.py", "a") as file:
                            file.write(f"        print({print_value})\n")
                    elif Is_In_FUNC == True and Is_In_IF_statement == False:
                        with open("compiled.py", "a") as file:
                            file.write(f"    print({print_value})\n")
                    elif Is_In_IF_statement == True and Is_In_FUNC == True:
                        with open("compiled.py", "a") as file:
                            file.write(f"        print({print_value})\n")
                    elif Is_In_LOOP == True:
                        with open("compiled.py", "a") as file:
                            file.write(f"    print({print_value})\n")
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
                    if Is_In_IF_statement == True and Is_In_FUNC == True and Is_In_LOOP == True:
                        with open("compiled.py", "a") as file:
                            file.write(f"            time.sleep({wait_value})\n")
                    elif Is_In_IF_statement == True and Is_In_FUNC == False:
                        with open("compiled.py", "a") as file:
                            file.write(f"    time.sleep({wait_value})\n")
                    elif Is_In_FUNC == True and Is_In_IF_statement == False:
                        with open("compiled.py", "a") as file:
                            file.write(f"    time.sleep({wait_value})\n")
                    elif Is_In_IF_statement == True and Is_In_FUNC == True:
                        with open("compiled.py", "a") as file:
                            file.write(f"        time.sleep({wait_value})\n")
                    elif Is_In_LOOP == True and Is_In_FUNC == True:
                        with open("compiled.py", "a") as file:
                            file.write(f"        time.sleep({wait_value})\n")
                    elif Is_In_LOOP == True:
                        with open("compiled.py", "a") as file:
                            file.write(f"    time.sleep({wait_value})\n")
                    else:
                        with open("compiled.py", "a") as file:
                            file.write(f"time.sleep({wait_value})\n")
                else:
                    print("Error: Invalid Syntax. No ':'?")
            else:
                print("Error: Invalid Value '" + Tokens[1] + "'")

        elif "end" == key_:
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
                                if Is_In_FUNC == True and Is_In_LOOP == True:
                                    with open("compiled.py", "a") as file:
                                        file.write(f"        elif {elseif_statement_one} {elseif_statement_operator}= {elseif_statement_two}:\n")
                                elif Is_In_FUNC == True:
                                    with open("compiled.py", "a") as file:
                                        file.write(f"    elif {elseif_statement_one} {elseif_statement_operator}= {elseif_statement_two}:\n")
                                elif Is_In_LOOP == True:
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
                    if Is_In_FUNC == True and Is_In_LOOP == True:
                        with open("compiled.py", "a") as file:
                            file.write(f"        else:\n")
                    elif Is_In_FUNC == True:
                        with open("compiled.py", "a") as file:
                            file.write(f"    else:\n")
                    elif Is_In_LOOP == True:
                        with open("compiled.py", "a") as file:
                            file.write(f"    else:\n")
                    else:
                        with open("compiled.py", "a") as file:
                            file.write(f"else:\n")
                else:
                    print(f"Error: 'else' Statement is not in an 'if' Statement!")
            else:
                print("Error: Invalid Syntax. No ':'?")

        elif "loop" == key_:
            if 'after_statement' in Tokens[1]:
                Is_In_LOOP = True
                if Is_In_FUNC == True:
                    with open("compiled.py", "a") as file:
                        file.write(f"    while True:\n")
                else:
                    with open("compiled.py", "a") as file:
                        file.write("while True:\n")
            else:
                print("Error: Invalid Syntax. No ':'?")

        elif "endloop" == key_:
            if 'after_statement' in Tokens[1]:
                if Is_In_LOOP == True:
                    Is_In_LOOP = False
                else:
                    print("Error: 'endloop' Statement is not in an 'loop' Statement!")
            else:
                print("Error: Invalid Syntax. No ':'?")

        elif "breakloop" == key_:
            if 'after_statement' in Tokens[1]:
                if Is_In_FUNC == True and Is_In_LOOP == True:
                    with open("compiled.py", "a") as file:
                        file.write(f"            break\n")
                elif Is_In_FUNC == True and Is_In_LOOP == True:
                    with open("compiled.py", "a") as file:
                        file.write(f"        break\n")
                elif Is_In_LOOP == True:
                    with open("compiled.py", "a") as file:
                        file.write(f"    break\n")
                else:
                    print("Error: 'breakloop' Statement is not in an 'loop' Statement!")
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
                            if Is_In_FUNC == True and Is_In_LOOP == True:
                                with open("compiled.py", "a") as file:
                                    file.write(f"        if {if_statement_one} {if_statement_operator}= {if_statement_two}:\n")
                            elif Is_In_FUNC == True:
                                with open("compiled.py", "a") as file:
                                    file.write(f"    if {if_statement_one} {if_statement_operator}= {if_statement_two}:\n")
                            elif Is_In_LOOP == True:
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

        #print(Is_In_IF_statement, Is_In_FUNC, Is_In_LOOP)
    except IndexError:
        with open("compiled.py", "a") as file:
            file.write(" \n")
    except Exception:
        print(f"Error: Invalid Syntax '" + str(source_code) + "'")
        os.remove("compiled.py")
        quit()

if __name__ == '__main__':
    Is_In_IF_statement   = False
    Is_In_FUNC           = False
    Is_In_LOOP           = False
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
            tokens = tokenize_source_code(cont, "comp", "unused")
            token_list.append(tokens)
        print(f"Zcript> {arg1} successfully compiled as compiled.py")
    elif arg2 == "--interpreter":
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write('')
            temp_file_path = temp_file.name
        token_list = []
        with open(arg1, "r") as file:
            content = file.readlines()
        for cont in content:
            tokens = tokenize_source_code(cont, "interp", temp_file_path)
            token_list.append(tokens)
        print("<==========================================================>")
        print(f"  Zcript> Starting script {arg1}...")
        print("<==========================================================>")
        os.system(f"python {temp_file_path}")
        os.unlink(temp_file_path)
    elif arg1 == "--create" or arg1 == "--Create" or arg1 == "--C" or arg1 == "--c":
        try:
            with open(f'{arg2}.zc', "w") as file:
                file.write('print "Thanks for using Zcript ;D":')
        except Exception:
            print("Error: No File name found")
            quit()
    elif arg1 == "--info" or arg1 == "--Info" or arg1 == "--I" or arg1 == "--i":
        print(f"Zcript {PLATFORM}: made by DDavid701")
        print("It is trash so please don't use it :)")
    elif arg1 == "--ver" or arg1 == "--version" or arg1 == "--V" or arg1 == "--v":
        print(f"Zcript 1.0.0 ({PYTHON})")
    elif arg1 == "--help" or arg1 == "--Help" or arg1 == "--H" or arg1 == "--h":
        print(f"<----| Zcript Help |---->")
        print("> zcript --V | get the latest version")
        print("> zcript --i | basically credits :D")
        print("> zcript <example.zc> --compiler | Compile your zcript code to python code :)")
        print("> zcript <example.zc> --interpreter | Run your script")
        print("> zcript --create <example_file> | Create a script file")
        print(f"<-| Made by DDavid701 |->")
    else:
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write('')
            temp_file_path = temp_file.name
        token_list = []
        with open(arg1, "r") as file:
            content = file.readlines()
        for cont in content:
            tokens = tokenize_source_code(cont, "interp", temp_file_path)
            token_list.append(tokens)
        print("<==========================================================>")
        print(f"  Zcript> Starting script {arg1}...")
        print("<==========================================================>")
        os.system(f"python {temp_file_path}")
        os.unlink(temp_file_path)