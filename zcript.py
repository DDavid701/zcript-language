import re

def tokenize_source_code(source_code):
    keywords = {
        "var": "identifier",
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

    return Tokens