import esprima
import escodegen
import base64
import random
import utils
from urllib.parse import quote

all_encode_string = ["ZGVjb2RlVVJJQ29tcG9uZW50KCI="]
inner_func_and_var = {}
all_identifier = {}


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



def add_decode_array(ast):
    encode_string_array = []
    for s in all_encode_string:
        encode_string_array.append(esprima.nodes.Literal(s, f'"{s}"'))

    left = esprima.nodes.Identifier("all_string")
    right = esprima.nodes.ArrayExpression(encode_string_array)
    expression = esprima.nodes.AssignmentExpression("=", left, right)
    ast.body.insert(0, esprima.nodes.ExpressionStatement(expression))


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

    def encode_string_literal(node):
        if node.type == 'Literal' and isinstance(node.value, str):
            opt = random.randint(1, 5)
            if opt == 1:
                return base64_encoding(node.value)
            elif opt == 2:
                return unescape_encoding(node.value)
            elif opt == 3:
                return replace_encoding(node.value)

        return node

    return traverse(node, func_before=encode_string_literal)


def rename_identifier(node):
    def gen_name():
        name = '_0ib' + str(random.randint(10, 99)) + 'k' + str(random.randint(1000, 9999)) + 's'
        while name in all_identifier:
            name = '_0ib' + str(random.randint(10, 99)) + 'k' + str(random.randint(1000, 9999)) + 's'
        return name

    def rename(node):
        if node.type == 'Identifier' and node.name in inner_func_and_var:
            if node.name not in all_identifier:
                all_identifier[node.name] = gen_name()

            node.name = all_identifier[node.name]
        return node

    return traverse(node, func_before=rename)


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

    return traverse(node, func_before=collect)


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
                number1 = random.randint(1, (node.value + 1) * 10)
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

    for i in range(random.randint(1, 5)):
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

    return traverse(node, func_before=split)


def obfuscate_code(code):
    ast = esprima.parseScript(code)
    print(ast)

    split_string(ast)
    encode_string(ast)
    add_decode_array(ast)
    add_decode_function(ast)
    collect_identifier(ast)
    rename_identifier(ast)
    transform_constants(ast)
    # print(ast)

    return escodegen.generate(ast, options={
        'format': {'indent': {'style': ''}, 'newline': '', 'space': '', 'hexadecimal': True}})


if __name__ == '__main__':
    file_path = ""
    file_path = "test.js"

    input_code = """
        function add(a, b) {
        a = "aaaaaaaaaaaaaaaaa\u002d"
        c = "-3" + "2"
            return a + b;
        }
        add("a", "b")
        // decodeBase64("a")
    """

    if file_path != "":
        with open(file_path, 'r', encoding='utf-8') as file:
            input_code = file.read()

    obfuscated_code = obfuscate_code(input_code)

    print("\n\n\n")
    print(obfuscated_code)


def add_fake_code(ast):
    # Ваш код для добавления ложного кода
    pass


def modify_control_flow(ast):
    # Ваш код для изменения потока управления программы
    pass
