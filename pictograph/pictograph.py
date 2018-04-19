#!/usr/bin/env python
import sys
import os

from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtWidgets import QGraphicsView
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget
from PyQt5 import QtCore, QtGui, QtWidgets

from pictograph.Node import *
import importlib.util
import json


class MainWindow(QMainWindow):

    central_widget = None
    layout_container = None

    def __init__(self):
        super(MainWindow, self).__init__()
        self.central_widget = QWidget()
        self.layout_container = QVBoxLayout()
        self.central_widget.setLayout(self.layout_container)
        self.setCentralWidget(self.central_widget)
        self.setMinimumSize(QtCore.QSize(1000, 600))
        
        # This Scene is the "controller" in the MVC methodology (really?)
        self.scene = PictoScene(self)
        # This view is the "view" in MVC
        self.view = QGraphicsView()
        self.view.setDragMode(QGraphicsView.RubberBandDrag)
        self.view.setScene(self.scene)
        self.view.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.layout_container.addWidget(self.view)
        
        # set up menu/toolbar actions
        exitAct = QtWidgets.QAction(QtGui.QIcon('exit24.png'), 'Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.triggered.connect(QtWidgets.qApp.quit)        
        
        deleteItemsAction = QtWidgets.QAction(QtGui.QIcon('delete.png'), 'Delete Item(s)', self)
        deleteItemsAction.setShortcut('Del')
        deleteItemsAction.setShortcut('Backspace')
        deleteItemsAction.triggered.connect(self.scene.deleteItems)

        openPictographAction = QtWidgets.QAction(QtGui.QIcon('open.png'), 'Open…', self)
        openPictographAction.setShortcut('Ctrl+O')
        openPictographAction.triggered.connect(self.openPictograph)
        
        savePictographAction = QtWidgets.QAction(QtGui.QIcon('save.png'), 'Save', self)
        savePictographAction.setShortcut('Ctrl+S')
        savePictographAction.triggered.connect(self.savePictograph)
        saveAsPictographAction = QtWidgets.QAction(QtGui.QIcon('saveas.png'), 'Save As…', self)
        saveAsPictographAction.setShortcut('Shift+Ctrl+S')
        newPictographAction = QtWidgets.QAction(QtGui.QIcon('new.png'), 'New', self)
        newPictographAction.setShortcut('Ctrl+N')

        loadGlyphsAction = QtWidgets.QAction(QtGui.QIcon('load.png'), 'Load Glyph Library', self)
        loadGlyphsAction.setShortcut('Ctrl+L')
        loadGlyphsAction.triggered.connect(self.loadGlyphLibrary)

        # set up the menubar
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(newPictographAction)
        fileMenu.addSeparator()
        fileMenu.addAction(openPictographAction)
        fileMenu.addSeparator()
        fileMenu.addAction(savePictographAction)
        fileMenu.addAction(saveAsPictographAction)
        fileMenu.addSeparator()
        fileMenu.addAction(loadGlyphsAction)
        editMenu = menubar.addMenu('&Edit')
        editMenu.addAction(deleteItemsAction)

        # set up the toolbar
        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(exitAct)        
        self.toolbar.addAction(deleteItemsAction)
        self.toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)

        # set up the "add node" sidebar
        self.nodeSelector = QtWidgets.QListWidget()

        def betterMousePress(event):
            oldSelection = self.nodeSelector.selectedItems()
            self.nodeSelector.clearSelection()
            QtWidgets.QListWidget.mousePressEvent(self.nodeSelector, event)
            if self.nodeSelector.selectedItems() == oldSelection:
                self.nodeSelector.clearSelection()            

        self.nodeSelector.mousePressEvent = betterMousePress
        
        nodeDockW = QtWidgets.QWidget()
        nodeDockL = QVBoxLayout()
        nodeDockW.setLayout(nodeDockL)
        nodeDockL.addWidget(self.nodeSelector)
        addNodeDock = QtWidgets.QDockWidget("Nodes", self)
        addNodeDock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        addNodeDock.setWidget(nodeDockW)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, addNodeDock)
        
        # add the default set of nodes
        self.loadGlyphModules('pictograph.customNodes')
        self.loadGlyphModules('pictograph.NumpyNodes')
        self.loadGlyphModules('pictograph.customNodeTest')

        # set up the node editor
        self.nodeEditor = NodeEditor(parent = self)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.nodeEditor)
        
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

        options = QtWidgets.QFileDialog.Options()
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self,"Save As","","All Files (*);;Pictograph Files (*.pictograph)", options=options)
        # todo, update this to do the normal save/save as behavior
        if filename:
            with open(filename, 'w') as f:    # use x so that fails if file exists
                print(json.dumps(the_file, sort_keys=True, indent=4), file=f)
    
    def clearNodeEditor(self):
        self.nodeEditor.clear()

    def openPictograph(self):
        options = QtWidgets.QFileDialog.Options()
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self,"Select Pictograph", "","All Files (*);;Pictograph Files (*.pictograph)", options=options)
        if filename:
            # TODO: 
            # if this window is empty, open here
            # otherwise make a new window and open there
            # Change try/catch to read entire file before adding any to scene
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
    
    def selectGlyphLibrary(self):
        # have user select file
        options = QtWidgets.QFileDialog.Options()
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self,"Select Glyph Library", "","All Files (*);;Python Files (*.py)", options=options)
        return filename        
        
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


