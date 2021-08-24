import os
import importlib.util
import json
from typing import Type

from pictograph.Node import *


class Pictograph:
    def __init__(self):
        self.scene = PictoCanvas()
        
    def savePictograph(self):
        # save glyphs
        glyph_list = []
        encoder = GlyphEncoder()
        for i,g in enumerate(self.scene.glyphs):
            d = encoder.default(g)
            d['id'] = i
            glyph_list.append(d)
        # save connections
        connection_list = []
        for i,c in enumerate(self.scene.connections):
            d = {'id': i}
            d['startGlyph'] = self.scene.glyphs.index(c.startAnchor.parent)
            d['endGlyph'] = self.scene.glyphs.index(c.endAnchor.parent)
            d['endGlyphKey'] = c.endAnchor.nodeKey
            connection_list.append(d)
        the_file = {'glyphs': glyph_list, 'connections': connection_list}
        # print(json.dumps(the_file, sort_keys=True, indent=4))
        
        filename = None
        if filename:
            with open(filename, 'w') as f:    # use x so that fails if file exists
                print(json.dumps(the_file, sort_keys=True, indent=4), file=f)
    
    def openPictograph(self):
        filename = None
        if filename:
            try:
                with open(filename, 'r') as f:
                    d = json.loads(''.join(f.readlines()))
                    if not 'glyphs' in d:
                        return
                    if not 'connections' in d:
                        return
                    for g in d['glyphs']:
                        obj = self.scene.addGlyphFromDict(g)
                        g['obj'] = obj
                    for c in d['connections']:
                        i = [g['obj'] for g in d['glyphs'] if g['id'] == c['startGlyph']][0]
                        j = [g['obj'] for g in d['glyphs'] if g['id'] == c['endGlyph']][0]
                        startAnchor = i.outputAnchor
                        endAnchor = j.inputAnchors[j.inputAnchorNames.index(c['endGlyphKey'])]
                        self.scene.connectAnchors(startAnchor, endAnchor)
            except:
                print('there was some error loading the file')
    
    def loadGlyphLibrary(self, filename = None):
        if not filename:
            filename = self.selectGlyphLibrary()
        if filename:
            mod_name = os.path.splitext(os.path.basename(filename))
            self.loadGlyphModules(mod_name[0], filename)
        
    def loadGlyphModules(self, mod_name, path=None):
        if path:
            spec = importlib.util.spec_from_file_location(mod_name, path)
            if spec is None:
                print("can't find the module " + mod_name)
            else:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
        else:
            spec = importlib.util.find_spec(mod_name)
            if spec is None:
                print("can't find the module " + mod_name)
            else:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

        def check_mod(m_name):
            m = module.__dict__[m_name]
            return (isinstance(m, type) and
                    issubclass(m, Node) and
                    not m == Node)

        node_list = [m for m in dir(module) if check_mod(m)]

        for name in node_list:
            if self.nodeSelector.findItems(name, QtCore.Qt.MatchExactly):
                print('A node type named ' + name + ' has already been loaded. Loading aborted.')
            else:
                w = QtWidgets.QListWidgetItem(name)
                w.nodeClass = module.__dict__[name]
                self.nodeSelector.addItem(w)


class PictoConnection:
    def __init__(self) -> None:
        self.startGlyph = None
        self.endGlyph = None
        self.endGlyphKey = None


class PictoAnchor:
    def __init__(self) -> None:
        pass


class PictoGlyph:
    def __init__(self, node_class: Type[Node]):
        self._node = node_class()

        # Todo: generate list of anchors?
    
    def set_adjustable_parameters(self, params):
        # set adjustable parameters
        for k, v in params.items():
            self._node._adjust_parameter(k, v)


class PictoCanvas:
    def __init__(self) -> None:
        self.glyphs = []
        self.connections = []

    def addGlyphFromDict(self, d):
        # create a glyph from the dict d, and add it to the scene
        mod_name = d['node_module']

        spec = importlib.util.find_spec('pictograph.' + mod_name)
        if spec is None:
            print("can't find the module " + mod_name)
        else:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        if d['node_class'] in module.__dict__:
            nodeType = module.__dict__[d['node_class']]
        else:
            print('class not found... abort file load.')
            # TODO: somehow do the file abort??
            return

        g = PictoGlyph(nodeType)
        g.set_adjustable_parameters(d['adjustable_parameters'])
        self.addItem(g)

    def deleteItems(self):
        # delete connection if one is active
        if self.activeConnection:
            c = self.activeConnection
            c.disconnect()
            self.connections.remove(c)
            self.removeItem(c)
            self.activeConnection = None
        # delete any selected glyphs
        for item in self.selectedItems():
            connections = []
            if isinstance(item, PictoGlyph):
                clist = item.removeConnections()
                self.removeItem(item)
                self.glyphs.remove(item)
                for c in clist:
                    connections.append(c)
                
            conections = set(connections)
            for c in connections:
                self.connections.remove(c)
                self.removeItem(c)
        
    def addItem(self, item):
        if isinstance(item, PictoGlyph):
            self.glyphs.append(item)
        elif isinstance(item, PictoConnection):
            self.connections.append(item)
        
    def connectAnchors(self, a1, a2):
        if a1.parentItem() == a2.parentItem():
            print('Cannot connect node to itself')
            return
        if a1.nodeKey == "output" and a2.nodeKey == "output":
            print('Cannot connect outputs to each other')
            return
        if "output" not in [a1.nodeKey, a2.nodeKey]:
            print('Cannot connect inputs to each other')
            return
        # TODO: need to check that the input is not already connected
        
        c = PictoConnection(a1, a2)
        self.addItem(c)
        a1.parentItem().addConnection(c)
        a2.parentItem().addConnection(c)
        if a1.nodeKey == "output":
            a1.parentItem().node.connect_output(a2.parentItem().node)
            a2.parentItem().node.connect_input(a2.nodeKey, a1.parentItem().node)
        else:
            a2.parentItem().node.connect_output(a1.parentItem().node)
            a1.parentItem().node.connect_input(a1.nodeKey, a2.parentItem().node)
            

class GlyphEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, PictoGlyph):
            d = obj.node._as_dictionary()
            pos = {'x': obj.pos().x(), 'y': obj.pos().y()}
            d['Position'] = pos
            d['node_module'] = self.get_module(obj)
            return d
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)
    
    def get_module(self, obj):
        name = obj.node.__module__
        if name == '__main__':
            filename = sys.modules[obj.node.__module__].__file__
            name = os.path.splitext(os.path.basename(filename))[0]
        return name

