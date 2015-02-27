import sys
import pyqtgraph as pg
import heka

app = pg.mkQApp()

win = pg.QtGui.QWidget()
layout = pg.QtGui.QGridLayout()
win.setLayout(layout)
hsplit = pg.QtGui.QSplitter(pg.QtCore.Qt.Horizontal)
layout.addWidget(hsplit, 0, 0)

vsplit = pg.QtGui.QSplitter(pg.QtCore.Qt.Vertical)
hsplit.addWidget(vsplit)

tree = pg.QtGui.QTreeWidget()
tree.setHeaderLabels(['Node', 'Label'])
tree.setColumnWidth(0, 200)
vsplit.addWidget(tree)

data_tree = pg.DataTreeWidget()
vsplit.addWidget(data_tree)

plot = pg.PlotWidget()
hsplit.addWidget(plot)

hsplit.setStretchFactor(0, 400)
hsplit.setStretchFactor(1, 600)
win.resize(1200, 800)
win.show()

def load(file_name):
    global bundle, tree_items
    bundle = heka.Bundle(file_name)
    tree.clear()
    
    update_tree(tree.invisibleRootItem(), [])
    replot()
    
def update_tree(root_item, index):
    global bundle
    root = bundle.pul
    node = root
    for i in index:
        node = node[i]
    node_type = node.__class__.__name__
    if node_type.endswith('Record'):
        node_type = node_type[:-6]
    try:
        node_type += str(getattr(node, node_type + 'Count'))
    except AttributeError:
        pass
    try:
        node_label = node.Label
    except AttributeError:
        node_label = ''
    item = pg.QtGui.QTreeWidgetItem([node_type, node_label])
    root_item.addChild(item)
    item.node = node
    item.index = index
    if len(index) < 2:
        item.setExpanded(True)
    for i in range(len(node.children)):
        update_tree(item, index + [i])

def replot():
    plot.clear()
    data_tree.clear()
    
    selected = tree.selectedItems()
    if len(selected) < 1:
        return
    
    # update data tree
    sel = selected[0]
    fields = sel.node.get_fields()
    data_tree.setData(fields)
    
    # plot all selected
    for sel in selected:
        index = sel.index
        if len(index) < 4:
            return
        
        trace = sel.node
        plot.setLabels(bottom=('Time', 's'), left=(trace.Label, trace.YUnit))
        plot.plot(bundle.data[index])
    
tree.itemSelectionChanged.connect(replot)

load('DemoV9Bundle.dat')


if sys.flags.interactive == 0:
    app.exec_()
    