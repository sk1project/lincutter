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
from lincutter.plotters import plt_data
from lincutter.widgets import UnitSpin, UnitLabel

class PlotterTab(gtk.VBox):

	name = "Plotter Setup"
	caption = _("Plotter Setup")
	caption_label = None


	def __init__(self, app):

		gtk.VBox.__init__(self)
		self.app = app
		self.caption_label = gtk.Label(self.caption)

		spacer = gtk.VBox()
		self.add(spacer)
		self.set_border_width(15)
		self.set_size_request(385, 220)

		tab = gtk.Table(3, 2, False)
		tab.set_row_spacings(10)
		tab.set_col_spacings(10)
		spacer.add(tab)


		#---------------------------

		label = gtk.Label(_('Plotter model:'))
		label.set_alignment(0, 0.5)
		tab.attach(label, 0, 1, 0, 1, gtk.FILL | gtk.EXPAND, gtk.SHRINK)

		self.combo = gtk.combo_box_new_text()
		self.combo.connect('changed', self.combo_changed)

		items = plt_data.keys()
		items.sort()
		for item in items:
			self.combo.append_text(item)

		tab.attach(self.combo, 1, 2, 0, 1, gtk.SHRINK, gtk.SHRINK)

		#---------------------------

		self.radiobut1 = gtk.RadioButton(None, _("Predefined model"))
		tab.attach(self.radiobut1, 0, 1, 1, 2, gtk.SHRINK, gtk.SHRINK)
		self.radiobut1.connect("toggled", self.radio_changed)

		self.radiobut2 = gtk.RadioButton(self.radiobut1, _("Custom model"))
		tab.attach(self.radiobut2, 1, 2, 1, 2, gtk.SHRINK, gtk.SHRINK)
		self.radiobut2.connect("toggled", self.radio_changed)

		#---------------------------

		self.data_frame = gtk.Frame(_('Plotter data'))
		tab.attach(self.data_frame, 0, 2, 2, 3, gtk.FILL | gtk.EXPAND, gtk.SHRINK)


		data_tab = gtk.Table(3, 3, False)
		data_tab.set_border_width(15)
		data_tab.set_row_spacings(10)
		data_tab.set_col_spacings(10)
		self.data_frame.add(data_tab)

		#===========================

		label = gtk.Label(_('Plotter model:'))
		label.set_alignment(1, 0.5)
		data_tab.attach(label, 0, 1, 0, 1, gtk.FILL , gtk.SHRINK)

		self.plt_name = gtk.Entry()
		self.plt_name.set_text(config.plotter_name)
		data_tab.attach(self.plt_name, 1, 3, 0, 1, gtk.FILL | gtk.EXPAND, gtk.SHRINK)

		#===========================

		label = gtk.Label(_('Cutting width:'))
		label.set_alignment(1, 0.5)
		data_tab.attach(label, 0, 1, 1, 2, gtk.FILL , gtk.SHRINK)

		self.height_spin = UnitSpin(self.user_changes)
		self.height_spin.set_point_value(config.plotter_page_height)
		data_tab.attach(self.height_spin, 1, 2, 1, 2, gtk.SHRINK, gtk.SHRINK)

		unit_label = UnitLabel()
		unit_label.set_alignment(0, 0.5)
		data_tab.attach(unit_label, 2, 3, 1, 2, gtk.FILL | gtk.EXPAND, gtk.SHRINK)

		#===========================		
		label = gtk.Label(_('Cutting length:'))
		label.set_alignment(1, 0.5)

		data_tab.attach(label, 0, 1, 2, 3, gtk.FILL , gtk.SHRINK)

		self.width_spin = UnitSpin(self.user_changes)
		self.width_spin.set_point_value(config.plotter_page_width)
		data_tab.attach(self.width_spin, 1, 2, 2, 3, gtk.SHRINK, gtk.SHRINK)

		unit_label = UnitLabel()
		unit_label.set_alignment(0, 0.5)
		data_tab.attach(unit_label, 2, 3, 2, 3, gtk.FILL | gtk.EXPAND, gtk.SHRINK)

		#===========================

		if config.plotter_name in items and \
		round(plt_data[config.plotter_name][0], 6) == round(config.plotter_page_height, 6) and \
		round(plt_data[config.plotter_name][1], 6) == round(config.plotter_page_width, 6):
			self.combo.set_active(items.index(config.plotter_name))
			self.radiobut1.set_active(True)
			self.data_frame.set_sensitive(False)
		else:
			self.radiobut2.set_active(True)

	def user_changes(self, *args):pass

	def radio_changed(self, *args):
		if self.radiobut1.get_active():
			self.combo_changed()
		else:
			self.data_frame.set_sensitive(True)

	def combo_changed(self, *args):
		items = plt_data.keys()
		items.sort()
		index = self.combo.get_active()
		if index == -1:
			index = items.index('Generic plotter')
			self.combo.set_active(index)
		value = items[index]
		self.plt_name.set_text(value)
		self.height_spin.set_point_value(plt_data[value][0])
		self.width_spin.set_point_value(plt_data[value][1])
		self.radiobut1.set_active(True)
		self.data_frame.set_sensitive(False)

	def do_apply(self):
		config.plotter_name = self.plt_name.get_text()
		config.plotter_page_height = self.height_spin.get_point_value()
		config.plotter_page_width = self.width_spin.get_point_value()
