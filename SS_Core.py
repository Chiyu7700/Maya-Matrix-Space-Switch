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

    #ctrl world matrix without its own channels (offsetParentMatrix * parent)
    ctrl_local = om.MFnTransform(ctrl_dag).transformation().asMatrix()
    ctrl_no_local = ctrl_local.inverse() * ctrl_dag.inclusiveMatrix()

    #offset is the ctrl relative to the space
    return ctrl_no_local * space_dag.inclusiveMatrixInverse()

#Set up space switch with choice node
def build_space_switch(spaces, ctrl, attr_name="space"):
    if not spaces:
        return

    ctrl_path = get_dag_path(ctrl)
    ctrl_fn = om.MFnDependencyNode(ctrl_path.node())

    #ctrl's parentInverseMatrix already has offsetParentMatrix in it (loops back), use the parent's own one
    parent_inv_plug = None
    if ctrl_path.length() > 1:
        parent_path = om.MDagPath(ctrl_path)
        parent_path.pop()
        parent_fn = om.MFnDependencyNode(parent_path.node())
        parent_inv_plug = parent_fn.findPlug("worldInverseMatrix", False).elementByLogicalIndex(0)

    enum_fn = om.MFnEnumAttribute()
    space_attr = enum_fn.create(attr_name, attr_name, 0)
    enum_fn.keyable = True

    for i, space in enumerate(spaces):
        enum_fn.addField(space, i)

    mod = om.MDGModifier()
    mod.addAttribute(ctrl_path.node(), space_attr)
    #attr only exists after doIt, need it before findPlug
    mod.doIt()

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

        #cancel out the ctrl's parent so it isn't applied twice (nothing to cancel if ctrl is under world)
        if parent_inv_plug is not None:
            mod.connect(parent_inv_plug, matrix_in.elementByLogicalIndex(2))

        mod.connect(
            mult_fn.findPlug("matrixSum", False),
            choice_fn.findPlug("input", False).elementByLogicalIndex(i)
        )

    mod.connect(
        choice_fn.findPlug("output", False),
        ctrl_fn.findPlug("offsetParentMatrix", False)
    )

    mod.doIt()