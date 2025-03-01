import os
import sys

# IR Variables
show_logs = False
is_IR_Made = False
INCLUDE = ""
EXTENSION = ""
OUTPUT = "libxmklib"
SRC_PATH = ""
OUT_DIR = ""
IR_LIST = []  # Stores multiple IRs

def lexer(code):
    tokens = []
    is_function_open = False
    is_comment_started = False
    temp_function_name = ""
    temp_function_data = ""
    cache_function_name = ""

    i = 0
    while i < len(code):
        if code[i] == '\n' and is_comment_started:
            is_comment_started = False
            code = code[i+1:]
            i = 0
            continue
        if is_comment_started:
            i += 1
            continue
        if code[i] == '#' or (code[i] == '/' and i+1 < len(code) and code[i+1] == '/'):
            if is_function_open:
                print("Lexer Err: Invalid Syntax, '#' inside function arguments.")
                sys.exit(3)
            else:
                is_comment_started = True
        elif code[i] == ';':
            if is_function_open:
                print("Lexer Err: Invalid Syntax, ';' inside function arguments.")
                sys.exit(3)
            tokens.append(f"{temp_function_name}:{temp_function_data}")
            temp_function_name = ""
            temp_function_data = ""
            cache_function_name = ""
            code = code[i+1:]
            i = 0
            continue
        elif code[i] == ')' and is_function_open:
            is_function_open = False
        elif is_function_open:
            temp_function_data += code[i]
        elif code[i] == '(' and not is_function_open:
            cache_function_name = ""
            x = i - 1
            while x >= 0:
                cache_function_name += code[x]
                x -= 1
            temp_function_name = ""
            y = len(cache_function_name) - 1
            while y >= 0:
                if cache_function_name[y] != ' ':
                    temp_function_name += cache_function_name[y]
                y -= 1
            is_function_open = True
        i += 1

    if show_logs:
        print("Lexer output tokens:")
        for token in tokens:
            print(token)
    
    return tokens

def function(name, arg):
    global show_logs, SRC_PATH, EXTENSION, OUTPUT, INCLUDE, OUT_DIR, is_IR_Made, IR_LIST

    if show_logs:
        print(f"Executing function: {name} with argument: {arg}")

    if name == "show_logs":
        show_logs = (arg == "true")
    elif name == "source_path":
        SRC_PATH = arg
    elif name == "extension":
        EXTENSION = arg
    elif name == "output":
        OUTPUT = arg
    elif name == "include":
        INCLUDE += f"LIBXINC {SRC_PATH}/{arg}.{EXTENSION}\n"
    elif name == "output_directory":
        if not os.path.exists(arg):
            os.makedirs(arg)
        OUT_DIR = arg
    elif name == "make":
        if OUTPUT and EXTENSION:
            new_IR = f"SIGNAL {OUTPUT}.{EXTENSION}\n{INCLUDE}SIGN-SIGNAL\n"
            IR_LIST.append(new_IR)  # Store the IR separately
            is_IR_Made = True

            # Reset INCLUDE for the next library
            INCLUDE = ""

            if show_logs:
                print("Generated IR:\n" + new_IR)
        else:
            print("Parser Err: Missing output name or extension before 'make ()'.")
            sys.exit(3)
    else:
        print(f"Unknown function: {name}")
        sys.exit(3)

def executer():
    global IR_LIST

    if show_logs:
        print("Executing IRs...")

    for IR in IR_LIST:
        irstream = IR.splitlines()
        files_captured = []
        signal = ""
        libxinc = ""

        for temp in irstream:
            if " " in temp:
                temp_name, temp_arguments = temp.split(" ", 1)
            else:
                temp_name = temp
                temp_arguments = ""

            if temp_name == "SIGNAL":
                signal = temp_arguments
            elif temp_name == "LIBXINC":
                if temp_arguments not in files_captured:
                    try:
                        with open(temp_arguments, "r") as i_include:
                            libxinc += i_include.read() + "\n"
                        files_captured.append(temp_arguments)
                        if show_logs:
                            print(f"Included file: {temp_arguments}")
                    except FileNotFoundError:
                        print(f"Executer Err: File {temp_arguments} not found.")
                        sys.exit(3)
            elif temp_name == "SIGN-SIGNAL":
                if not os.path.exists(OUT_DIR):
                    os.makedirs(OUT_DIR)
                with open(f"{OUT_DIR}/{signal}", "w") as sign_signal_out_file:
                    sign_signal_out_file.write(libxinc)
                files_captured.clear()
                if show_logs:
                    print(f"Library successfully created at {OUT_DIR}/{signal}")

def parser(tokens):
    for token in tokens:
        valid_token = token.replace("\n", "")
        function_name, function_arg = valid_token.split(":", 1)
        if show_logs:
            print(f"Parsing function: {function_name} with argument: {function_arg}")
        function(function_name, function_arg)

def main():
    global show_logs

    if show_logs:
        print("Starting MKLIB...")

    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_build.mklib>")
        sys.exit(1)

    build_file_path = os.path.join(sys.argv[1], "build.mklib")

    if not os.path.isfile(build_file_path):
        print("Error: build.mklib not found.")
        sys.exit(3)

    if show_logs:
        print("Loaded build.mklib")

    with open(build_file_path, "r") as config:
        config_data = config.read()

    parser(lexer(config_data))
    executer()

    if show_logs:
        print("MKLIB execution completed.")

if __name__ == "__main__":
    main()