class NodeEditor(QtWidgets.QDockWidget):
    def __init__(self, parent):
        super(NodeEditor, self).__init__("Node Editor", parent)
        
        gb = QtWidgets.QWidget()
        self.nodeEditorGroup = QVBoxLayout()
        gb.setLayout(self.nodeEditorGroup)
        gb.setMinimumSize(QtCore.QSize(300,50))
        self.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        self.setWidget(gb)
        
    def clear(self):
        ng = self.nodeEditorGroup
        while ng.count():
            child = ng.takeAt(0)
            if child.widget():
              child.widget().deleteLater()

    def update(self, node):
        self.clear()
        self.textBox = QtWidgets.QTextEdit()
        self.textBox.setText(node.displayName + ": " +  node._output_data_cache.__repr__())
        self.nodeEditorGroup.addWidget(self.textBox)

        self.addWidgetsForNode(node)

    def addWidgetsForNode(self, node):
        if hasattr(node, 'as_widget') and callable(node.as_widget):
            try:
                for w in node.as_widget():
                    self.nodeEditorGroup.addWidget(w)
            except TypeError:
                self.nodeEditorGroup.addWidget(node.as_widget())
        else:
            for k, p in node._adjustable_parameters.items():
                l, w = self.parameter_as_widgets(p, node)
                self.nodeEditorGroup.addWidget(l)
                self.nodeEditorGroup.addWidget(w)
    
    def setAdjustedParameter(self, node, key, value):
        print(value)
        node._adjust_parameter(key, value)
        self.textBox.setText(node.displayName + ": " +  node._output_data_cache.__repr__())
    
    def parameter_as_widgets(self, p, node):
        locale = QtCore.QLocale()
        labelWidget = QtWidgets.QLabel(p.name)
        w = QtWidgets.QLineEdit()
        w.setText(str(p._value))
        if p.type == "string":
            # validate strings?
            w.textChanged.connect(lambda val: node._adjust_parameter(p.name, val) )
        elif p.type == "double":
            w.setValidator(QtGui.QDoubleValidator(-1e-15, 1e15, 10, w))
            w.textChanged.connect(lambda val: node._adjust_parameter(p.name, locale.toDouble(val)[0]) )
        elif p.type == "int":
            w.setValidator(QtGui.QIntValidator(w))
            w.textChanged.connect(lambda val: node._adjust_parameter(p.name, locale.toInt(val)[0]) )

        editWidget = w
        return labelWidget, editWidget


