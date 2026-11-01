<h1 align="center">Maya Matrix Space Switch</h1>
<p align="center">
  <a href="https://www.autodesk.com/products/maya/overview"><img src="https://img.shields.io/badge/Maya-2025%2B-blue?logo=autodesk&logoColor=white" alt="Maya 2025+"></a>
  <a href="https://pypi.org/project/PySide6/"><img src="https://img.shields.io/badge/PySide6-Qt%20for%20Python-green?logo=qt&logoColor=white" alt="PySide6"></a>
  <img src="https://img.shields.io/badge/Maya%20API-2.0-lightgrey" alt="Maya API 2.0">
</p>
<br>

<h2>Installation</h2>

-----

Copy `SS_Core.py`, `SS_ui.py` and `SS_Undo.py` to your 📁`Documents/maya/scripts` directory

Then open the Script Editor in Maya and run this in a Python tab:

```python
import SS_ui
SS_ui.show_ui()
```

You can middle mouse drag those two lines onto a shelf to make a button for it.

> [!Note]
> The UI uses PySide6 so it needs Maya 2025 or newer. `SS_Undo.py` is a small plugin that gets loaded automatically the first time you build, you don't need to load it yourself.

-----

### Table of Contents
* [About](#about)
* [Instructions](#instructions)
* [How it works](#how-it-works)
* [Planned_Features](#planned_features)
* [Thanks](#thanks)

-----

### About

A small tool for setting up space switches with matrix nodes and offsetParentMatrix instead of parent constraints. Pick your spaces, pick a control, hit build and the control gets a Space attribute to switch between them. There's also a Switch button that matches the control so it doesn't pop when you change spaces.

> [!Note]
> I made this mainly to get comfortable with matrix rigging and the Maya Python API 2.0, so it's a learning project and not production ready. I learned a lot from the bugs along the way, more on that in [How it works](#how-it-works).

-----

### Instructions

* Building a space switch

> Select the objects you want as spaces (root, hips, chest etc.) and click *Add Selected*. The first one in the list is the default space. Then select your control, click `<<` and hit *Build Space Switch*. The control shouldn't move when it's built.

<br>

* Switching spaces

> Pick a space from the dropdown and click *Switch*. The control stays where it is and its translate/rotate gets changed to make up for the new space, so there's no pop.
> You can still change the Space attribute in the channel box, but the control will jump if the spaces have moved apart since the build.

<br>

* Keying the switch

> Tick *Key* before clicking *Switch* if you're animating. It keys the frame before in the old space and the current frame in the new one.
> You can also call it from a script: `SS_Core.match_switch("hand_ctrl", 1, key=True)`

<br>

-----

### How it works

Each space gets a multMatrix node:

`offset * space.worldMatrix * (control's parent).worldInverseMatrix`

They all plug into a choice node, the Space attribute is the selector and the choice output drives the control's offsetParentMatrix. The offset is worked out at build time so the control stays put.

Some things I learned making it:
* Matrix order really matters. I had the offset backwards at first and the control went twice as far as it should.
* My first fix for the control's parent used its own parentInverseMatrix, but that already includes offsetParentMatrix so it looped back into itself and the control drifted after a few switches. Using the parent's worldInverseMatrix fixed it.
* MDGModifier doesn't do anything until doIt(), so you can't findPlug an attribute you just added before calling it.
* MDGModifier changes also don't go on Maya's undo queue by themselves. To get Ctrl+z working I had to write a small MPxCommand (`SS_Undo.py`) that holds onto the modifier and calls its undoIt/doIt.

-----

### Planned_Features

* Locked channels
> If the control's translate/rotate are locked, Switch can't match it and the control still pops.

* Proper node names
> Nodes are just called choice1, multMatrix1 etc. I want to name them after the control.

* Removing a space switch
> A button to delete the network and the Space attribute.

* Switching over a frame range
> Match and key a switch across a whole range instead of one frame at a time.

* Drag and Drop Installer
> Ease of use drag and drop installer to avoid having to manually place files.

<br>

-----

### Thanks
Thanks for reading this far and giving the tool a go. If you run into any issues or have any suggestions please don't hesitate to reach out to me on LinkedIn
