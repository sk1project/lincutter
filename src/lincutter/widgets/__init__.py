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

from uc2.uc2const import unit_dict, point_dict

from lincutter import _, config, events
from uc2 import uc2const

class ImageButton(gtk.Button):
	def __init__(self, path, text):
		gtk.Button.__init__(self)
		self.set_property('relief', gtk.RELIEF_NONE)
		loader = gtk.gdk.pixbuf_new_from_file
		image = gtk.Image()
		pixbuf = loader(os.path.join(config.resource_dir, path))
		image.set_from_pixbuf(pixbuf)
		self.add(image)
		if text:
			self.set_tooltip_text(text)

class ActionButton(gtk.Button):
	def __init__(self, action):
		gtk.Button.__init__(self, stock=action.icon)
		self.set_property('relief', gtk.RELIEF_NONE)
		self.set_tooltip_text(action.tooltip)
		action.connect_proxy(self)

class KeepRatioLabel(gtk.EventBox):

	value = True

	def __init__(self):
		path_true = 'object-keep-ratio.png'
		path_false = 'object-dont-keep-ratio.png'

		loader = gtk.gdk.pixbuf_new_from_file
		self.image_true = loader(os.path.join(config.resource_dir, path_true))

		loader = gtk.gdk.pixbuf_new_from_file
		self.image_false = loader(os.path.join(config.resource_dir, path_false))

		gtk.EventBox.__init__(self)
		self.image = gtk.Image()
		self.image.set_from_pixbuf(self.image_true)
		self.add(self.image)
		self.connect('button-press-event', self.process_click)
		self.set_tooltip_text(_('Keep aspect ratio'))

	def process_click(self, *args):
		if self.value:
			self.value = False
			self.image.set_from_pixbuf(self.image_false)
			self.set_tooltip_text(_('Don\'t keep aspect ratio'))
		else:
			self.value = True
			self.image.set_from_pixbuf(self.image_true)
			self.set_tooltip_text(_('Keep aspect ratio'))


class UnitLabel(gtk.Label):

	def __init__(self):
		gtk.Label.__init__(self, config.default_unit)
		events.connect(events.CONFIG_MODIFIED, self.update_label)

	def update_label(self, *args):
		if args[0][0] == 'default_unit':
			self.set_text(config.default_unit)

class UnitSpin(gtk.SpinButton):

	point_value = 0
	flag = False
	callback = None

	def __init__(self, callback):
		#value=0, lower=0, upper=0, step_incr=0, page_incr=0, page_size=0
		self.callback = callback
		self.adj = gtk.Adjustment(0.0, 0.0, 1.0, 0.001, 1.0, 0.0)
		gtk.SpinButton.__init__(self, self.adj, 0.1, 2)
		self.update_increment()
		self.set_numeric(True)
		events.connect(events.CONFIG_MODIFIED, self.update_spin)
		self.connect('value-changed', self.update_point_value)

	def update_increment(self):
		self.flag = True
		if config.default_unit == uc2const.UNIT_IN:
			value = 0.001
			self.set_digits(3)
		else:
			value = 0.01
			self.set_digits(2)
		self.adj.set_upper(100000.0 * point_dict[config.default_unit])
		self.adj.set_step_increment(value)
		self.adj.set_page_increment(value)
		self.flag = True
		self.adj.set_value(self.point_value * point_dict[config.default_unit])
		self.flag = False


	def update_spin(self, *args):
		if args[0][0] == 'default_unit':
			self.update_increment()

	def update_point_value(self, *args):
		if self.flag:
			self.flag = False
		else:
			value = self.adj.get_value()
			self.point_value = value * unit_dict[config.default_unit]
			self.callback()

	def set_point_value(self, value=0.0):
		self.point_value = value
		self.flag = True
		self.adj.set_value(value * point_dict[config.default_unit])
		self.flag = False

	def get_point_value(self):
		return self.point_value
