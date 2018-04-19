# README #

This README gives some info about what Pictograph is, and how it works.

### What is Pictograph ###

**Pictograph** is a graphical interface for connecting and running small pieces of python code. At its core it is meant to provide a rich, graphical, way to create and run workflows, called _pictographs_. These pictographs are created by chaining together _nodes_ or glyphs; it's a visual way to create computer programs. Each glyph represents a small piece of python code, and visually shows its inputs and output as anchors which can be connected to other nodes. Each input is connected to the output of a single other node, and each output can be connected to multiple nodes. The "ready state" of each node is recorded and automatically communicated to all connected nodes, thus allowing the computations represented by the pictograph to proceed automatically once all inputs are defined.

Pictographs are saved in json format for maximum openness and flexibility. Since json is plain text, you can do anything with them that you can do with a text file... like edit them by hand, put them in version control, copy/paste them into an email, etc.

Pictograph is completely written in python, both for speed of development and for maximum "hackability". The quickest way to get started extending Pictograph is to define your own node types. `Node.py` defines the base `Node` class, and your custom subclasses can do any computations that you desire. You define what your node does, and Pictograph turns it into a drag-and-drop black box for incorporating into your workflows.

Here's some ideas of what to do with Pictograph:

* Create computational workflows... visually
* Design and test new computational algorithms
* Create workflows for capturing data in the lab, and running postprocessing routines
* Define pictographs that take your data and automatically create polished graphs
* Anything else you could do with python!



### How do I get set up? ###

Pictograph is currently only available in source format. You need a few things to get up and running with it.

* Some sort of python environment (Using [Anaconda](https://www.anaconda.com/download/) is strongly encouraged!)
* PyQt5 and numpy

Once you have your python environment set up, just run `python main.py`!


### The `Node` base class ###

The node base class defined in `Node.py` is set up to provide nearly all the necessary functionality that makes pictographs work. The behavior of a node is described by a small set of functions, which you can think of as a mini API:

* `list_inputs()`: returns a list of names/keys of the inputs. In traditional programming, these would be the names of function arguments. Each input is another Node.
* `connect_input( input_name, node )`: sets node to be the input for `input_name`
* `disconnect_input( input_name )`: removes the connection for `input_name`
* `connect_output( node )`: adds `node` to the list of output connections
* `disconnect_output( node )`: removes `node` from the list of output connections
* `is_output_valid()`: check if cached output is accurate given the current values of the inputs
* `process()`: do the computation that defines this node
* `set_auto_process(flag)`: set `auto_process` to value of True/False flag, to say if this node should automatically perform its process once its inputs become valid
* `description`: the text that describes this node

For the nerds who care (that's all of you, right?), the Node class works by message passing, using a simple implementation of the Observer design pattern. Each node is both a publisher (subject) and a subscriber (observer). When the node's output becomes valid (or invalid), it sends a message to all nodes connected to its output. Meanwhile it is subscribed to receive messages from all the nodes connected to its inputs. And that's pretty much it; not too complicated is it? Note that the Node class is implemented in a separate file from the rest of the app, so that if you want to use the nodes without the GUI, you totally can.

Also, the output of a node can be anything you want. Since objects in python are fundamental to how the language works, this means that nodes can be much more powerful than you might first imagine. (Want a node that returns the definition of a new python class? You can totally do that.)

Here are a couple examples of node definitions, so that you can see how easy it really is to write your own custom nodes.


    class AdditionNode(Node):
        def __init__(self):
            super().__init__()
            self.displayName = "Add"
            self.description = "Adds two input values"
            self._input_terminals = {"arg1": None, "arg2": None}
    
        def _process_core(self):
            return self.arg1 + self.arg2

Note in this example that the keys in the `_input_terminals` dictionary become variables that you can use in the `_process_core` function.

    class NumberNode(Node):
        def __init__(self, the_value=0):
            super().__init__()
            self.displayName = "Number"
            self.description = "A constant numerical value"
            self._adjustable_parameters = 
                    {'Number': AdjustableParameter(
                    name="Number", 
                    type="double", 
                    val=the_value)}
            self._output_data_cache = self._adjustable_parameters['Number']._value
            self._is_output_valid = True
        
        def _process_core(self):
            self._output_data_cache = self._adjustable_parameters["Number"]._value
            return self._output_data_cache

This example shows a node with "adjustable parameters". These are values that will have a widget in the GUI so that you can, unsurprisingly, adjust their values. For simple parameter types, the GUI widgets will be created automatically. For more complicated nodes, you can create your own QT widget for adjusting the node, displaying its value... whatever you want, really.
