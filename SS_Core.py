import maya.api.OpenMaya as om

#trace DagPath for an object
def get_dag_path(obj):
    selection = om.MSelectionList()
    selection.add(obj)
    return selection.getDagPath(0)

#calculate offset between the space and ctrl
def calculate_space_offset(space, ctrl):
    space_dag = get_dag_path(space)
    ctrl_dag = get_dag_path(ctrl)

    space_mtx = space_dag.inclusiveMatrix()
    ctrl_par_inv = ctrl_dag.exclusiveMatrixInverse()

    return space_mtx * ctrl_par_inv

#Set up space switch with choice node
def build_space_switch(spaces, ctrl, attr_name="space"):
    if not spaces:
        return

    ctrl_path = get_dag_path(ctrl)
    ctrl_node = om.MFnDependencyNode(ctrl_path.node())

    mod = om.MDGModifier()

    enum_attr = om.MFnEnumAttribute()
    space_enum = enum_attr.create(attr_name, attr_name, 0)

    for i in range(len(spaces)):
        enum_attr.addField(spaces[i], i)

    mod.addAttribute(ctrl_path.node(), space_enum)

    choice = mod.createNode("choice")
    choice_nd = om.MFnDependencyNode(choice)

    mod.connect(
        ctrl_node.findPlug(attr_name, False),
        choice_nd.findPlug("selector", False)
    )

    for i in range(len(spaces)):
        space = spaces[i]

        mult = mod.createNode("multMatrix")
        mult_node = om.MFnDependencyNode(mult)

        offset = calculate_space_offset(space, ctrl)
        offset_obj = om.MFnMatrixData().create(offset)

        mult_node.findPlug("matrixIn", False).elementByLogicalIndex(0).setMObject(offset_obj)

        space_path = get_dag_path(space)
        space_node = om.MFnDependencyNode(space_path.node())

        mod.connect(
            space_node.findPlug("worldMatrix", False).elementByLogicalIndex(0),
            mult_node.findPlug("matrixIn", False).elementByLogicalIndex(1)
        )

        mod.connect(
            mult_node.findPlug("matrixSum", False),
            choice_nd.findPlug("input", False).elementByLogicalIndex(i)
        )

    mod.connect(
        choice_nd.findPlug("output", False),
        ctrl_node.findPlug("offsetParentMatrix", False)
    )

    mod.doIt()