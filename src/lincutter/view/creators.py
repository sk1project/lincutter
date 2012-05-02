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

from uc2.formats.pdxf import const

from lincutter import modes
from lincutter.view.controllers import AbstractController

class RectangleCreator(AbstractController):

	mode = modes.RECT_MODE

	def __init__(self, canvas, presenter):
		AbstractController.__init__(self, canvas, presenter)

	def do_action(self, event):
		if self.start and self.end:
			if abs(self.end[0] - self.start[0]) > 2 and \
			abs(self.end[1] - self.start[1]) > 2:
				rect = self.start + self.end
				self.api.create_rectangle(rect)

class EllipseCreator(AbstractController):

	mode = modes.ELLIPSE_MODE

	def __init__(self, canvas, presenter):
		AbstractController.__init__(self, canvas, presenter)

	def do_action(self, event):
		if self.start and self.end:
			if abs(self.end[0] - self.start[0]) > 2 and \
			abs(self.end[1] - self.start[1]) > 2:
				rect = self.start + self.end
				self.api.create_ellipse(rect)

class PolygonCreator(AbstractController):

	mode = modes.POLYGON_MODE

	def __init__(self, canvas, presenter):
		AbstractController.__init__(self, canvas, presenter)

	def do_action(self, event):
		if self.start and self.end:
			if abs(self.end[0] - self.start[0]) > 2 and \
			abs(self.end[1] - self.start[1]) > 2:
				rect = self.start + self.end
				self.api.create_polygon(rect)

class TextBlockCreator(AbstractController):

	mode = modes.TEXT_MODE

	def __init__(self, canvas, presenter):
		AbstractController.__init__(self, canvas, presenter)

	def do_action(self, event):
		if self.start and self.end:
			if abs(self.end[0] - self.start[0]) > 2 and \
			abs(self.end[1] - self.start[1]) > 2:
				rect = self.start + self.end
				self.api.create_text(rect)
			else:
				rect = self.start + self.start
				self.api.create_text(rect, width=const.TEXTBLOCK_WIDTH)


#		if self.start and self.end:
#			add_flag = False
#			if event.state & gtk.gdk.SHIFT_MASK:
#				add_flag = True
#			change_x = abs(self.end[0] - self.start[0])
#			change_y = abs(self.end[1] - self.start[1])
#			if change_x < 5 and change_y < 5:
#				self.canvas.select_at_point(self.start, add_flag)
#			else:
#				self.canvas.select_by_rect(self.start, self.end, add_flag)
#
#			dpoint = self.canvas.win_to_doc(self.start)
#			if self.selection.is_point_over(dpoint):
#				self.canvas.set_temp_mode(modes.MOVE_MODE)

