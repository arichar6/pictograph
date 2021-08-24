from .context import pictograph
from pictograph.customNodes import NumberNode, PrinterNode, AdditionNode

def test_valid():
    n = NumberNode()
    assert n.is_output_valid() == True

def test_connection():
    n = NumberNode()
    p = PrinterNode()
    p.connect_input("arg1", n)
    n._adjust_parameter('Number', 2)

    assert n._process_core() == 2

def test_addition():
    nodes = [NumberNode(n) for n in [2.5, 5.5]]
    a = AdditionNode()
    a.connect_input('arg1', nodes[0])
    a.connect_input('arg2', nodes[1])
    a.process()
    assert a._output_data_cache == 8.0
    nodes[0]._adjust_parameter('Number', 1.0)
    assert a._output_data_cache == 6.5
