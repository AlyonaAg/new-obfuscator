import subprocess
import os
import sexpdata


ast_filename = 'res.tmp'


def ruby_code_to_nested_lists(ruby_ast):
    try:
        sexp = sexpdata.loads(ruby_ast)
        d = sexpdata.dumps(sexp)
        return sexp
    except sexpdata.ExpectClosingBracket as e:
        print(f"Error: {e}")


if __name__ == '__main__':
    filename = 'test2.rb'

    ruby_script_path = os.getcwd() + '\\parser.rb'
    ruby_script_args = ['p', filename, ast_filename]
    command = ['ruby', ruby_script_path] + ruby_script_args

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        print("Error executing Ruby script:", e)

    with open(ast_filename, 'r', encoding='utf-8') as file:
        input_code = file.read()

    ast = ruby_code_to_nested_lists(input_code)
    print(ast)
