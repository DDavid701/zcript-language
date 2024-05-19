import zcript
from platform import system

print(f"Zcript 1.0 ({system()})")

while True:
    INPUT = input(">")
    RESULT = zcript.tokenize_source_code(INPUT)
    print(RESULT)