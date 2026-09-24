import maya.api.OpenMaya as om

#selection = om.MSelectionList()
sl = om.MGlobal.getActiveSelectionList()
sl_path = sl.getDagPath(0)

print(sl_path.fullPathName())
print(sl_path.exclusiveMatrixInverse(), 'asibe happy')

sl_world_matrix = sl_path.inclusiveMatrix()

print(sl_world_matrix)