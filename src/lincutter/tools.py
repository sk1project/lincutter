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

import os
import gtk

from lincutter import _, config
from lincutter import events, modes

class AppTools(gtk.VBox):

	def __init__(self, mw):
		gtk.VBox.__init__(self, False, 0)
		self.mw = mw
		self.app = mw.app
		self.actions = self.app.actions

		spacer = gtk.EventBox()
		spacer.set_size_request(10, 50)
		self.pack_start(spacer, False, False)

		items = [None,
				('select.png', 'SELECT_MODE', modes.SELECT_MODE),
				('fleur.png', 'FLEUR_MODE', modes.FLEUR_MODE),
				('zoom.png', 'ZOOM_MODE', modes.ZOOM_MODE),
				None,
			   ]

		for item in items:
			if item is None:
				self.pack_start(gtk.HSeparator(), False, False, 0)
			else:
				if len(item) == 3:
					icon_file = item[0]
					action = self.actions[item[1]]
				else:
					icon_file = item
					action = None
				icon_file = os.path.join(config.resource_dir,
										 'icons', 'tools', icon_file)
				icon = gtk.Image()
				icon.set_from_file(icon_file)
				if len(item) == 3:
					toolbutton = AppToggleButton(self.app, item[2], icon, action)
				else:
					toolbutton = AppToolButton(self.app, icon)
				self.pack_start(toolbutton, False, False, 0)

class AppToggleButton(gtk.ToggleToolButton):

	def __init__(self, app, mode, image, action):
		gtk.ToggleToolButton.__init__(self)
		self.app = app
		self.mode = mode
		self.action = action
		self.set_icon_widget(image)
		self.set_tooltip_text(self.action.tooltip)
		events.connect(events.MODE_CHANGED, self.check_mode)
		events.connect(events.DOC_CHANGED, self.check_mode)
		self.connect('toggled', self.toggle_changed)
		self.mode_flag = False

	def check_mode(self, *args):
		canvas = self.app.current_doc.canvas
		if canvas.mode == self.mode:
			self.mode_flag = True
			self.set_property('active', True)
		else:
			self.mode_flag = False
			self.set_property('active', False)

	def toggle_changed(self, *args):
		if self.mode_flag and not self.get_active():
			self.set_property('active', True)
		if self.get_active() and not self.mode_flag:
			self.action.activate()

class AppToolButton(gtk.ToolButton):

	def __init__(self, app, image, action=None):
		gtk.ToolButton.__init__(self, image)
		self.app = app
		self.action = action
		if not action is None:
			action.connect_proxy(self)