class PictoScene(QGraphicsScene):
    def __init__(self, parent):
        super(PictoScene, self).__init__()
        self.setParent(parent)
        
        # hack to get the first glyph to stay where the click happened
        r = QtCore.QRectF(0,0,300,300)
        r = QtWidgets.QGraphicsRectItem(r)
        r.setVisible(False)
        self.addItem(r)

        # This cavas is the "model" in MVC. It holds the nodes
        # self.canvas = Canvas()
        
        # This is the "model" in MVC.
        # TODO: refactor so glyphs+connections is the model. This
        # will allow things like load/save files to happen separate
        # from the GUI. 
        self.glyphs = []
        self.connections = []
        
        self.activeAnchor = None
        self.activeConnection = None

    def addGlyphFromDict(self, d):
        # create a glyph from the dict d, and add it to the scene
        pos = QtCore.QPointF(d['Position']['x'], d['Position']['y'])
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

        g = PictoGlyph(pos, nodeType)
        # set adjustable parameters
        for k,v in d['adjustable_parameters'].items():
            g.node._adjust_parameter(k, v)
        self.addItem(g)
        return g

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
        
    def drawBackground(self, painter, rect):
        # TODO: still need to figure out how to redraw this when nodes move and when the view scrolls
        # also, this needs to have the gradient height based on window size, instead of fixed at 500
        gradient = QtGui.QLinearGradient(0, 0, 0, 500)
        gradient.setColorAt(0.0, QtGui.QColor(117, 213, 255))
        gradient.setColorAt(1.0, QtGui.QColor(5, 131, 255))
        painter.fillRect(rect, QtGui.QBrush(gradient))

        gridsize = 20
        # really need to only draw within rect
        y0 = -250*gridsize
        x0 = -250*gridsize
        y1 = 250*gridsize
        x1 = 250*gridsize
        for y in range(500):
            painter.setPen(QtGui.QPen(QtGui.QColor(0,64,141), 1))
            painter.drawLine(x0, y0 + y*gridsize, x1, y0 + y*gridsize)
        for x in range(500):
            painter.setPen(QtGui.QPen(QtGui.QColor(0,64,141), 1))
            painter.drawLine(x0 + x*gridsize, y0, x0 + x*gridsize, y1)
        
        
    def addItem(self, item):
        if isinstance(item, PictoGlyph):
            self.glyphs.append(item)
        elif isinstance(item, PictoConnection):
            self.connections.append(item)
        super(PictoScene, self).addItem(item)
        
    def mousePressEvent(self,event):
        if self.parent().nodeSelector.currentItem() and self.parent().nodeSelector.currentItem().isSelected():
            selectedNodeType = self.parent().nodeSelector.currentItem().nodeClass
            e = PictoGlyph(event.scenePos(), selectedNodeType)
            self.addItem(e)
            self.parent().nodeSelector.clearSelection()
        else:
            # check if node was clicked or if anchor was clicked
            ilist = self.items(event.scenePos())
            anchorlist = [x for x in ilist if isinstance(x, PictoAnchor)]
            connectionList = [x for x in ilist if isinstance(x, PictoConnection)]
            if len(anchorlist) > 0:
                x = anchorlist[0]
                if self.activeAnchor:
                    self.connectAnchors(x, self.activeAnchor)
                    self.clearActiveAnchors()
                else:
                    self.clearActiveAnchors()
                    x.isActiveAnchor = True
                    x.update()
                    self.activeAnchor = x
                    #print(x.nodeKey)
            elif len(connectionList) > 0:
                x = connectionList[0]
                self.clearActiveConnections()
                x.isActiveConnection = True
                x.update()
                self.activeConnection = x
            else:
                self.clearActiveAnchors()
                self.clearActiveConnections()
                super(PictoScene, self).mousePressEvent(event)
                if len(self.selectedItems()) == 1:
                    self.parent().nodeEditor.update(self.selectedItems()[0].node)
                else:
                    self.parent().nodeEditor.clear()

    def clearActiveAnchors(self):
        self.activeAnchor = None
        for i in self.glyphs:
            i.clearActiveAnchors()
    def clearActiveConnections(self):
        self.activeConnection = None
        for c in self.connections:
            c.isActiveConnection = False
            c.update()
    
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
            

class PictoGlyph(QtWidgets.QGraphicsItem):
    def __init__(self, eventPos, nodeType):
        super(PictoGlyph, self).__init__()
        self.connections = []
        self.rect = QtCore.QRectF(0, 0, 60, 80)
        rect = self.rect
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        
        self.setPos(eventPos.x(), eventPos.y())
        self.node = nodeType()
        self.displayName = self.node.displayName
        self.node.set_auto_process(True)

        def anchorPoint(i):
            p = rect.topLeft()
            frac = (i+1)/(len(self.inputAnchorNames)+1)
            titleHeight = self.rect.height()/5
            dy = QtCore.QPointF(0, titleHeight + frac*(rect.height()-titleHeight))
            return p + dy

        self.inputAnchors = []
        self.inputAnchorNames = sorted(self.node._input_terminals.keys())
        for i, k in enumerate(self.inputAnchorNames):
            p = anchorPoint(i)
            self.inputAnchors.append(PictoAnchor(p,self,k))

        if self.node._has_output:
            titleHeight = self.rect.height()/5
            p3 = rect.topRight() + QtCore.QPointF(0, titleHeight + 0.5*(rect.height() - titleHeight))
            self.outputAnchor = PictoAnchor(p3, self, "output")

        self.backgroundColor = QtGui.QColor(10, 123, 255)
        self.highlightColor = QtGui.QColor(0, 44, 106)
    
    def removeConnection(self, connection):
        #self.connecttions = [c for c in self.connections if c is not connection]
        if connection in self.connections: self.connections.remove(connection)
        
    def removeConnections(self):
        clist = self.connections.copy()
        for c in clist:
            c.disconnect()
        return clist
    
    def addConnection(self, c):
        self.connections.append(c)
        #self.node.connect_input()

    def boundingRect(self):
        r = QtCore.QRectF(self.rect.topLeft(), self.rect.size())
        #r.adjust(-3,0,6,0);
        return r

    def paint(self, painter, opt, w):
        painter.setBrush(self.backgroundColor)
        painter.setPen(QtGui.QPen(self.highlightColor, 2))
        painter.drawRoundedRect(self.rect, 5, 5)
        
        painter.setPen(QtGui.QPen(self.highlightColor, 2))
        painter.setBrush(self.highlightColor)
        y = self.rect.height()/5
        painter.drawLine(0, y, self.rect.width(), y)
        painter.drawRoundedRect(0, 0, self.rect.width(), y, 5, 5)

        painter.setPen(QtGui.QPen(QtCore.Qt.white, 2))
        painter.drawText(self.boundingRect(), self.displayName)
        
        if self.isSelected():
            painter.setBrush(QtCore.Qt.NoBrush)
            painter.setPen(QtGui.QPen(QtCore.Qt.red, 2, QtCore.Qt.DashLine))
            painter.drawRect(self.boundingRect())

    
    def clearActiveAnchors(self):
        for i in self.inputAnchors:
            i.isActiveAnchor = False
            i.update()
        if self.node._has_output:
            self.outputAnchor.isActiveAnchor = False
            self.outputAnchor.update()
        
    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemPositionChange:
            for c in self.connections:
                c.updatePosition()
        return value

        
