require 'parser/current'
require 'unparser'

$inner_func_and_var = {}
$all_identifier = {}

def extract_prefix(str)
  match = str.match(/^(@@|@|\$)/)
  match.nil? ? "" : match[0]
end

def gen_name
  name = "_0ib#{rand(10..999)}k#{rand(1000..9999)}s"

  while $all_identifier.key?(name)
    name = "_0ib#{rand(10..999)}k#{rand(1000..9999)}s"
  end

  name
end

def get_expr(operation, left, right)
  Parser::AST::Node.new(
    :begin,
    [
      Parser::AST::Node.new(
        :send,
        [
          Parser::AST::Node.new(:int, [left]),
          operation.to_sym,
          Parser::AST::Node.new(:int, [right])]
        )]
    )
end


def traverse(node, &func_before)
  if func_before.is_a?(Proc)
    new_node = func_before.call(node)
  end

  new_child = new_node.children.dup
  new_child.each_with_index do |value, index|
    if value.is_a?(Parser::AST::Node)
      new_subnode = traverse(value, &func_before)
      if new_subnode != new_node
        new_child[index] = new_subnode
      end
    end
  end
  new_node = new_node.updated(new_node.type, new_child)

  new_node
end

def collect_identifier(node)
  collect = lambda do |coll_node|
    types0 = [:lvasgn, :gvasgn, :cvasgn, :ivasgn, :arg, :def]
    types1 = [:const]

    if types0.include?(coll_node.type)
      $inner_func_and_var[coll_node.children[0]] = {}
    elsif types1.include?(coll_node.type)
      $inner_func_and_var[coll_node.children[1]] = {}
    end

    return coll_node
  end

  traverse(node, &collect)
end


def rename_identifier(node)
  rename = lambda do |rename_node|
    types0 = [:lvasgn, :gvasgn, :cvasgn, :ivasgn, :lvar, :arg, :ivar, :cvar, :gvar, :def]
    types1 = [:send, :const]

    if types0.include?(rename_node.type) && $inner_func_and_var.key?(rename_node.children[0])
      unless $all_identifier.key?(rename_node.children[0])
        prefix = extract_prefix(rename_node.children[0].name)
        $all_identifier[rename_node.children[0]] = prefix + gen_name
      end


      new_child = rename_node.children.dup
      new_child[0] = $all_identifier[rename_node.children[0]].to_sym
      rename_node = rename_node.updated(rename_node.type, new_child)
    elsif types1.include?(rename_node.type) && $inner_func_and_var.key?(rename_node.children[1])
      unless $all_identifier.key?(rename_node.children[1])
        prefix = extract_prefix(rename_node.children[1].name)
        if rename_node.type == :const
          prefix = 'C' + prefix
        end
        $all_identifier[rename_node.children[1]] = prefix + gen_name
      end


      new_child = rename_node.children.dup
      new_child[1] = $all_identifier[rename_node.children[1]].to_sym
      rename_node = rename_node.updated(rename_node.type, new_child)
    end

    return rename_node
  end

  traverse(node, &rename)
end


def transform_constants(node)
  transform = lambda do |transform_node|
    if transform_node.type == :int && !$transform_const && transform_node.children.length == 1
      opt = rand(1..7)

      value = transform_node.children[0].to_s.to_i
      case opt
      when 1
        number1 = rand(1..(value + 1)*2)
        if value < number1
          number2 = number1 - value
          return get_expr("-", number1, number2)
        else
          number2 = value - number1
          return get_expr("+", number1, number2)
        end
      when 2
        number1 = rand((value + 1)..((value + 1) * 10))
        number2 = number1 * rand(1..100) + value
        return get_expr("%", number2, number1)
      when 3
        number1 = rand(1..((value + 1) * 10))
        number2 = value ^ number1
        return get_expr("^", number2, number1)
      end
    end

    return transform_node
  end


  traverse(node, &transform)
end

input_filename = ARGV[0]
output_filename = ARGV[1]

input_filename = "test2.rb"
output_filename = "res.rb"

if input_filename.nil? || output_filename.nil?
  puts "Usage: ruby read_file.rb <input_filename> <output_filename>"
  exit
end

begin
  file_content = File.read(input_filename)
rescue Errno::ENOENT
  abort("Error: File '#{filename}' not found.")
rescue Errno::EACCES
  abort("Error: Permission denied for file '#{filename}'.")
rescue => e
  abort("An unexpected error occurred: #{e.message}")
end

ast = Unparser.parse(file_content)
ast = ast.dup
puts ast
ast = collect_identifier(ast)
ast = rename_identifier(ast)
ast = transform_constants(ast)


#puts $inner_func_and_var
result_content = Unparser.unparse(ast)
puts result_content
File.open(output_filename, 'w') { |file| file.write(result_content) }