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

from lincutter import _, config
from lincutter.dialogs.prefs.general import GeneralTab
from lincutter.dialogs.prefs.colorstab import ColorsTab
from lincutter.dialogs.prefs.pltsetup import PlotterTab

def get_prefs_dialog(app, page=0):

	parent = app.mw
	title = _('%s Preferences') % (app.appdata.app_name)

	dialog = gtk.Dialog(title, parent,
	                   gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
	                   (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
	                    gtk.STOCK_APPLY, gtk.RESPONSE_ACCEPT))


	vbox = gtk.VBox()

	nb = PrefsNotebook(app)
	nb.set_property('scrollable', True)
	nb.set_tab_pos(gtk.POS_TOP)
	nb.show_all()
	nb.set_current_page(page)

	vbox.set_border_width(5)
	vbox.pack_start(nb)

	vbox.show_all()

	dialog.vbox.pack_start(vbox)

	ret = dialog.run()
	if ret == gtk.RESPONSE_ACCEPT:
		nb.run_apply()
		app.proxy.force_redraw()
	dialog.destroy()

class PrefsNotebook(gtk.Notebook):

	def __init__(self, app):
		self.app = app
		gtk.Notebook.__init__(self)

		self.generaltab = GeneralTab(self.app)
		self.append_page(self.generaltab, self.generaltab.caption_label)

		self.colorstab = ColorsTab(self.app)
		self.append_page(self.colorstab, self.colorstab.caption_label)

		self.plttab = PlotterTab(self.app)
		self.append_page(self.plttab, self.plttab.caption_label)

		self.widgets = [self.generaltab, self.colorstab, self.plttab]


	def run_apply(self):
		for widget in self.widgets:
			widget.do_apply()



