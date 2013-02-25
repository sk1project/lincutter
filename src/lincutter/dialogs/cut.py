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

from lincutter import _, config, icons


def get_cut_dialog(app):

	parent = app.mw
	title = _('Cutting')

	dialog = gtk.Dialog(title, parent,
	                   gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)

	dialog.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT)
	cut_button = dialog.add_button(icons.STOCK_CUTTING, gtk.RESPONSE_ACCEPT)

	cut_panel = CuttingPanel(app, cut_button)
	cut_panel.set_border_width(5)
	cut_panel.show_all()

	dialog.vbox.pack_start(cut_panel)

	ret = dialog.run()
	if ret == gtk.RESPONSE_ACCEPT:
		cut_panel.do_apply()
	dialog.destroy()
	return ret


class CuttingPanel(gtk.VBox):

	def __init__(self, app, button):
		gtk.VBox.__init__(self)
		self.button = button
		self.app = app
		self.build()

	def build(self):
		self.set_size_request(385, 200)

		tab = gtk.Table(7, 2, False)
		tab.set_row_spacings(10)
		tab.set_col_spacings(10)
		self.pack_start(tab)

		#---------------------------

		label = gtk.Label(_('Plotter:'))
		label.set_alignment(1, 0.5)
		tab.attach(label, 0, 1, 0, 1, gtk.FILL, gtk.SHRINK)


		label = gtk.Label()
		markup = '<b>' + config.plotter_name + '</b>'
		label.set_markup(markup)
		label.set_alignment(0, 0.5)
		tab.attach(label, 1, 2, 0, 1, gtk.FILL | gtk.EXPAND, gtk.SHRINK)

		#---------------------------

		check = gtk.CheckButton(label=_('Output to file'))
		check.set_active(True)
		check.set_sensitive(False)
		tab.attach(check, 0, 1, 1, 2, gtk.FILL, gtk.SHRINK)

		self.output_file = gtk.FileChooserButton(_('Select file for output'))
		filename = os.path.expanduser(config.output_file)
		if not os.path.lexists(filename):
			file = open(filename, 'wb')
			file.close()
		self.output_file.set_filename(filename)
		self.output_file.connect('file-set', self.combo_changed)
		tab.attach(self.output_file, 1, 2, 1, 2, gtk.FILL | gtk.EXPAND, gtk.SHRINK)

		#---------------------------

		self.bbox = gtk.CheckButton(label=_('Cut bounding box'))
		self.bbox.set_active(config.cut_bbox)
		tab.attach(self.bbox, 0, 2, 2, 3, gtk.FILL | gtk.EXPAND, gtk.SHRINK)

		#---------------------------
		hline = gtk.HSeparator()
		tab.attach(hline, 0, 2, 3, 4, gtk.FILL | gtk.EXPAND, gtk.SHRINK)
		#---------------------------

		label = gtk.Label(_('Flattening tolerance:'))
		label.set_alignment(0, 0.5)
		tab.attach(label, 0, 1, 4, 5, gtk.FILL , gtk.SHRINK)

		self.tolerance_adj = gtk.Adjustment(config.tolerance,
										0.01, 10.0, 0.01, 1.0, 0.0)
		spinner = gtk.SpinButton(self.tolerance_adj, 0.1, 2)
		spinner.set_numeric(True)
		hbox = gtk.HBox()
		hbox.pack_start(spinner, False)
		tab.attach(hbox, 1, 2, 4, 5, gtk.FILL, gtk.SHRINK)

		markup = _('Flattening tolerance affects on curve flattening quality.\n\
Lower value means better cutting quality and slower cutting speed.\n\
Default flattening tolerance value is 0,5')
		label = gtk.Label()
		label.set_markup(markup)
		label.set_alignment(0, 0.5)
		label.set_sensitive(False)
		tab.attach(label, 0, 2, 5, 6, gtk.FILL | gtk.EXPAND, gtk.SHRINK)

		#---------------------------

	def combo_changed(self, *args):
		if self.output_file.get_filename() is None:
			self.button.set_sensitive(False)
		else:
			self.button.set_sensitive(True)

	def do_apply(self):
		config.output_file = self.output_file.get_filename()
		config.tolerance = self.tolerance_adj.get_value()
		config.cut_bbox = self.bbox.get_active()