class PictoAnchor(QtWidgets.QGraphicsItem):
    def __init__(self,pos,parent,nodeKey, color= QtGui.QColor(0, 44, 106)):
        super(PictoAnchor, self).__init__(parent)
        self.backgroundColor = color
        self.size = 7
        self.upperLeft = QtCore.QPointF(-self.size/2, -self.size/2)
        self.isActiveAnchor = False
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setPos(pos)
        self.highlightColor = QtGui.QColor(0, 44, 106)
        self.nodeKey = nodeKey
        self.parent = parent
    
    def boundingRect(self):
        return QtCore.QRectF(self.upperLeft, QtCore.QSizeF(self.size+3,self.size+3))
    
    def paint(self, painter, opt, w):
        painter.setBrush(self.backgroundColor)
        painter.setPen(QtGui.QPen(self.highlightColor, 0))
        painter.drawRoundedRect(self.upperLeft.x(), self.upperLeft.y(), 
            self.size, self.size, 0,0)
        if self.isActiveAnchor:
            painter.setPen(QtGui.QPen(QtCore.Qt.red, 1, QtCore.Qt.SolidLine))
            painter.drawRect(self.boundingRect())
        
class PictoConnection(QtWidgets.QGraphicsItem):
    def __init__(self, startAnchor, endAnchor):
        super(PictoConnection, self).__init__()
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges, True)
        if startAnchor.nodeKey == 'output':
            self.startAnchor = startAnchor
            self.endAnchor = endAnchor        
        else:
            self.endAnchor = startAnchor
            self.startAnchor = endAnchor

        self.setPos(self.startAnchor.scenePos())
        self.isActiveConnection = False
        self.highlightColor = QtGui.QColor(0, 44, 106)

    def disconnect(self):
        # tell glyphs at start/end anchors to remove the connections
        self.startAnchor.parent.removeConnection(self)
        self.endAnchor.parent.removeConnection(self)
        
        # tell the underlying nodes to remove the connection
        #startNode = self.startAnchor.parent.node
        endNode = self.endAnchor.parent.node
        
        # don't need to disconnect_output. this is a
        # startNode.disconnect_output(endNode)
        theInputKey = self.endAnchor.nodeKey
        endNode.disconnect_input(theInputKey)

    def boundingRect(self):
        startingPoint = self.mapFromItem(self.startAnchor, 0, 0)
        finalPoint = self.mapFromItem(self.endAnchor, 0, 0)
        return QtCore.QRectF(startingPoint,
                QtCore.QSizeF(finalPoint.x() - startingPoint.x(),
                       finalPoint.y() - startingPoint.y())).normalized()
    
    def paint(self, painter, opt, w):
        path = QtGui.QPainterPath()
        startingPoint = self.mapFromItem(self.startAnchor, 0, 0)
        finalPoint = self.mapFromItem(self.endAnchor, 0, 0)
        x = ([startingPoint.x(), finalPoint.x()])
        y = ([startingPoint.y(), finalPoint.y()])
        path.moveTo(x[0], y[0])
        path.cubicTo(x[1], y[0],  # control point 1
                          x[0], y[1],  # control point 2
                          x[1], y[1])
        if self.isActiveConnection:
            painter.setPen(QtGui.QPen(QtCore.Qt.red, 2, QtCore.Qt.SolidLine))
        else:
            painter.setPen(QtGui.QPen(self.highlightColor, 2, QtCore.Qt.SolidLine))
        painter.drawPath(path)

    def updatePosition(self):
        self.prepareGeometryChange()


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

