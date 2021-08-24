# %% try running from command line
import pictograph
from pictograph.customNodes import NumberNode, AdditionNode, PrinterNode

# %%
n1 = NumberNode(2.5)
n2 = NumberNode(6.2)

# %%
a = AdditionNode()
p = PrinterNode()

p.connect_input('arg1', a)
a.connect_input('arg1', n1)
a.connect_input('arg2', n2)

# %%
n1._adjust_parameter('Number', 1.0)

# %%
n2.process()

# %%
