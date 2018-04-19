from .context import pictograph
from pictograph.customNodes import NumberNode, PrinterNode

def test_valid():
    n = NumberNode()
    assert n.is_output_valid() == True

def test_connection():
    n = NumberNode()
    p = PrinterNode()
    p.connect_input("arg1", n)
    n._adjustable_parameters['Number']._value = 2

    assert n._process_core() == 2
