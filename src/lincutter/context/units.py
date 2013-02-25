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

from uc2.uc2const import unit_names, unit_full_names

from lincutter import _, config, events

class UnitsPlugin(gtk.HBox):

	def __init__(self, mw):
		gtk.HBox.__init__(self)
		self.mw = mw
		self.app = mw.app
		self.actions = self.app.actions
		self.build()

	def build(self):
		label = gtk.Label(_('Units:'))
		self.pack_start(label, False, False, 3)

		self.combo = gtk.combo_box_new_text()
		self.pack_start(self.combo, False, False, 0)

		for item in unit_names:
			self.combo.append_text(unit_full_names[item])

		self.combo.set_active(unit_names.index(config.default_unit))
		self.combo.connect('changed', self.combo_changed)

		events.connect(events.NO_DOCS, self.set_state)
		events.connect(events.DOC_CHANGED, self.set_state)
		events.connect(events.CONFIG_MODIFIED, self.config_changed)

	def config_changed(self, *args):
		if not config.default_unit == unit_names[self.combo.get_active()]:
			self.combo.set_active(unit_names.index(config.default_unit))

	def combo_changed(self, *args):
		if not config.default_unit == unit_names[self.combo.get_active()]:
			config.default_unit = unit_names[self.combo.get_active()]
			self.combo.set_active(unit_names.index(config.default_unit))

	def set_state(self, *args):
		if self.app.current_doc is None:
			self.set_sensitive(False)
		else:
			self.set_sensitive(True)
