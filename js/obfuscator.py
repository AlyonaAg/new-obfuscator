import esprima
import escodegen
import base64
import random
import utils
from urllib.parse import quote

all_encode_string = ["ZGVjb2RlVVJJQ29tcG9uZW50KCI="]
inner_func_and_var = {}
all_identifier = {}
func_args = {}
instructions = []


def add_decode_function(ast):
    decode_unescape_function = esprima.parseScript(
        'function decodeUnescape(value){return eval(decodeBase64(0) + value + "\\")");}'
    )
    ast.body.insert(0, decode_unescape_function.body[0])

    decode_base64_function = esprima.parseScript(
        'function decodeBase64(index){return eval(' +
        '"d4e454c33o44d21e21U2R50I1C42o13m2p49o18n9e21n17t16(8e49s2c27a2p8e41(33w3i35n4d25o25w19.2a17t31o50b438(4\\""' +
        '.replace(/[0-9]/g,"") + all_string[index] + "\\")))");}'
    )
    ast.body.insert(0, decode_base64_function.body[0])

    decode_replace_encoding = esprima.parseScript(
        'function decodeReplace(value, r){return value.replaceAll(r,  "")}'
    )
    ast.body.insert(0, decode_replace_encoding.body[0])

    decode_reverse = esprima.parseScript(
        'function rev(value){ var a=value.split(""); var b=a.reverse(); var c=b.join("");return c;}'
    )
    ast.body.insert(0, decode_reverse.body[0])


def add_decode_array(ast):
    encode_string_array = []
    for s in all_encode_string:
        encode_string_array.append(esprima.nodes.Literal(s, f'"{s}"'))

    left = esprima.nodes.Identifier("all_string")
    right = esprima.nodes.ArrayExpression(encode_string_array)
    expression = esprima.nodes.AssignmentExpression("=", left, right)
    ast.body.insert(0, esprima.nodes.ExpressionStatement(expression))


def gen_expression(var_names):
    opt = random.randint(1 if len(var_names) > 0 else 2, 3)
    if opt == 1:
        return esprima.nodes.Identifier(random.choice(var_names))
    elif opt == 2:
        val = random.randint(1, 1000)
        return esprima.nodes.Literal(val, f'{val}')
    else:
        val = utils.generate_unique_sequence(random.randint(1, 10))
        return esprima.nodes.Literal(val, f'"{val}"')


def traverse(node, func_before=None, func_after=None):
    if func_before is not None:
        new_node = func_before(node)
        if new_node != node:
            return new_node

    node_items = node.items()
    for key, value in node_items:
        if key != 'type':
            if isinstance(value, list):
                for i, item in enumerate(value):
                    value[i] = traverse(item, func_before, func_after)
            elif isinstance(value, esprima.nodes.Node):
                setattr(node, key, traverse(value, func_before, func_after))

    if func_after is not None:
        new_node = func_before(node)
        if new_node != node:
            return new_node

    return node


def encode_string(node):
    def base64_encoding(value):
        encoded_value = base64.b64encode(value.encode('utf-8')).decode('utf-8')
        try:
            index = all_encode_string.index(encoded_value)
        except ValueError:
            all_encode_string.append(encoded_value)
            index = len(all_encode_string) - 1

        return esprima.nodes.CallExpression(
            esprima.nodes.Identifier("decodeBase64"),
            [esprima.nodes.Literal(index, f'"{len(all_encode_string) - 1}"')],
        )

    def unescape_encoding(value):
        # val = ''.join([f"%{ord(char):02x}" for char in value])
        val = quote(value, safe='')

        return esprima.nodes.CallExpression(
            esprima.nodes.Identifier("decodeUnescape"),
            [esprima.nodes.Literal(val, f'"{val}"')],
        )

    def replace_encoding(value):
        while True:
            random_sequence = utils.generate_unique_sequence(random.randint(3, 5))
            if random_sequence not in value:
                break

        parts = utils.get_parts(value)
        if len(parts) == 1:
            index_to_insert = int(len(value)/2)
            val = value[:index_to_insert] + random_sequence + value[index_to_insert:]
        else:
            val = random_sequence.join(parts)

        return esprima.nodes.CallExpression(
            esprima.nodes.Identifier("decodeReplace"),
            [esprima.nodes.Literal(val, f'"{val}"'), esprima.nodes.Literal(random_sequence, f'"{random_sequence}"')],
        )

    def reverse_encoding(value):
        val = value[::-1]

        return esprima.nodes.CallExpression(
            esprima.nodes.Identifier("rev"),
            [esprima.nodes.Literal(val, f'"{val}"')],
        )

    def encode_string_literal(node):
        if node.type == 'Literal' and isinstance(node.value, str):
            opt = random.randint(1, 4)
            if opt == 1:
                return base64_encoding(node.value)
            elif opt == 2:
                return unescape_encoding(node.value)
            elif opt == 3:
                return replace_encoding(node.value)
            elif opt == 4:
                return reverse_encoding(node.value)

        return node

    traverse(node, func_before=encode_string_literal)


def rename_identifier(node):
    def rename(node):
        if node.type == 'Identifier' and node.name in inner_func_and_var:
            if node.name not in all_identifier:
                all_identifier[node.name] = utils.gen_name(all_identifier)

            node.name = all_identifier[node.name]
        return node

    traverse(node, func_before=rename)


