# -*- coding: utf-8 -*-
#
#	Copyright (C) 2012 by Igor E. Novikov
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

from lincutter import _, config

class GeneralTab(gtk.VBox):

	name = "General Options"
	caption = _("General Options")
	caption_label = None


	def __init__(self, app):

		gtk.VBox.__init__(self)
		self.app = app
		self.caption_label = gtk.Label(self.caption)

		spacer = gtk.VBox()
		self.add(spacer)
		self.set_border_width(15)
		self.set_size_request(500, 200)

		tab = gtk.Table(8, 2, False)
		tab.set_row_spacings(10)
		tab.set_col_spacings(10)
		spacer.pack_start(tab)

		#---------------------------

		label = gtk.Label(_('Application units:'))
		label.set_alignment(0, 0.5)
		tab.attach(label, 0, 1, 0, 1, gtk.FILL | gtk.EXPAND, gtk.SHRINK)

		self.combo = gtk.combo_box_new_text()

		for item in unit_names:
			self.combo.append_text(unit_full_names[item])

		self.combo.set_active(unit_names.index(config.default_unit))
		tab.attach(self.combo, 1, 2, 0, 1, gtk.SHRINK, gtk.SHRINK)


		#---------------------------
		hline = gtk.HSeparator()
		tab.attach(hline, 0, 2, 1, 2, gtk.FILL | gtk.EXPAND, gtk.SHRINK)
		#---------------------------

		label = gtk.Label(_('Curves flattening tolerance:'))
		label.set_alignment(0, 0.5)
		tab.attach(label, 0, 1, 2, 3, gtk.FILL | gtk.EXPAND, gtk.SHRINK)

		self.tolerance_adj = gtk.Adjustment(config.tolerance,
										0.01, 10.0, 0.01, 1.0, 0.0)
		spinner = gtk.SpinButton(self.tolerance_adj, 0.1, 2)
		spinner.set_numeric(True)
		tab.attach(spinner, 1, 2, 2, 3, gtk.FILL, gtk.SHRINK)

		markup = _('Flattening tolerance affects on curve flattening quality.\n\
Lower value means better cutting quality and slower cutting speed.\n\
Default flattening tolerance value is 0,5')
		label = gtk.Label()
		label.set_markup(markup)
		label.set_alignment(0, 0.5)
		label.set_sensitive(False)
		tab.attach(label, 0, 2, 3, 4, gtk.FILL | gtk.EXPAND, gtk.SHRINK)

		#---------------------------
		hline = gtk.HSeparator()
		tab.attach(hline, 0, 2, 4, 5, gtk.FILL | gtk.EXPAND, gtk.SHRINK)
		#---------------------------

		self.new_doc = gtk.CheckButton(label=_('Create new document on start'))
		self.new_doc.set_active(config.new_doc_on_start)
		tab.attach(self.new_doc, 0, 2, 5, 6, gtk.FILL | gtk.EXPAND, gtk.SHRINK)
		#---------------------------

		self.backup_check = gtk.CheckButton(label=_('Make backup when save'))
		self.backup_check.set_active(config.make_backup)
		tab.attach(self.backup_check, 0, 2, 6, 7, gtk.FILL | gtk.EXPAND, gtk.SHRINK)
		#---------------------------

		self.release_check = gtk.CheckButton(label=_('Allow release check'))
		self.release_check.set_active(config.allow_release_check)
		tab.attach(self.release_check, 0, 2, 7, 8, gtk.FILL | gtk.EXPAND, gtk.SHRINK)


	def do_apply(self):
		config.new_doc_on_start = self.new_doc.get_active()
		config.allow_release_check = self.release_check.get_active()
		config.make_backup = self.backup_check.get_active()
		config.tolerance = self.tolerance_adj.get_value()
		config.default_unit = unit_names[self.combo.get_active()]
