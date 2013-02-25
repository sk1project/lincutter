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

from copy import deepcopy

import cairo

from uc2 import uc2const
from uc2.formats.pdxf import model
from uc2.formats.pdxf.crenderer import CairoRenderer
from uc2 import libcairo

from lincutter import config

CAIRO_BLACK = [0.0, 0.0, 0.0]
CAIRO_LIGHT_GRAY = [0.95, 0.95, 0.95]
CAIRO_GRAY = [0.5, 0.5, 0.5]
CAIRO_WHITE = [1.0, 1.0, 1.0]
CAIRO_BLUE = [0.0, 0.0, 1.0]
CAIRO_RED = [1.0, 0.0, 0.0]

class PDRenderer(CairoRenderer):

	direct_matrix = None

	canvas = None
	ctx = None
	win_ctx = None
	surface = None
	presenter = None

	width = 0
	height = 0

	def __init__(self, canvas):

		self.canvas = canvas
		self.direct_matrix = cairo.Matrix(1.0, 0.0, 0.0, 1.0, 0.0, 0.0)

	#-------DOCUMENT RENDERING

	def paint_document(self):
		self.presenter = self.canvas.presenter
		self.cms = self.presenter.cms
		self.win_ctx = self.canvas.window.cairo_create()
		self.start()
		self.paint_page_border()
		self.render_doc()