def collect_identifier(node):
    def collect(node):
        if node.type == 'FunctionDeclaration':
            inner_func_and_var[node.id.name] = {}
            for p in node.params:
                inner_func_and_var[p.name] = {}
        elif node.type == 'AssignmentExpression':
            inner_func_and_var[node.left.name] = {}
        elif node.type == 'VariableDeclarator':
            inner_func_and_var[node.id.name] = {}

        return node

    traverse(node, func_before=collect)


def collect_instruction(node):
    def collect(node):
        if node.type == 'ExpressionStatement':
            instructions.append(node)
        elif node.type == 'ForStatement':
            instructions.append(node)
        elif node.type == 'IfStatement':
            instructions.append(node)
        elif node.type == 'WhileStatement':
            instructions.append(node)

        return node

    traverse(node, func_before=collect)


def transform_constants(node):
    def get_literal(number):
        literal = esprima.nodes.Literal(abs(number), f'{abs(number)}')
        if number > 0:
            return literal
        return esprima.nodes.UnaryExpression('-', literal)

    def transform(node):
        if node.type == 'Literal' and isinstance(node.value, int):
            opt = random.randint(1, 5)
            if opt == 1:
                number1 = random.randint(1, node.value + 1)
                if number1 < node.value:
                    number2 = number1 - node.value

                    return esprima.nodes.BinaryExpression(
                        '-',
                        get_literal(number1),
                        get_literal(number2),
                    )
                else:
                    number2 = node.value - number1

                    return esprima.nodes.BinaryExpression(
                        '+',
                        get_literal(number2),
                        get_literal(number1),
                    )
            elif opt == 2:
                number1 = random.randint((node.value + 1), (node.value + 1) * 10)
                number2 = number1 * random.randint(1, 100) + node.value

                return esprima.nodes.BinaryExpression(
                    '%',
                    get_literal(number2),
                    get_literal(number1),
                )
            elif opt == 3:
                number1 = random.randint(1, (node.value + 1) * 10)
                number2 = node.value ^ number1

                return esprima.nodes.BinaryExpression(
                    '^',
                    get_literal(number2),
                    get_literal(number1),
                )

        return node

    for i in range(random.randint(1, 3)):
        node = traverse(node, func_before=transform)
    return node


def split_string(node):
    def split(node):
        if node.type == 'Literal' and isinstance(node.value, str):
            parts = utils.get_parts(node.value)
            if len(parts) == 1:
                return node

            left = esprima.nodes.Literal(parts[0], f'"{parts[0]}"')
            for part in parts[1:]:
                left = esprima.nodes.BinaryExpression('+', left, esprima.nodes.Literal(part, f'"{part}"'))
            return left

        return node

    traverse(node, func_before=split)


def add_args(node):
    def add_to_declaration(node):
        if node.type == 'FunctionDeclaration':
            new_count_arg = random.randint(len(node.params), len(node.params)*2 + 3)
            idx = utils.generate_unique_random_numbers(len(node.params), new_count_arg)

            func_args[node.id.name] = {'idx': idx, 'count': new_count_arg}

            params = []
            for i in range(new_count_arg):
                params.append(esprima.nodes.Identifier(utils.generate_unique_sequence(3)))

            for index, value in enumerate(node.params):
                params[idx[index]] = value

            node.params = params
        return node

    def add_to_call(node):
        if node.type == 'CallExpression':
            if node.callee.name not in func_args:
                return node

            args_name = []
            for a in node.arguments:
                if a.type == 'Identifier':
                    args_name.append(a.name)

            new_args = func_args[node.callee.name]
            if len(node.arguments) == new_args['count']:
                return node

            args = []
            for i in range(new_args['count']):
                val = gen_expression(args_name)
                args.append(val)

            for index, value in enumerate(node.arguments):
                args[new_args['idx'][index]] = value

            node.arguments = args

        return node

    traverse(node, func_before=add_to_declaration)
    traverse(node, func_before=add_to_call)


def add_fake_function(ast):
    def gen_body():
        body = []
        for _ in range(random.randint(1, min(len(instructions), 15))):
            body.append(random.choice(instructions))
        return esprima.nodes.BlockStatement(body)

    def gen_args():
        return []

    def gen_func():
        func_name = utils.gen_name(all_identifier)
        body = gen_body()
        args = gen_args()

        return esprima.nodes.FunctionDeclaration(
            esprima.nodes.Identifier(func_name),
            args,
            body,
            False
        )

    collect_instruction(ast)

    for _ in range(random.randint(1, min(len(ast.body), 5))):
        ast.body.insert(random.randint(0, len(ast.body) - 1), gen_func())


def obfuscate_code(code):
    ast = esprima.parseScript(code)
    print(ast)

    split_string(ast)
    encode_string(ast)
    add_decode_array(ast)
    add_decode_function(ast)
    add_fake_function(ast)
    add_args(ast)
    collect_identifier(ast)
    rename_identifier(ast)
    transform_constants(ast)
    #print(ast)

    return escodegen.generate(ast, options={
        'format': {'indent': {'style': ''}, 'newline': '', 'space': '', 'hexadecimal': True}})


if __name__ == '__main__':
    file_path = ""
    file_path = "test.js"

    input_code = """
        function add(a, b) {
            return a + b;
        }
        add("a", "b")
    """

    if file_path != "":
        with open(file_path, 'r', encoding='utf-8') as file:
            input_code = file.read()

    obfuscated_code = obfuscate_code(input_code)

    with open('res.js', 'w') as file:
        file.write(obfuscated_code)

    print("\n\n\n")
    #print(obfuscated_code)
