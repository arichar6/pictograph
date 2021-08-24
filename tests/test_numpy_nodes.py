from .context import pictograph
import numpy as np
from pictograph.NumpyNodes import npVectorNode

def test_vector_node():
    vec = np.linspace(0,1,5)
    n = npVectorNode(vec)
    np.testing.assert_equal(n._output_data_cache, vec)
    assert id(n._output_data_cache) == id(vec)

