import esprima
import escodegen
import base64

all_encode_string = []


def add_decode_function(ast):
    if len(all_encode_string) == 0:
        return
    decode_function = esprima.parseScript(
        "function decodeBase64(index){return decodeURIComponent(escape(window.atob(all_string[index])));}"
    )
    ast.body.insert(0, decode_function.body[0])


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
    def encode_string_literal(node):
        if node.type == 'Literal' and isinstance(node.value, str):
            encoded_value = base64.b64encode(node.value.encode('utf-8')).decode('utf-8')
            try:
                index = all_encode_string.index(encoded_value)
            except ValueError:
                all_encode_string.append(encoded_value)
                index = len(all_encode_string) - 1

            node = esprima.nodes.CallExpression(
                esprima.nodes.Identifier("decodeBase64"),
                [esprima.nodes.Literal(index, f'"{len(all_encode_string) - 1}"')],
            )
        return node

    return traverse(node, func_before=encode_string_literal)


def obfuscate_code(code):
    ast = esprima.parseScript(code)
    # print(ast)

    encode_string(ast)
    add_decode_array(ast)
    add_decode_function(ast)

    return escodegen.generate(ast, options={'format': {'indent': {'style': ''}, 'newline': '', 'space': ''}})


if __name__ == '__main__':
    file_path = ""
    # file_path = "test.js"

    input_code = """
    function add(a, b) {
    a = "aaaa"
    b = "a - b";
    с = "aaaa"
        return a + b;
    }
    // decodeBase64("a")
    """

    if file_path != "":
        with open(file_path, 'r', encoding='utf-8') as file:
            input_code = file.read()

    obfuscated_code = obfuscate_code(input_code)

    print("\n\n\n")
    print(obfuscated_code)



def remove_formatting(ast):
    # Ваш код для удаления символов форматирования
    pass

def add_fake_code(ast):
    # Ваш код для добавления ложного кода
    pass

def modify_control_flow(ast):
    # Ваш код для изменения потока управления программы
    pass

def transform_constants(ast):
    # Ваш код для преобразования констант
    pass

def rename_functions_variables(ast):
    # Ваш код для переименования функций и переменных
    pass
