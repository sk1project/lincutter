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
import cairo
import gobject


from uc2.uc2const import mm_to_pt
from uc2.libcairo import normalize_bbox

from lincutter import _, config
from lincutter import modes, events
from lincutter.view import controllers
from lincutter.view import creators
from lincutter.view.renderer import PDRenderer


PAGEFIT = 0.9
ZOOM_IN = 1.25
ZOOM_OUT = 0.8
OFFSET = 15.0

WORKSPACE_HEIGHT = 2000 * mm_to_pt
WORKSPACE_WIDTH = 14000 * mm_to_pt

class AppCanvas(gtk.DrawingArea):

	mw = None
	matrix = None
	trafo = []
	zoom = 1.0
	width = 0
	height = 0
	mode = None
	previous_mode = None
	controller = None
	ctrls = None
	orig_cursor = None
	current_cursor = None
	resize_marker = 0
	stroke_view = True
	draft_view = False

	def __init__(self, parent):

		gtk.DrawingArea.__init__(self)
		self.mw = parent
		self.presenter = parent.presenter
		self.eventloop = self.presenter.eventloop
		self.app = self.presenter.app

		self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color("#ffffff"))

		self.add_events(gtk.gdk.BUTTON_PRESS_MASK |
					gtk.gdk.POINTER_MOTION_MASK |
					gtk.gdk.BUTTON_RELEASE_MASK |
              		gtk.gdk.SCROLL_MASK)

		self.connect('button_press_event', self.mousePressEvent)
		self.connect('motion_notify_event', self.mouseMoveEvent)
		self.connect('button_release_event', self.mouseReleaseEvent)
		self.connect('scroll-event', self.wheelEvent)

		self.connect('expose_event', self.repaint)
		self.trafo = [1.0, 0.0, 0.0, 1.0, 0.0 , 0.0]
		self.mw.h_adj.connect('value_changed', self.hscroll)
		self.mw.v_adj.connect('value_changed', self.vscroll)

		self.doc = self.presenter.model
		self.renderer = PDRenderer(self)
		self.my_change = False
		self.ctrls = self.init_controllers()
		self.eventloop.connect(self.eventloop.DOC_MODIFIED, self.repaint)
		self.eventloop.connect(self.eventloop.SELECTION_CHANGED,
							self.selection_repaint)

	def init_controllers(self):
		dummy = controllers.AbstractController(self, self.presenter)
		ctrls = {
		modes.SELECT_MODE: controllers.SelectController(self, self.presenter),
		modes.SHAPER_MODE: dummy,
		modes.ZOOM_MODE: controllers.ZoomController(self, self.presenter),
		modes.FLEUR_MODE: controllers.FleurController(self, self.presenter),
		modes.PICK_MODE: controllers.PickController(self, self.presenter),
		modes.LINE_MODE: dummy,
		modes.CURVE_MODE: dummy,
		modes.RECT_MODE: creators.RectangleCreator(self, self.presenter),
		modes.ELLIPSE_MODE: creators.EllipseCreator(self, self.presenter),
		modes.TEXT_MODE: creators.TextBlockCreator(self, self.presenter),
		modes.POLYGON_MODE: creators.PolygonCreator(self, self.presenter),
		modes.MOVE_MODE: controllers.MoveController(self, self.presenter),
		modes.RESIZE_MODE: controllers.TransformController(self, self.presenter),
		}
		return ctrls


	def set_mode(self, mode=modes.SELECT_MODE):
		if not mode == self.mode:
			self.mode = mode
			self.controller = self.ctrls[mode]
			self.controller.set_cursor()
			events.emit(events.MODE_CHANGED, mode)

	def set_temp_mode(self, mode=modes.SELECT_MODE, callback=None):
		if not mode == self.mode:
			self.previous_mode = self.mode
			self.mode = mode
			self.controller = self.ctrls[mode]
			self.controller.callback = callback
			self.controller.set_cursor()

	def restore_mode(self):
		if not self.previous_mode is None:
			self.set_mode(self.previous_mode)
			self.previous_mode = None

	def set_canvas_cursor(self, mode):
		self.current_cursor = self.app.cursors[mode]
		self.window.set_cursor(self.current_cursor)

	def set_temp_cursor(self, cursor):
		self.orig_cursor = self.app.cursors[self.mode]
		self.current_cursor = cursor
		self.window.set_cursor(cursor)

	def restore_cursor(self):
		if not self.orig_cursor is None:
			self.window.set_cursor(self.orig_cursor)
			self.current_cursor = self.orig_cursor
			self.orig_cursor = None

	def _scrolling(self, *args):
		m11, m12, m21, m22, dx_old, dy_old = self.trafo
		yval = float(self.mw.v_adj.get_value()) * m11
		xval = float(self.mw.h_adj.get_value()) * m11
		dx = -xval
		dy = -yval
		if dx - dx_old or dy - dy_old:
			self.trafo = [m11, m12, m21, m22, dx, dy]
			self.matrix = cairo.Matrix(m11, m12, m21, m22, dx, dy)
			self.force_redraw()

	def vscroll(self, *args):
		m11, m12, m21, m22, dx, dy = self.trafo
		val = float(self.mw.v_adj.get_value()) * m11
		dy = -val
		self.trafo = [m11, m12, m21, m22, dx, dy]
		self.matrix = cairo.Matrix(m11, m12, m21, m22, dx, dy)
		self.force_redraw()

	def hscroll(self, *args):
		m11, m12, m21, m22, dx, dy = self.trafo
		val = float(self.mw.h_adj.get_value()) * m11
		dx = -val
		self.trafo = [m11, m12, m21, m22, dx, dy]
		self.matrix = cairo.Matrix(m11, m12, m21, m22, dx, dy)
		self.force_redraw()

	def update_scrolls(self):
		x, y = self.win_to_doc()
		m11 = self.trafo[0]

		dx = dy = OFFSET / m11

		self.mw.h_adj.set_lower(-dx)
		self.mw.h_adj.set_upper(WORKSPACE_WIDTH)
		self.mw.h_adj.set_page_size(self.width / m11)
		self.mw.h_adj.set_step_increment(self.width / (m11 * 10.0))
		self.my_change = True
		self.mw.h_adj.set_value(x)

		self.mw.v_adj.set_lower(-WORKSPACE_HEIGHT)
		self.mw.v_adj.set_upper(dy)
		self.mw.v_adj.set_page_size(self.height / m11)
		self.mw.v_adj.set_step_increment(self.height / (m11 * 10.0))
		self.my_change = True
