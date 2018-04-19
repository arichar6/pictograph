from pictograph.Node import Node, AdjustableParameter
from PyQt5 import QtCore, QtWidgets, QtGui


class MultiplicationNode(Node):
    def __init__(self):
        super().__init__()
        self.displayName = "Multiply"
        self.description = "Multiplies two input values"
        self._input_terminals = {"arg1": None, "arg2": None}
    
    def _process_core(self):
        return self.arg1 * self.arg2


class AnotherNumberNode(Node):
    def __init__(self, the_value=0):
        super().__init__()
        self.displayName = "Number"
        self.description = "A constant numerical value"
        self._adjustable_parameters = {'Number': AdjustableParameter(name="Number", type="double", val=the_value)}
        self._output_data_cache = self._adjustable_parameters['Number']._value
        self._is_output_valid = True

    def _process_core(self):
        self._output_data_cache = self._adjustable_parameters["Number"]._value
        return self._output_data_cache

    def as_widget(self):
        locale = QtCore.QLocale()
        labelWidget = QtWidgets.QLabel("Set the number:")
        w = QtWidgets.QLineEdit()
        w.setText(str(self._adjustable_parameters['Number']._value))
        w.setValidator(QtGui.QDoubleValidator(-1e-15, 1e15, 10, w))
        w.textChanged.connect(lambda val: self._adjust_parameter('Number', locale.toDouble(val)[0]) )

        editWidget = w
        return labelWidget, editWidget

