from pictograph.Node import Node, AdjustableParameter


class AdditionNode(Node):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.displayName = "Add"
        self.description = "Adds two input values"
        self._input_terminals = {"arg1": None, "arg2": None}
    
    def _process_core(self):
        return self.arg1 + self.arg2


class NumberNode(Node):
    def __init__(self, the_value=0, **kwargs):
        super().__init__(**kwargs)
        self.displayName = "Number"
        self.description = "A constant numerical value"
        self._adjustable_parameters = {'Number': AdjustableParameter(name="Number", type="double", val=the_value)}
        self._output_data_cache = self._adjustable_parameters['Number']._value
        self._is_output_valid = True
        
    def _process_core(self):
        self._output_data_cache = self._adjustable_parameters["Number"]._value
        return self._output_data_cache


class IntegerNode(Node):
    def __init__(self, the_value=0, **kwargs):
        super().__init__(**kwargs)
        self.displayName = "Integer"
        self.description = "A constant integer"
        self._adjustable_parameters = {"Integer": AdjustableParameter(name="Integer", type="int", val=the_value)}
        self._output_data_cache = self._adjustable_parameters["Integer"]._value
        self._is_output_valid = True
        
    def _process_core(self):
        self._output_data_cache = self._adjustable_parameters["Integer"]._value
        return self._output_data_cache


class PrinterNode(Node):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.displayName = "Print"
        self.description = "A printer, with no output values"
        self._output_data_cache = None
        self._is_output_valid = False
        self._input_terminals = {"arg1": None}
        self._has_output = False
        
    def _process_core(self):
        print('Node value changed to "' + str(self.arg1) + '"')
        return None

    def _invalidate_output(self):
        super()._invalidate_output()
        print( 'Node output became invalid' )
    
    def connect_output(self, the_node):
        raise ValueError("Cannot connect output to this node")


class SubtractionNode(Node):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.displayName = "Subtract"
        self.description = "Subtracts two input values"
        self._input_terminals = {"arg1":None, "arg2":None}
    
    def _process_core(self):
        return self.arg1 - self.arg2


class MultiplicationNode(Node):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.displayName = "Multiply"
        self.description = "Multiplies two input values"
        self._input_terminals = {"arg1":None, "arg2":None}
    
    def _process_core(self):
        return self.arg1 * self.arg2


class StringNode(Node):
    def __init__(self, the_value="", **kwargs):
        super().__init__(**kwargs)
        self.displayName = "String"
        self._adjustable_parameters = {
            "String": 
            AdjustableParameter(name="String", 
                                type="string", 
                                val=the_value)
            }
        self._output_data_cache = self._adjustable_parameters["String"]._value
        self._is_output_valid = True
        
    def _process_core(self):
        self._output_data_cache = self._adjustable_parameters["String"]._value
        return self._output_data_cache


class StringFormatNode(Node):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.displayName = "Format"
        self.description = "Format a string"
        self._input_terminals = {"arg1": None, "arg2": None}
    
    def _process_core(self):
        return self.arg1.format(self.arg2)
        

    