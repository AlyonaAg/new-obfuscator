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


def traverse(node, &func_before)
  if func_before.is_a?(Proc)
    node = func_before.call(node)
    # return new_node if new_node != node
  end

  new_child = node.children.dup
  new_child.each_with_index do |value, index|
    if value.is_a?(Parser::AST::Node)
      new_subnode = traverse(value, &func_before)
      if new_subnode != node
        new_child[index] = new_subnode
      end
    end
  end
  node = node.updated(node.type, new_child)

  node
end

def collect_identifier(node)
  collect = lambda do |coll_node|
    types = [:lvasgn, :gvasgn, :cvasgn, :ivasgn, :arg]

    if types.include?(coll_node.type)
      $inner_func_and_var[coll_node.children[0]] = {}
    end

    return coll_node
  end

  traverse(node, &collect)
end


def rename_identifier(node)
  rename = lambda do |rename_node|
    types = [:lvasgn, :gvasgn, :cvasgn, :ivasgn, :lvar, :arg]

    if types.include?(rename_node.type) && $inner_func_and_var.key?(rename_node.children[0])
      unless $all_identifier.key?(rename_node.children[0])
        prefix = extract_prefix(rename_node.children[0].name)
        $all_identifier[rename_node.children[0]] = prefix + gen_name
      end


      new_child = rename_node.children.dup
      new_child[0] = $all_identifier[rename_node.children[0]].to_sym
      rename_node = rename_node.updated(rename_node.type, new_child)
    end

    return rename_node
  end

  traverse(node, &rename)
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
#traverse(ast)
ast = collect_identifier(ast)
ast = rename_identifier(ast)


puts $inner_func_and_var
result_content = Unparser.unparse(ast)
puts result_content
File.open(output_filename, 'w') { |file| file.write(result_content) }