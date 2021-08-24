"""
Nodes which know about numpy arrays
"""
from pictograph.Node import Node, AdjustableParameter
import numpy as np


class ZerosNode(Node):
    def __init__(self):
        super().__init__()
        self.displayName = "Np Zeros"
        self.description = "Create Numpy Array of Zeros"
        self._adjustable_parameters = {"Length": AdjustableParameter(name="Length", type="int", val=0)}
    
    def _process_core(self):
        return np.zeros((1,self._adjustable_parameters["Length"]._value))


class OnesNode(Node):
    def __init__(self):
        super().__init__()
        self.displayName = "Np Ones"
        self.description = "Create Numpy Array of Ones"
        self._adjustable_parameters = {"Length": AdjustableParameter(name="Length", type="int", val=0)}

    def _process_core(self):
        return np.ones((1,self._adjustable_parameters["Length"]._value))


class npVectorNode(Node):
    def __init__(self, v=np.zeros(1)):
        super().__init__()
        self.displayName = "np Vector"
        self.description = "A numpy vector"
        self._adjustable_parameters = {"Vector": AdjustableParameter(name="Vector", type="Vector", val=v)}
        self._output_data_cache = self._adjustable_parameters["Vector"]._value
        self._is_output_valid = True

    def _process_core(self):
        self._output_data_cache = self._adjustable_parameters["Vector"]._value
        return self._output_data_cache
