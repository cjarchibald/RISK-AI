"""Just start up the game"""

"""This is a risk game, playable over the internet.
Copyright (C) 2004 John Bauman

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
"""

import sys

from gui import riskgui
from gui import riskengine

try:
    import psyco #can't hurt - speeds up AI for autogames
    psyco.full()
except:
    pass #too bad

__version__ = "0.7.1"

if len(sys.argv) > 1 and sys.argv[1] == "-d":
    riskengine.debugging = 1

riskengine.setupdebugging()
riskengine.openworldfile("world.zip")
riskengine.loadterritories()
riskgui.setupdata()
riskgui.rungame()

