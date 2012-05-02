# -*- coding: utf-8 -*-
#
#	Copyright (C) 2011-2012 by Igor E. Novikov
#	
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#	
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#	
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>.

import gtk

from lincutter.context.units import UnitsPlugin
from lincutter.context.transform import RotatePlugin, MirrorPlugin, \
					MiscPlugin, ResizePlugin, GroupPlugin, PathsPlugin

class ContextPanel(gtk.VBox):

	def __init__(self, mw):
		gtk.VBox.__init__(self)
		self.mw = mw
		self.app = mw.app
		self.actions = self.app.actions

		self.hbox = gtk.HBox()
		self.pack_start(self.hbox, True, True, 1)

		line = gtk.HSeparator()
		self.pack_start(line, True, False)

		self.plugins = [UnitsPlugin, ResizePlugin, GroupPlugin, PathsPlugin,
					RotatePlugin, MirrorPlugin, MiscPlugin, ]

		self.init_plugins()

		self.show_all()

	def init_plugins(self):
		for item in self.plugins:
			if self.plugins.index(item):
				sep = gtk.VSeparator()
				self.hbox.pack_start(sep, False, False, 5)
			item = item(self.mw)
			self.hbox.pack_start(item, False, False)


