import numpy as np
from qtpy import QtCore, QtWidgets

from imswitch.imcontrol.view import guitools
from .basewidgets import NapariHybridWidget


class ULensesWidget(NapariHybridWidget):
    """ Alignment widget that shows a grid of points on top of the image in the viewbox."""

    sigULensesClicked = QtCore.Signal()
    sigUShowLensesChanged = QtCore.Signal(bool)  # (enabled)

    def __post_init__(self):
        # Graphical Elements
        self.ulensesButton = guitools.BetterPushButton('uLenses')
        self.xEdit = QtWidgets.QLineEdit('0')
        self.yEdit = QtWidgets.QLineEdit('0')
        self.pxEdit = QtWidgets.QLineEdit('157.5')
        self.upEdit = QtWidgets.QLineEdit('1182')
        
        # Add elements to GridLayout
        ulensesLayout = QtWidgets.QGridLayout()
        self.setLayout(ulensesLayout)
        ulensesLayout.addWidget(QtWidgets.QLabel('Pixel Size'), 0, 0)
        ulensesLayout.addWidget(self.pxEdit, 0, 1)
        ulensesLayout.addWidget(QtWidgets.QLabel('Periodicity'), 1, 0)
        ulensesLayout.addWidget(self.upEdit, 1, 1)
        ulensesLayout.addWidget(QtWidgets.QLabel('X offset'), 2, 0)
        ulensesLayout.addWidget(self.xEdit, 2, 1)
        ulensesLayout.addWidget(QtWidgets.QLabel('Y offset'), 3, 0)
        ulensesLayout.addWidget(self.yEdit, 3, 1)
        ulensesLayout.addWidget(self.ulensesButton, 4, 0)

        # Connect signals
        self.ulensesButton.clicked.connect(self.sigULensesClicked)

    def getParameters(self):
        """ Returns the X offset, Y offset, pixel size, and periodicity
        parameters respectively set by the user."""
        return (np.float(self.xEdit.text()),
                np.float(self.yEdit.text()),
                np.float(self.pxEdit.text()),
                np.float(self.upEdit.text()))

# Copyright (C) 2020, 2021 TestaLab
# This file is part of ImSwitch.
#
# ImSwitch is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ImSwitch is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
