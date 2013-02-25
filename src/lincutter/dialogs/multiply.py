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
from lincutter.widgets import UnitSpin, UnitLabel

def multiply_dialog(parent):

	result = []

	caption = _("Multiply selection")
	dialog = gtk.Dialog(caption, parent,
						gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
						(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
						gtk.STOCK_OK, gtk.RESPONSE_OK))
	dialog.set_icon(parent.get_icon())
	dialog.set_default_size(200, 300)
	dialog.set_resizable(False)

	vbox = gtk.VBox(False, 5)
	vbox.set_border_width(5)
	dialog.vbox.pack_start(vbox, 15)

	#=========QUANTITY======================

	frame1 = gtk.Frame(' Quantity ')
	frame1.set_border_width(5)

	tab1 = gtk.Table(2, 3, False)
	tab1.set_row_spacings(10)
	tab1.set_col_spacings(10)
	tab1.set_border_width(5)

	#--------------------------

	label = gtk.Label(_('Horizontal:'))
	label.set_alignment(0, 0.5)
	tab1.attach(label, 0, 1, 0, 1, gtk.FILL | gtk.EXPAND, gtk.SHRINK)

	hu_adj = gtk.Adjustment(1.0, 1.0, 1000.0, 1.0, 1.0, 0.0)
	spinner = gtk.SpinButton(hu_adj, 0, 0)
	spinner.set_numeric(True)
	tab1.attach(spinner, 1, 2, 0, 1, gtk.FILL | gtk.EXPAND, gtk.SHRINK)

	label = gtk.Label(_('units'))
	label.set_alignment(0, 0.5)
	tab1.attach(label, 2, 3, 0, 1, gtk.FILL , gtk.SHRINK)

	#--------------------------

	label = gtk.Label(_('Vertical:'))
	label.set_alignment(0, 0.5)
	tab1.attach(label, 0, 1, 1, 2, gtk.FILL | gtk.EXPAND, gtk.SHRINK)

	vu_adj = gtk.Adjustment(1.0, 1.0, 1000.0, 1.0, 1.0, 0.0)
	spinner = gtk.SpinButton(vu_adj, 0, 0)
	spinner.set_numeric(True)
	tab1.attach(spinner, 1, 2, 1, 2, gtk.FILL | gtk.EXPAND, gtk.SHRINK)

	label = gtk.Label(_('units'))
	label.set_alignment(0, 0.5)
	tab1.attach(label, 2, 3, 1, 2, gtk.FILL , gtk.SHRINK)



	frame1.add(tab1)
	vbox.pack_start(frame1, 5)

	#===========SPACING====================

	def callback():pass

	frame2 = gtk.Frame(' Spacing ')
	frame2.set_border_width(5)

	tab2 = gtk.Table(2, 3, False)
	tab2.set_row_spacings(10)
	tab2.set_col_spacings(10)
	tab2.set_border_width(5)

	#--------------------------

	label = gtk.Label(_('Horizontal:'))
	label.set_alignment(0, 0.5)
	tab2.attach(label, 0, 1, 0, 1, gtk.FILL | gtk.EXPAND, gtk.SHRINK)

	h_spinner = UnitSpin(callback)
	tab2.attach(h_spinner, 1, 2, 0, 1, gtk.FILL | gtk.EXPAND, gtk.SHRINK)

	label = UnitLabel()
	label.set_alignment(0, 0.5)
	tab2.attach(label, 2, 3, 0, 1, gtk.FILL , gtk.SHRINK)

	#--------------------------

	label = gtk.Label(_('Vertical:'))
	label.set_alignment(0, 0.5)
	tab2.attach(label, 0, 1, 1, 2, gtk.FILL | gtk.EXPAND, gtk.SHRINK)

	v_spinner = UnitSpin(callback)
	tab2.attach(v_spinner, 1, 2, 1, 2, gtk.FILL | gtk.EXPAND, gtk.SHRINK)

	label = UnitLabel()
	label.set_alignment(0, 0.5)
	tab2.attach(label, 2, 3, 1, 2, gtk.FILL , gtk.SHRINK)




	frame2.add(tab2)
	vbox.pack_start(frame2, 5)

	#===============================

	dialog.show_all()
	ret = dialog.run()

	if ret == gtk.RESPONSE_OK:
		result = [int(hu_adj.get_value()), int(vu_adj.get_value()),
				h_spinner.get_point_value(), v_spinner.get_point_value()]

	dialog.destroy()
	return result
