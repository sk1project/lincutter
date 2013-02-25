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

from uc2.utils import system

from lincutter.view.canvas import AppCanvas
from lincutter.widgets.ruler import RulerCorner, Ruler


class DocArea(gtk.Table):

	canvas = None
	caption = None
	tab_caption = None
	corner = None
	hruler = None
	vruler = None

	def __init__(self, app, presenter):
		gtk.Table.__init__(self)
		self.app = app
		self.presenter = presenter
		self.caption = presenter.doc_name

		self.tab_caption = TabCaption(self, self.caption)

		da_box = gtk.Table(3, 3, False)

		self.corner = RulerCorner(self)
		da_box.attach(self.corner, 0, 1, 0, 1, gtk.SHRINK, gtk.SHRINK)

		self.hruler = Ruler(self, 0)
		da_box.attach(self.hruler, 1, 3, 0, 1, gtk.EXPAND | gtk.FILL, gtk.SHRINK)

		self.vruler = Ruler(self, 1)
		da_box.attach(self.vruler, 0, 1, 1, 3, gtk.SHRINK, gtk.EXPAND | gtk.FILL)

		self.v_adj = gtk.Adjustment()
		self.vscroll = gtk.VScrollbar(self.v_adj)
		da_box.attach(self.vscroll, 2, 3, 1, 2, gtk.SHRINK, gtk.EXPAND | gtk.FILL)

		self.h_adj = gtk.Adjustment()
		self.hscroll = gtk.HScrollbar(self.h_adj)
		da_box.attach(self.hscroll, 1, 2, 2, 3, gtk.EXPAND | gtk.FILL, gtk.SHRINK)

		self.canvas = AppCanvas(self)
		da_box.attach(self.canvas, 1, 2, 1, 2, gtk.FILL | gtk.EXPAND,
			gtk.FILL | gtk.EXPAND, 0, 0)

		if system.get_os_family() == system.WINDOWS:
			xpad = 2; ypad = 0
		else:
			xpad = ypad = 3

		self.attach(da_box, 0, 1, 0, 1,
					gtk.EXPAND | gtk.FILL, gtk.EXPAND | gtk.FILL,
					xpadding=xpad, ypadding=ypad)

	def set_caption(self, caption):
		self.caption = caption
		self.tab_caption.set_caption(self.caption)

class TabCaption(gtk.HBox):

	do_action = False

	def __init__(self, master, caption):
		gtk.HBox.__init__(self, False, 0)
		self.presenter = master.presenter
		self.app = master.app
		self.mw = master.app.mw

		self.label = gtk.Label('')
		self.tab_icon = gtk.Image()
		self.tab_icon.set_from_stock(gtk.STOCK_FILE, gtk.ICON_SIZE_MENU)
		self.but_icon = gtk.Image()
		self.but_icon.set_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)


		self.tab_button = gtk.EventBox()
		self.tab_button.set_border_width(0)
		self.tab_button.set_visible_window(False)
		self.tab_button.set_size_request(15, 15)
		color = self.mw.get_style().bg[gtk.STATE_ACTIVE]
		self.tab_button.modify_bg(gtk.STATE_NORMAL, color)
		self.tab_button.add(self.but_icon)

		self.pack_start(self.tab_icon, False)
		self.pack_start(self.label, False)
		self.pack_start(self.tab_button, False)
		self.set_caption(caption)
		self.show_all()
		self.but_icon.set_property('sensitive', False)

		self.tab_button.connect('button-press-event', self.button_press)
		self.tab_button.connect('button-release-event', self.button_release)
		self.tab_button.connect('leave-notify-event', self.leave_event)
		self.tab_button.connect('enter-notify-event', self.enter_event)

	def set_caption(self, caption):
		self.label.set_text('  %s  ' % (caption))

	def enter_event(self, *args):
		self.but_icon.set_property('sensitive', True)

	def leave_event(self, *args):
		self.but_icon.set_property('sensitive', False)
		self.do_action = False

	def button_press(self, *args):
		self.but_icon.set_property('sensitive', False)
		self.do_action = True

	def button_release(self, *args):
		self.but_icon.set_property('sensitive', True)
		if self.do_action:
			self.app.close(self.presenter)


