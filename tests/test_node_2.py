from .context import pictograph
from pictograph import Node, customNodes

pi = customNodes.NumberNode(3.14159)
assert pi._process_core() == 3.14159

# TODO: change the sample code below into real tests

adder = customNodes.AdditionNode()
p = customNodes.PrinterNode()
p.connect_input('arg1', adder)


adder.connect_input('arg1', pi)
adder.connect_input('arg2', pi)



print(adder.is_output_valid)
adder.process()
print(adder._output_data_cache)

adder.disconnect_input('arg1')

print(adder.is_output_valid)
print(pi._output_terminals)

adder.disconnect_input('arg2')

print(pi._output_terminals)


