"""
A node/glyph, which is the basic processing unit in a pictograph/flowchart/canvas
"""
from abc import ABC, abstractmethod
import json


class AdjustableParameter(object):
    def __init__(self, name, type, val):
        self.name = name
        self.type = type
        self.default = None
        self.values = []     # this is only used for type "options"
        self._value = val

    def _as_dictionary(self):
        return self.__dict__

    def __setattr__(self, key, value):
        super().__setattr__(key, value)


class Node(ABC):
    output_now_valid_message = 0
    output_now_invalid_message = 1
    
    def __init__(self, auto_process=False, **kwargs):
        # This looks like a dict of arguments to a function, but every argument is a Node
        self._input_terminals = {}

        # Each node can only have one output. This is a list of nodes that have signed up 
        # to receive the output of this node as one of their inputs.
        self._output_terminals = []
        
        # flag for outputs, eg, plots or file save may not have "output"
        self._has_output = True
        
        self.description = ""
        self.displayName = ""
        self._output_data_cache = None
        self._is_output_valid = False
        self._auto_process = auto_process
        self._adjustable_parameters = {}

    # -------- Private API ---------
    def _adjust_parameter(self, key, new_value):
        self._adjustable_parameters[key]._value = new_value
        self.process()
        
    def _inputs_are_defined(self):
        # check that all inputs are connected to nodes
        for key, input_node in self._input_terminals.items():
            if input_node is None:
                return False
        return True

    def _inputs_are_valid(self):
        if not self._inputs_are_defined(): return False
        # check that all inputs are valid
        for key, input_node in self._input_terminals.items():
            if not isinstance(input_node, Node):
                return False
            if input_node._is_output_valid is False:
                return False
        return True
    
    def _cache_input_vars(self):
        # should check for validity here?
        # cache the input data for easier access
        for key, input_node in self._input_terminals.items():
            vars(self)[key] = input_node._output_data_cache

    def _invalidate_input_cache(self, input_node):
        # reset cached inputs
        for key, node in self._input_terminals.items():
            if node == input_node:
                vars(self)[key] = None

    def _notify_output_nodes(self, message):
        # go through list of nodes receiving this node's output and send message
        for output_node in self._output_terminals:
            output_node._receive_message(message, self)

    def _receive_message(self, message, sender):
        if message == Node.output_now_valid_message:
            self.process()
        elif message == Node.output_now_invalid_message:
            self._invalidate_output()
            self._invalidate_input_cache(sender)

    def _invalidate_output(self):
        # reset the output cache, "complete" flag, and cached inputs
        self._output_data_cache = None
        self._is_output_valid = False
        self._notify_output_nodes(Node.output_now_invalid_message)
    
    def _as_dictionary(self):
        # return a dictionary with enough information to recreate this Node
        the_dict = {"node_class": self.__class__.__name__,
                    "adjustable_parameters": self._adjustable_parameters}
        return the_dict

    @abstractmethod
    def _process_core(self):
        # This is where input data is processed to become output data.
        # It must be defined by subclasses and return the processed data. E.g.,
        #    _process_core(self):
        #        return self.arg1 + self.arg2
        pass

    # -------- Public API ---------
    def process(self):
        if self._inputs_are_valid():
            self._cache_input_vars()
            self._output_data_cache = self._process_core()
            self._is_output_valid = True
            self._notify_output_nodes(Node.output_now_valid_message)
        else:
            pass  # should really set some error flag or something?

    def disconnect_input(self, input_key):
        tmp_node = self._input_terminals[input_key]
        self._input_terminals[input_key] = None
        # If tmp_node is not being used as another input to this node,
        #   tell it to remove this node from its output connections
        if tmp_node not in set(self._input_terminals.values()):
            tmp_node.disconnect_output(self)
        self._invalidate_output()

    def connect_input(self, input_key, the_node):
        if input_key not in self._input_terminals:
            node_error('The key "' + input_key + '" does not describe a valid input terminal')
            return
        if self._input_terminals[input_key] is not None:
            node_error('The input terminal ' + input_key + ' is already connected')
            return
        self._input_terminals[input_key] = the_node
        the_node.connect_output(self)
        if self._auto_process:
            self.process()
        
    def connect_output(self, the_node):
        if the_node not in self._output_terminals:
            self._output_terminals.append(the_node)

    def disconnect_output(self, the_node):
        if the_node in self._output_terminals: self._output_terminals.remove(the_node)
    
    def set_auto_process(self, flag):
        if flag not in [True, False]:
            node_error('The auto_process flag must be either True or False')
            return
        self._auto_process = flag

    def is_output_valid(self):
        return self._is_output_valid


class NodeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Node):
            return obj._as_dictionary()
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)
        
        
def node_error(message):
    raise ValueError(message)
