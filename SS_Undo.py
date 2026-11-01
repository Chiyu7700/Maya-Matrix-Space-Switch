import maya.api.OpenMaya as om

#tells maya this plugin uses api 2.0
def maya_useNewAPI():
    pass

#MDGModifier changes don't go on the undo queue by themselves, they need a command
#SS_Core runs the modifier, stores it in SS_Core.pending_mod then calls this command so ctrl+z can undo it
class UndoableModCmd(om.MPxCommand):
    name = "ssUndoableMod"

    def __init__(self):
        super().__init__()
        self.mod = None

    def doIt(self, args):
        import SS_Core
        self.mod = SS_Core.pending_mod
        SS_Core.pending_mod = None

    def undoIt(self):
        self.mod.undoIt()

    def redoIt(self):
        self.mod.doIt()

    def isUndoable(self):
        return True

def initializePlugin(plugin):
    om.MFnPlugin(plugin).registerCommand(UndoableModCmd.name, UndoableModCmd)

def uninitializePlugin(plugin):
    om.MFnPlugin(plugin).deregisterCommand(UndoableModCmd.name)
