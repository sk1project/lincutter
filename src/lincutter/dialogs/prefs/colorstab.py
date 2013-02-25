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

from uc2.cms import rgb_to_hexcolor, gdk_hexcolor_to_rgb

from lincutter import _, config

class ColorsTab(gtk.VBox):

	name = "Canvas Colors"
	caption = _("Canvas Colors")
	caption_label = None


	def __init__(self, app):

		gtk.VBox.__init__(self)
		self.app = app
		self.caption_label = gtk.Label(self.caption)

		spacer = gtk.VBox()
		self.add(spacer)
		self.set_border_width(15)
		self.set_size_request(385, 200)

		tab = gtk.Table(6, 2, False)
		tab.set_row_spacings(10)
		tab.set_col_spacings(10)
		spacer.add(tab)

		#---------------------------

		label = gtk.Label(_('Desktop color:'))
		label.set_alignment(0, 0.5)
		tab.attach(label, 0, 1, 0, 1, gtk.FILL | gtk.EXPAND, gtk.SHRINK)

		self.cb1 = gtk.ColorButton()
		self.cb1.set_size_request(100, -1)
		self.cb1.set_title(_('Select desktop color'))
		self.cb1.set_color(gtk.gdk.Color(rgb_to_hexcolor(config.desktop_color)))
		tab.attach(self.cb1, 1, 2, 0, 1, gtk.SHRINK, gtk.SHRINK)

		#---------------------------

		label = gtk.Label(_('Axes color:'))
		label.set_alignment(0, 0.5)
		tab.attach(label, 0, 1, 1, 2, gtk.FILL | gtk.EXPAND, gtk.SHRINK)

		self.cb2 = gtk.ColorButton()
		self.cb2.set_size_request(100, -1)
		self.cb2.set_title(_('Select axes color'))
		self.cb2.set_color(gtk.gdk.Color(rgb_to_hexcolor(config.axes_color)))
		tab.attach(self.cb2, 1, 2, 1, 2, gtk.SHRINK, gtk.SHRINK)

		#---------------------------

		label = gtk.Label(_('Page background color:'))
		label.set_alignment(0, 0.5)
		tab.attach(label, 0, 1, 2, 3, gtk.FILL | gtk.EXPAND, gtk.SHRINK)

		self.cb3 = gtk.ColorButton()
		self.cb3.set_size_request(100, -1)
		self.cb3.set_title(_('Select page background color'))
		self.cb3.set_color(gtk.gdk.Color(rgb_to_hexcolor(config.page_color)))
		tab.attach(self.cb3, 1, 2, 2, 3, gtk.SHRINK, gtk.SHRINK)

		#---------------------------

		label = gtk.Label(_('Page border color:'))
		label.set_alignment(0, 0.5)
		tab.attach(label, 0, 1, 3, 4, gtk.FILL | gtk.EXPAND, gtk.SHRINK)

		self.cb4 = gtk.ColorButton()
		self.cb4.set_size_request(100, -1)
		self.cb4.set_title(_('Select page border color'))
		self.cb4.set_color(gtk.gdk.Color(rgb_to_hexcolor(config.page_border_color)))
		tab.attach(self.cb4, 1, 2, 3, 4, gtk.SHRINK, gtk.SHRINK)

		#---------------------------

		label = gtk.Label(_('Paths color:'))
		label.set_alignment(0, 0.5)
		tab.attach(label, 0, 1, 4, 5, gtk.FILL | gtk.EXPAND, gtk.SHRINK)

		self.cb5 = gtk.ColorButton()
		self.cb5.set_size_request(100, -1)
		self.cb5.set_title(_('Select paths color'))
		self.cb5.set_color(gtk.gdk.Color(rgb_to_hexcolor(config.paths_color)))
		tab.attach(self.cb5, 1, 2, 4, 5, gtk.SHRINK, gtk.SHRINK)

		self.show_all()

	def do_apply(self):
		config.desktop_color = gdk_hexcolor_to_rgb(self.cb1.get_color().to_string())
		config.axes_color = gdk_hexcolor_to_rgb(self.cb2.get_color().to_string())
		config.page_color = gdk_hexcolor_to_rgb(self.cb3.get_color().to_string())
		config.page_border_color = gdk_hexcolor_to_rgb(self.cb4.get_color().to_string())
		config.paths_color = gdk_hexcolor_to_rgb(self.cb5.get_color().to_string())



