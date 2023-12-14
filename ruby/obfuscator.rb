require 'parser/current'
require 'unparser'
require 'base64'

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

def get_parts(input_string)
  return [input_string] if input_string.length == 1

  num_parts = rand(1..(input_string.length / 2) + 1)
  return [input_string] if num_parts == 1

  split_indices = (1..input_string.length - 1).to_a.sample(num_parts - 1).sort

  parts = split_indices.each_with_index.map do |j, i|
    prev_index = i.zero? ? 0 : split_indices[i - 1] + 1
    input_string[prev_index..j]
  end

  parts << input_string[split_indices.last + 1..-1] if split_indices.last
  parts
end

def get_base64_encoding(string)
  args = [nil, :"decode_base64", Parser::AST::Node.new(:str, [base64(string).to_s])]
  Parser::AST::Node.new(:send, args)
end

def base64(input_string)
  encoded_string = Base64.encode64(input_string)
  encoded_string.chomp
end


def traverse(node, skip_new, &func_before)
  if func_before.is_a?(Proc)
    new_node = func_before.call(node)
    if new_node != node && skip_new
      return new_node
    end
  end

  new_child = new_node.children.dup
  new_child.each_with_index do |value, index|
    if value.is_a?(Parser::AST::Node)
      new_subnode = traverse(value, skip_new, &func_before)
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
    elsif types1.include?(coll_node.type) && coll_node.children[1] != :Base64
      $inner_func_and_var[coll_node.children[1]] = {}
    end

    return coll_node
  end

  traverse(node, false, &collect)
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

  traverse(node, false, &rename)
end


def transform_constants(node)
  transform = lambda do |transform_node|
    if transform_node.type == :int && transform_node.children.length == 1
      opt = rand(1..4)

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


  for i in 1..4
    node = traverse(node,true, &transform)
  end

  node
end

def split_string(node)
  split = lambda do |split_node|
    if split_node.type == :str
      parts = get_parts(split_node.children[0].to_s)
      if parts.length == 1
        return split_node
      end

      left = Parser::AST::Node.new(:str, [parts[0].to_s])
      parts[1..-1].each do |part|
        left = Parser::AST::Node.new(:send, [left, :+, Parser::AST::Node.new(:str, [part])])
      end
      return left
    end

    split_node
  end

  traverse(node, true, &split)
end

def encoding_string(node)
  encoding = lambda do |encoding_node|
    if encoding_node.type == :str
      opt = rand(1..2)
      if opt == 1
        value = encoding_node.children[0].to_s
        return get_base64_encoding(value)
      end

      return encoding_node
    end

    encoding_node
  end

  traverse(node, true, &encoding)
end

def add_decode_function(node)
  f = Unparser.parse("def decode_base64(encoded_string)\nBase64.decode64(encoded_string)\nend")

  new_child = node.children.dup
  new_child.insert(0, f)

  node.updated(node.type, new_child)
end

def add_require(node)
  req = Unparser.parse("require 'base64'")
  new_child = node.children.dup
  new_child.insert(0, req)

  node.updated(node.type, new_child)
end

input_filename = ARGV[0]
output_filename = ARGV[1]

input_filename = "test.rb"
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

ast = add_decode_function(ast)
ast = split_string(ast)
ast = encoding_string(ast)
ast = collect_identifier(ast)
ast = rename_identifier(ast)
ast = transform_constants(ast)
ast = add_require(ast)



#puts $inner_func_and_var
result_content = Unparser.unparse(ast)
puts result_content
File.open(output_filename, 'w') { |file| file.write(result_content) }