#		self.mw.v_adj.set_value(-self.height / m11 + dy)
		self.mw.v_adj.set_value(-y)

	def _keep_center(self):
		x, y, w, h = self.allocation
		w = float(w)
		h = float(h)
		if not w == self.width or not h == self.height:
			_dx = (w - self.width) / 2.0
			_dy = (h - self.height) / 2.0
			m11, m12, m21, m22, dx, dy = self.trafo
			dx += _dx
			if dx > OFFSET: dx = OFFSET
			dy += _dy
			if dy < h - OFFSET: dy = h - OFFSET
			self.trafo = [m11, m12, m21, m22, dx, dy]
			self.matrix = cairo.Matrix(m11, m12, m21, m22, dx, dy)
			self.width = w
			self.height = h
			self.update_scrolls()

	def _set_center(self, center):
		x, y = center
		_dx = self.width / 2.0 - x
		_dy = self.height / 2.0 - y
		m11, m12, m21, m22, dx, dy = self.trafo
		dx += _dx
		dy += _dy
		self.trafo = [m11, m12, m21, m22, dx, dy]
		self.matrix = cairo.Matrix(m11, m12, m21, m22, dx, dy)
		self.update_scrolls()

	def doc_to_win(self, point=[0.0, 0.0]):
		x, y = point
		m11, m12, m21, m22, dx, dy = self.trafo
		x_new = m11 * x + dx
		y_new = m22 * y + dy
		return [x_new, y_new]

	def win_to_doc(self, point=[0, 0]):
		x, y = point
		x = float(x)
		y = float(y)
		m11, m12, m21, m22, dx, dy = self.trafo
		x_new = (x - dx) / m11
		y_new = (y - dy) / m22
		return [x_new, y_new]

	def _fit_to_page(self):
		height = config.plotter_page_height

		x, y, w, h = self.allocation
		w = float(w)
		h = float(h)
		self.width = w
		self.height = h
		zoom = h / height * PAGEFIT
		dx = OFFSET
		dy = h - OFFSET
		self.trafo = [zoom, 0, 0, -zoom, dx, dy]
		self.matrix = cairo.Matrix(zoom, 0, 0, -zoom, dx, dy)
		self.zoom = zoom
		self.update_scrolls()

	def zoom_fit_to_page(self):
		self._fit_to_page()
		self.force_redraw()

	def _zoom(self, dzoom=1.0):
		m11, m12, m21, m22, dx, dy = self.trafo
		m11 *= dzoom
		_dx = (self.width * dzoom - self.width) / 2.0
		_dy = (self.height * dzoom - self.height) / 2.0
		dx = dx * dzoom - _dx
		dy = dy * dzoom - _dy
		if dx > OFFSET: dx = OFFSET
		if dy < self.height - OFFSET: dy = self.height - OFFSET
		self.trafo = [m11, m12, m21, -m11, dx, dy]
		self.matrix = cairo.Matrix(m11, m12, m21, -m11, dx, dy)
		self.zoom = m11
		self.update_scrolls()
		self.force_redraw()

	def zoom_in(self):
		self._zoom(ZOOM_IN)

	def zoom_out(self):
		self._zoom(ZOOM_OUT)

	def zoom_100(self):
		self._zoom(1.0 / self.zoom)

	def zoom_at_point(self, point, zoom):
		self._set_center(point)
		self._zoom(zoom)

	def zoom_to_rectangle(self, start, end):
		x, y, w, h = self.allocation
		w = float(w)
		h = float(h)
		self.width = w
		self.height = h
		width = abs(end[0] - start[0])
		height = abs(end[1] - start[1])
		zoom = min(w / width, h / height) * 0.95
		center = [start[0] + (end[0] - start[0]) / 2,
				start[1] + (end[1] - start[1]) / 2]
		self._set_center(center)
		self._zoom(zoom)

	def zoom_selected(self):
		x0, y0, x1, y1 = self.presenter.selection.frame
		start = self.doc_to_win([x0, y0])
		end = self.doc_to_win([x1, y1])
		self.zoom_to_rectangle(start, end)

	def select_at_point(self, point, flag=False):
		point = self.win_to_doc(point)
		self.presenter.selection.select_at_point(point, flag)

	def pick_at_point(self, point):
		point = self.win_to_doc(point)
		return self.presenter.selection.pick_at_point(point)

	def select_by_rect(self, start, end, flag=False):
		start = self.win_to_doc(start)
		end = self.win_to_doc(end)
		rect = start + end
		rect = normalize_bbox(rect)
		self.presenter.selection.select_by_rect(rect, flag)

	def force_redraw(self):
		self.queue_draw()
		self.eventloop.emit(self.eventloop.VIEW_CHANGED)

	def repaint(self, *args):
		if self.matrix is None:
			self.zoom_fit_to_page()
			self.set_mode(modes.SELECT_MODE)
		self._keep_center()
		self.renderer.paint_document()

	def selection_repaint(self, *args):
		self.renderer.paint_selection()

#==============EVENT CONTROLLING==========================
	def mouseDoubleClickEvent(self, widget, event):
		pass

	def mouseMoveEvent(self, widget, event):
		self.controller.mouse_move(event)

	def mousePressEvent(self, widget, event):
		self.controller.set_cursor()
		self.controller.mouse_down(event)

	def mouseReleaseEvent(self, widget, event):
		self.controller.mouse_up(event)

	def wheelEvent(self, widget, event):
		self.controller.wheel(event)

	def keyPressEvent(self, widget, event):
		pass

	def keyReleaseEvent(self, widget, event):
		pass