#		self.finalize()
		self.paint_selection()

	def start(self):
		width = int(self.canvas.width)
		height = int(self.canvas.height)
		if self.surface is None:
			self.surface = cairo.ImageSurface(cairo.FORMAT_RGB24, width, height)
			self.width = width
			self.height = height
		elif self.width <> width or self.height <> height:
			self.surface = cairo.ImageSurface(cairo.FORMAT_RGB24, width, height)
			self.width = width
			self.height = height
		self.ctx = cairo.Context(self.surface)
		self.ctx.set_source_rgb(*config.desktop_color)
		self.ctx.paint()

	def finalize(self):
		self.win_ctx.set_source_surface(self.surface)
		self.win_ctx.paint()

	def paint_page_border(self):
		self.ctx.set_matrix(self.canvas.matrix)
		self.ctx.set_line_width(1.0 / self.canvas.zoom)
		self.ctx.set_antialias(cairo.ANTIALIAS_NONE)

		x, y = self.canvas.doc_to_win()

		x1 = config.plotter_page_width
		y1 = config.plotter_page_height
		p4 = [0.0, y1]
		p5 = [x1, y1]
		p6 = [x1, 0.0]

		self.ctx.rectangle(0.0, 0.0, x1, y1)
		self.ctx.set_source_rgb(*config.page_color)
		self.ctx.fill()

		self.ctx.new_path()
		self.ctx.move_to(*p4)
		self.ctx.line_to(*p5)
		self.ctx.line_to(*p6)
		self.ctx.set_source_rgb(*config.page_border_color)
		self.ctx.stroke()

		p0 = self.canvas.win_to_doc([0.0, y])
		p1 = self.canvas.win_to_doc([self.canvas.width, y])
		p2 = self.canvas.win_to_doc([x, 0.0])
		p3 = self.canvas.win_to_doc([x, self.canvas.height])

		self.ctx.new_path()
		self.ctx.move_to(*p0)
		self.ctx.line_to(*p1)
		self.ctx.set_source_rgb(*config.axes_color)
		self.ctx.stroke()

		self.ctx.new_path()
		self.ctx.move_to(*p2)
		self.ctx.line_to(*p3)
		self.ctx.set_source_rgb(*config.axes_color)
		self.ctx.stroke()

	def render_doc(self):
		if self.canvas.draft_view:
			self.antialias_flag = False
		else:
			self.antialias_flag = True

		self.contour_flag = True

		page = self.presenter.active_page
		for layer in page.childs:
			if self.canvas.stroke_view:
				self.stroke_style = deepcopy(layer.style)
				color = deepcopy(config.paths_color)
				stroke = self.stroke_style[1]
				stroke[1] = 1.0 / self.canvas.zoom
				stroke[2] = [uc2const.COLOR_RGB, color, 1.0, '']
			self.render(self.ctx, layer.childs)

	#------MARKER RENDERING

	def start_soft_repaint(self):
		self.win_ctx = self.canvas.window.cairo_create()
		self.temp_surface = cairo.ImageSurface(cairo.FORMAT_RGB24,
								int(self.canvas.width),
								int(self.canvas.height))
		self.ctx = cairo.Context(self.temp_surface)
		self.ctx.set_source_surface(self.surface)
		self.ctx.paint()

	def end_soft_repaint(self):
		self.win_ctx.set_source_surface(self.temp_surface)
		self.win_ctx.paint()

	def draw_frame(self, start, end):
		if start and end:
			path = libcairo.convert_bbox_to_cpath(start + end)
			self._draw_frame(path)

	def _draw_frame(self, path):
		self.start_soft_repaint()
		self.ctx.set_matrix(self.direct_matrix)
		self.ctx.set_antialias(cairo.ANTIALIAS_NONE)
		self.ctx.set_line_width(1.0)
		self.ctx.set_dash([])
		self.ctx.set_source_rgb(1, 1, 1)
		self.ctx.new_path()
		self.ctx.append_path(path)
		self.ctx.stroke()
		self.ctx.set_dash(config.sel_frame_dash)
		r, g, b = config.sel_frame_color
		self.ctx.set_source_rgb(r, g, b)
		self.ctx.new_path()
		self.ctx.append_path(path)
		self.ctx.stroke()

		self.end_soft_repaint()

	def _paint_selection(self):
		selection = self.presenter.selection
		if selection.objs:
			selection.update_markers()
			zoom = self.canvas.zoom
			self.ctx.set_matrix(self.canvas.matrix)
			self.ctx.set_antialias(cairo.ANTIALIAS_NONE)

			#Frame
			x0, y0, x1, y1 = selection.frame
			self.ctx.set_line_width(1.0 / zoom)
			self.ctx.set_dash([])
			self.ctx.set_source_rgb(1, 1, 1)
			self.ctx.rectangle(x0, y0, x1 - x0, y1 - y0)
			self.ctx.stroke()
			r, g, b = config.sel_marker_frame_color
			self.ctx.set_source_rgb(r, g, b)
			a, b = config.sel_marker_frame_dash
			self.ctx.set_dash([a / zoom, b / zoom])
			self.ctx.rectangle(x0, y0, x1 - x0, y1 - y0)
			self.ctx.stroke()

			#Selection markers
			markers = selection.markers
			r, g, b = config.sel_marker_fill
			r1, g1, b1 = config.sel_marker_stroke
			size = config.sel_marker_size / zoom
			i = 0
			for marker in markers:
				if i == 9:
					cs = 3.0 / (2.0 * zoom)
					self.ctx.set_source_rgb(r, g, b)
					self.ctx.rectangle(marker[0], marker[1] + size / 2.0 - cs,
									size, 2.0 * cs)
					self.ctx.rectangle(marker[0] + size / 2.0 - cs, marker[1],
									2.0 * cs, size)
					self.ctx.fill()
					self.ctx.set_source_rgb(r1, g1, b1)
					self.ctx.move_to(marker[0] + size / 2.0, marker[1])
					self.ctx.line_to(marker[0] + size / 2.0, marker[1] + size)
					self.ctx.stroke()
					self.ctx.move_to(marker[0], marker[1] + size / 2.0)
					self.ctx.line_to(marker[0] + size, marker[1] + size / 2.0)
					self.ctx.stroke()
				elif i in [0, 1, 2, 3, 5, 6, 7, 8]:
					self.ctx.set_source_rgb(r, g, b)
					self.ctx.rectangle(marker[0], marker[1], size, size)
					self.ctx.fill_preserve()
					self.ctx.set_source_rgb(r1, g1, b1)
					self.ctx.set_line_width(1.0 / zoom)
					self.ctx.set_dash([])
					self.ctx.stroke()
				i += 1

			#Object markers
			objs = selection.objs
			self.ctx.set_source_rgb(0, 0, 0)
			self.ctx.set_line_width(1.0 / zoom)
			self.ctx.set_dash([])
			offset = 2.0 / zoom
			for obj in objs:
				bbox = obj.cache_bbox
				self.ctx.rectangle(bbox[0] - offset, bbox[1] - offset,
								 2.0 * offset, 2.0 * offset)
				self.ctx.stroke()

	def	paint_selection(self):
		self.start_soft_repaint()
		self._paint_selection()
		self.end_soft_repaint()

	def stop_draw_frame(self, start, end):
		self.start_soft_repaint()
		self.end_soft_repaint()

	def show_move_frame(self):
		bbox = self.presenter.selection.bbox
		if bbox:
			path = libcairo.convert_bbox_to_cpath(bbox)
			libcairo.apply_trafo(path, self.canvas.trafo)
			self._draw_frame(path)

	def draw_move_frame(self, trafo):
		bbox = self.presenter.selection.bbox
		if bbox:
			path = libcairo.convert_bbox_to_cpath(bbox)
			libcairo.apply_trafo(path, trafo)
			libcairo.apply_trafo(path, self.canvas.trafo)
			self._draw_frame(path)

	def hide_move_frame(self):
		self.start_soft_repaint()
		self._paint_selection()
		self.end_soft_repaint()
