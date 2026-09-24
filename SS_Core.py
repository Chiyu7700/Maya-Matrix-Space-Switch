import maya.api.OpenMaya as om

#trace DagPath for an object
def get_dag_path(node_name):
    selection = om.MSelectionList()
    selection.add(node_name)
    return selection.getDagPath(0)

#calculate offset between the leader and follower
def calculate_offset_offset(leader, follower):
    leader_dag = get_dag_path(leader)
    follower_dag = get_dag_path(follower)

    leader_mtx = leader_dag.inclusiveMatrix()
    follower_inv = follower_dag.exclusiveMatrixInverse()

    return leader_mtx * follower_inv