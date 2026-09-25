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
    ctrl_fn = om.MFnDependencyNode(ctrl_path.node())

    enum_fn = om.MFnEnumAttribute()
    space_attr = enum_fn.create(attr_name, attr_name, 0)

    for i, space in enumerate(spaces):
        enum_fn.addField(space, i)

    mod = om.MDGModifier()
    mod.addAttribute(ctrl_path.node(), space_attr)

    choice_node = mod.createNode("choice")
    choice_fn = om.MFnDependencyNode(choice_node)

    mod.connect(
        ctrl_fn.findPlug(attr_name, False),
        choice_fn.findPlug("selector", False)
    )

    for i, space in enumerate(spaces):
        mult_node = mod.createNode("multMatrix")
        mult_fn = om.MFnDependencyNode(mult_node)

        offset_mtx = calculate_space_offset(space, ctrl)
        offset_data = om.MFnMatrixData().create(offset_mtx)

        matrix_in = mult_fn.findPlug("matrixIn", False)
        matrix_in.elementByLogicalIndex(0).setMObject(offset_data)

        space_path = get_dag_path(space)
        space_fn = om.MFnDependencyNode(space_path.node())

        mod.connect(
            space_fn.findPlug("worldMatrix", False).elementByLogicalIndex(0),
            matrix_in.elementByLogicalIndex(1)
        )

        mod.connect(
            mult_fn.findPlug("matrixSum", False),
            choice_fn.findPlug("input", False).elementByLogicalIndex(i)
        )

    mod.connect(
        choice_fn.findPlug("output", False),
        ctrl_fn.findPlug("offsetParentMatrix", False)
    )

    mod.doIt()