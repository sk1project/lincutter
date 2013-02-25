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
import types
import math
import gtk

from uc2.formats.pdxf import model
from uc2.formats.pdxf import const
from uc2 import libgeom

from lincutter import _
from lincutter import config
from lincutter import events
from lincutter import dialogs
from lincutter import modes


class AbstractAPI:

	presenter = None
	view = None
	methods = None
	model = None
	app = None
	eventloop = None
	undo = []
	redo = []
	undo_marked = False
	selection = None
	callback = None
	pdxf_cfg = None

	def do_undo(self):
		transaction_list = self.undo[-1][0]
		for transaction in transaction_list:
			self._do_action(transaction)
		tr = self.undo[-1]
		self.undo.remove(tr)
		self.redo.append(tr)
		self.eventloop.emit(self.eventloop.DOC_MODIFIED)
		if self.undo and self.undo[-1][2]:
			self.presenter.reflect_saving()
		if not self.undo and not self.undo_marked:
			self.presenter.reflect_saving()

	def do_redo(self):
		action_list = self.redo[-1][1]
		for action in action_list:
			self._do_action(action)
		tr = self.redo[-1]
		self.redo.remove(tr)
		self.undo.append(tr)
		self.eventloop.emit(self.eventloop.DOC_MODIFIED)
		if not self.undo or self.undo[-1][2]:
			self.presenter.reflect_saving()

	def _do_action(self, action):
		if not action: return
		if len(action) == 1:
			action[0]()
		elif len(action) == 2:
			action[0](action[1])
		elif len(action) == 3:
			action[0](action[1], action[2])
		elif len(action) == 4:
			action[0](action[1], action[2], action[3])
		elif len(action) == 5:
			action[0](action[1], action[2], action[3], action[4])
		elif len(action) == 6:
			action[0](action[1], action[2], action[3], action[4], action[5])

	def _clear_history_stack(self, stack):
		for obj in stack:
			if type(obj) == types.ListType:
				obj = self._clear_history_stack(obj)
		return []

	def add_undo(self, transaction):
		self.redo = self._clear_history_stack(self.redo)
		self.undo.append(transaction)
		self.eventloop.emit(self.eventloop.DOC_MODIFIED)

	def save_mark(self):
		for item in self.undo:
			item[2] = False
		for item in self.redo:
			item[2] = False

		if self.undo:
			self.undo[-1][2] = True
			self.undo_marked = True

	def _set_selection(self, objs):
		self.selection.objs = [] + objs
		self.selection.update()

	def _delete_object(self, obj):
		self.methods.delete_object(obj)
		if obj in self.selection.objs:
			self.selection.remove([obj])

	def _insert_object(self, obj, parent, index):
		self.methods.insert_object(obj, parent, index)

	def _get_layers_snapshot(self):
		layers_snapshot = []
		model = self.presenter.model
		page = self.presenter.active_page
		layers = page.childs + model.childs[1].childs
		for layer in layers:
			layers_snapshot.append([layer, [] + layer.childs])
		return layers_snapshot

	def _set_layers_snapshot(self, layers_snapshot):
		for layer, childs in layers_snapshot:
			layer.childs = childs

	def _delete_objects(self, objs_list):
		for obj, parent, index in objs_list:
			self.methods.delete_object(obj)
			if obj in self.selection.objs:
				self.selection.remove([obj])

	def _insert_objects(self, objs_list):
		for obj, parent, index in objs_list:
			self.methods.insert_object(obj, parent, index)

	def _normalize_rect(self, rect):
		x0, y0, x1, y1 = rect
		x0, y0 = self.view.win_to_doc([x0, y0])
		x1, y1 = self.view.win_to_doc([x1, y1])
		new_rect = [0, 0, 0, 0]
		if x0 < x1:
			new_rect[0] = x0
			new_rect[2] = x1 - x0
		else:
			new_rect[0] = x1
			new_rect[2] = x0 - x1
		if y0 < y1:
			new_rect[1] = y0
			new_rect[3] = y1 - y0
		else:
			new_rect[1] = y1
			new_rect[3] = y0 - y1
		return new_rect

	def _get_objs_styles(self, objs):
		result = []
		for obj in objs:
			style = deepcopy(obj.style)
			result.append([obj, style])
		return result

	def _set_objs_styles(self, objs_styles):
		for obj, style in objs_styles:
			obj.style = style

	def _fill_objs(self, objs, color):
		for obj in objs:
			style = deepcopy(obj.style)
			if color:
				fill = style[0]
				new_fill = []
				if not fill:
					new_fill.append(self.pdxf_cfg.default_fill_rule)
				else:
					new_fill.append(fill[0])
				new_fill.append(const.FILL_SOLID)
				new_fill.append(deepcopy(color))
				style[0] = new_fill
			else:
				style[0] = []
			obj.style = style

	def _apply_trafo(self, objs, trafo):
		before = []
		after = []
		for obj in objs:
			before.append(obj.get_trafo_snapshot())
			obj.apply_trafo(trafo)
			after.append(obj.get_trafo_snapshot())
		self.selection.update_bbox()
		return (before, after)

	def _set_snapshots(self, snapshots):
		for snapshot in snapshots:
			obj = snapshot[0]
			obj.set_trafo_snapshot(snapshot)
		self.selection.update_bbox()

	def _stroke_objs(self, objs, color):
		for obj in objs:
			style = deepcopy(obj.style)
			if color:
				stroke = style[1]
				if not stroke:
					new_stroke = deepcopy(self.pdxf_cfg.default_stroke)
				else:
					new_stroke = deepcopy(stroke)
				new_stroke[2] = deepcopy(color)
				style[1] = new_stroke
			else:
				style[1] = []
			obj.style = style

	def _set_parent(self, objs, parent):
		for obj in objs:
			obj.parent = parent

	def _restore_parents(self, parent_list):
		for obj, parent in parent_list:
			obj.parent = parent


class PresenterAPI(AbstractAPI):

	def __init__(self, presenter):
		self.presenter = presenter
		self.selection = presenter.selection
		self.methods = self.presenter.methods
		self.model = presenter.model
		self.pdxf_cfg = presenter.doc_presenter.config
		self.view = presenter.canvas

		self.eventloop = presenter.eventloop
		self.app = presenter.app
		self.undo = []
		self.redo = []

	def clear_history(self):
		self.undo = self._clear_history_stack(self.undo)
		self.redo = self._clear_history_stack(self.redo)
		events.emit(events.DOC_MODIFIED, self.presenter)
		self.presenter.reflect_saving()

	def set_doc_origin(self, origin):
		cur_origin = self.model.doc_origin
		transaction = [
			[[self.methods.set_doc_origin, cur_origin]],
			[[self.methods.set_doc_origin, origin]],
			False]
		self.methods.set_doc_origin(origin)
		self.add_undo(transaction)

	def insert_object(self, obj, parent, index):
		sel_before = [] + self.selection.objs
		self._insert_object(obj, parent, index)
		self.selection.set([obj])
		sel_after = [] + self.selection.objs
		transaction = [
			[[self._delete_object, obj],
			[self._set_selection, sel_before]],
			[[self._insert_object, obj, parent, index],
			[self._set_selection, sel_after]],
			False]
		self.add_undo(transaction)
		self.selection.update()

	def delete_object(self, obj, parent, index):
		sel_before = [] + self.selection.objs
		self._delete_object(obj)
		sel_after = []
		transaction = [
			[[self._insert_object, obj, parent, index],
			[self._set_selection, sel_before]],
			[[self._delete_object, obj],
			[self._set_selection, sel_after]],
			False]
		self.add_undo(transaction)
		self.selection.update()

	def insert_objects(self, objs_list):
		sel_before = [] + self.selection.objs
		self._insert_objects(objs_list)
		sel_after = [] + objs_list
		transaction = [
			[[self._delete_objects, objs_list],
			[self._set_selection, sel_before]],
			[[self._insert_objects, objs_list],
			[self._set_selection, sel_after]],
			False]
		self.add_undo(transaction)
		self.selection.update()

	def delete_objects(self, objs_list):
		sel_before = [] + self.selection.objs
		self._delete_objects(objs_list)
		sel_after = []
		transaction = [
			[[self._insert_objects, objs_list],
			[self._set_selection, sel_before]],
			[[self._delete_objects, objs_list],
			[self._set_selection, sel_after]],
			False]
		self.add_undo(transaction)
		self.selection.update()

	def delete_selected(self):
		if self.selection.objs:
			before = self._get_layers_snapshot()
			sel_before = [] + self.selection.objs
			for obj in self.selection.objs:
				self.methods.delete_object(obj)
			after = self._get_layers_snapshot()
			transaction = [
				[[self._set_layers_snapshot, before],
				[self._set_selection, sel_before]],
				[[self._set_layers_snapshot, after],
				[self.selection.clear()]],
				False]
			self.add_undo(transaction)
		self.selection.clear()

	def cut_selected(self):
		self.copy_selected()
		self.delete_selected()

	def copy_selected(self):
		if self.selection.objs:
			self.app.clipboard.set(self.selection.objs)

	def paste_selected(self):
		objs = self.app.clipboard.get()
		sel_before = [] + self.selection.objs
		before = self._get_layers_snapshot()
		self.methods.append_objects(objs, self.presenter.active_layer)
		after = self._get_layers_snapshot()
		sel_after = [] + objs
		transaction = [
			[[self._set_layers_snapshot, before],
			[self._set_selection, sel_before]],
			[[self._set_layers_snapshot, after],
			[self._set_selection, sel_after]],
			False]
		self.add_undo(transaction)
		for obj in objs:
			obj.do_update()
		self.selection.set(objs)
		self.selection.update()

#/////////// CREATORS //////////////////////
	def create_rectangle(self, rect):
		rect = self._normalize_rect(rect)
		parent = self.presenter.active_layer
		obj = model.Rectangle(self.pdxf_cfg, parent, rect)
		obj.style = deepcopy(self.model.styles['Default Style'])
		obj.update()
		self.insert_object(obj, parent, len(parent.childs))

	def create_ellipse(self, rect):
		rect = self._normalize_rect(rect)
		parent = self.presenter.active_layer
		obj = model.Circle(self.pdxf_cfg, parent, rect)
		obj.style = deepcopy(self.model.styles['Default Style'])
		obj.update()
		self.insert_object(obj, parent, len(parent.childs))

	def create_polygon(self, rect):
		rect = self._normalize_rect(rect)
		parent = self.presenter.active_layer
		obj = model.Polygon(self.pdxf_cfg, parent, rect)
		obj.style = deepcopy(self.model.styles['Default Style'])
		obj.update()
		self.insert_object(obj, parent, len(parent.childs))

	def create_text(self, rect, width=0):
		rect = self._normalize_rect(rect)
		parent = self.presenter.active_layer
		if width == 0: width = rect[2]
		text = dialogs.text_edit_dialog(self.app.mw)
		if text:
			obj = model.Text(self.pdxf_cfg, parent, rect, text, width)
			obj.style = deepcopy(self.model.styles['Default Style'])
			obj.update()
			self.insert_object(obj, parent, len(parent.childs))


#///////////////////////////////////////////

	#FIXME: Add undo for operation!
	def edit_text(self):
		if self.selection.objs:
			obj = self.selection.objs[0]
			obj.text = dialogs.text_edit_dialog(self.app.mw, obj.text)
			obj.update()

	def fill_selected(self, color):
		if self.selection.objs:
			color = deepcopy(color)
			sel_before = [] + self.selection.objs
			objs = [] + self.selection.objs
			initial_styles = self._get_objs_styles(objs)
			self._fill_objs(objs, color)
			sel_after = [] + self.selection.objs
			transaction = [
				[[self._set_objs_styles, initial_styles],
				[self._set_selection, sel_before]],
				[[self._fill_objs, objs, color],
				[self._set_selection, sel_after]],
				False]
			self.add_undo(transaction)
			self.selection.update()

	def stroke_selected(self, color):
		if self.selection.objs:
			color = deepcopy(color)
			sel_before = [] + self.selection.objs
			objs = [] + self.selection.objs
			initial_styles = self._get_objs_styles(objs)
			self._stroke_objs(objs, color)
			sel_after = [] + self.selection.objs
			transaction = [
				[[self._set_objs_styles, initial_styles],
				[self._set_selection, sel_before]],
				[[self._stroke_objs, objs, color],
				[self._set_selection, sel_after]],
				False]
			self.add_undo(transaction)
			self.selection.update()

	def transform_selected(self, trafo, copy=False):
		if self.selection.objs:
			sel_before = [] + self.selection.objs
			objs = [] + self.selection.objs
			if copy:
				copied_objs = []
				for obj in objs:
					copied_obj = obj.copy()
					copied_obj.update()
					copied_objs.append(copied_obj)
				self._apply_trafo(copied_objs, trafo)
				before = self._get_layers_snapshot()
				self.methods.append_objects(copied_objs,
										self.presenter.active_layer)
				after = self._get_layers_snapshot()
				sel_after = [] + copied_objs
				transaction = [
					[[self._set_layers_snapshot, before],
					[self._set_selection, sel_before]],
					[[self._set_layers_snapshot, after],
					[self._set_selection, sel_after]],
					False]
				self.add_undo(transaction)
				self.selection.set(copied_objs)
			else:
				before, after = self._apply_trafo(objs, trafo)
				sel_after = [] + objs
				transaction = [
					[[self._set_snapshots, before],
					[self._set_selection, sel_before]],
					[[self._set_snapshots, after],
					[self._set_selection, sel_after]],
					False]
				self.add_undo(transaction)
			self.selection.update()

	def move_selected(self, x, y, copy=False):
		trafo = [1.0, 0.0, 0.0, 1.0, x, y]
		self.transform_selected(trafo, copy)


	def move_to_origin_selected(self, copy=False):
		if self.selection.objs:
			bbox = self.selection.bbox
			x0, y0 = bbox[:2]
			trafo = [1.0, 0.0, 0.0, 1.0, -x0, -y0]
			self.transform_selected(trafo, copy)

	def rotate_selected(self, angle=0, copy=False):
		if self.selection.objs:
			bbox = self.selection.bbox
			w = bbox[2] - bbox[0]
			h = bbox[3] - bbox[1]

			x0, y0 = bbox[:2]
			shift_x, shift_y = self.selection.center_offset
			center_x = x0 + w / 2.0 + shift_x
			center_y = y0 + h / 2.0 + shift_y

			m21 = math.sin(angle)
			m11 = m22 = math.cos(angle)
			m12 = -m21
			dx = center_x - m11 * center_x + m21 * center_y;
			dy = center_y - m21 * center_x - m11 * center_y;

			trafo = [m11, m21, m12, m22, dx, dy]
			self.transform_selected(trafo, copy)

	def mirror_selected(self, vertical=True, copy=False):
		if self.selection.objs:
			m11 = m22 = 1.0
			dx = dy = 0.0
			bbox = self.selection.bbox
			w = bbox[2] - bbox[0]
			h = bbox[3] - bbox[1]
			x0, y0 = bbox[:2]
			if vertical:
				m22 = -1
				dy = 2 * y0 + h
			else:
				m11 = -1
				dx = 2 * x0 + w

			trafo = [m11, 0.0, 0.0, m22, dx, dy]
			self.transform_selected(trafo, copy)

	def multiply_selected(self):
		from lincutter.dialogs.multiply import multiply_dialog

		data = multiply_dialog(self.app.mw)
		if data:
			hor_quant, vert_quant, hor_spacing, vert_spacing = data

			if hor_quant == vert_quant == 1: return

			bbox = self.selection.bbox
			w = bbox[2] - bbox[0]
			h = bbox[3] - bbox[1]

			direction = 1
			for column in range(hor_quant):
				for row in range(vert_quant - 1):
					self.move_selected(0.0, direction * (h + vert_spacing), True)
				if direction == 1:
					direction = -1
				else:
					direction = 1
				if column < hor_quant - 1:
					self.move_selected(w + hor_spacing, 0.0, True)


	def convert_to_curve_selected(self):
		if self.selection.objs:
			before = self._get_layers_snapshot()
			objs = [] + self.selection.objs
			sel_before = [] + self.selection.objs

			for obj in objs:
				if obj.cid > model.PRIMITIVE_CLASS and not obj.cid == model.CURVE:
					curve = obj.to_curve()
					if curve is not None:
						parent = obj.parent
						id = parent.childs.index(obj)
						curve.parent = parent
						parent.childs[id] = curve
						sel_id = self.selection.objs.index(obj)
						self.selection.objs[sel_id] = curve

			after = self._get_layers_snapshot()
			sel_after = [] + self.selection.objs
			transaction = [
				[[self._set_layers_snapshot, before],
				[self._set_selection, sel_before]],
				[[self._set_layers_snapshot, after],
				[self._set_selection, sel_after]],
				False]
			self.add_undo(transaction)
			self.selection.update()

	def group_selected(self):
		if self.selection.objs:
			before = self._get_layers_snapshot()
			objs = [] + self.selection.objs
			sel_before = [] + self.selection.objs

			parent = objs[-1].parent
			group = model.Group(objs[-1].config, parent, objs)
			group.update()
			for obj in objs:
				obj.parent.childs.remove(obj)
			parent.childs.append(group)
			parent_list = []
			for obj in objs:
				parent_list.append([obj, obj.parent])
				obj.parent = group

			after = self._get_layers_snapshot()
			sel_after = [group]
			self.selection.set([group])
			transaction = [
				[[self._set_layers_snapshot, before],
				[self._restore_parents, parent_list],
				[self._set_selection, sel_before]],
				[[self._set_layers_snapshot, after],
				[self._set_parent, sel_after, group],
				[self._set_selection, sel_after]],
				False]
			self.add_undo(transaction)
			self.selection.update()

	def ungroup_selected(self):
		if self.selection.objs:
			group = self.selection.objs[0]
			before = self._get_layers_snapshot()
			objs = [] + group.childs
			sel_before = [] + self.selection.objs
			parent = group.parent
			index = parent.childs.index(group)

			objs.reverse()
			parent.childs.remove(group)
			parent_list = []

			for obj in objs:
				parent.childs.insert(index, obj)
				obj.parent = parent
				parent_list.append([obj, group])

			after = self._get_layers_snapshot()
			sel_after = objs
			self.selection.set(sel_after)
			transaction = [
				[[self._set_layers_snapshot, before],
				[self._set_parent, sel_after, group],
				[self._set_selection, sel_before]],
				[[self._set_layers_snapshot, after],
				[self._restore_parents, parent_list],
				[self._set_selection, sel_after]],
				False]
			self.add_undo(transaction)
			self.selection.update()

	def _ungroup_tree(self, group, objs_list, parent_list):
		for obj in group.childs:
			if not obj.cid == model.GROUP:
				objs_list += [obj]
				parent_list += [[obj, obj.parent]]
			else:
				self._ungroup_tree(obj, objs_list, parent_list)

	def ungroup_all(self):
		if self.selection.objs:
			parent_list_before = []
			parent_list_after = []
			sel_after = []

			sel_before = [] + self.selection.objs
			before = self._get_layers_snapshot()

			for obj in self.selection.objs:
				if obj.cid == model.GROUP:
					objs_list = []
					self._ungroup_tree(obj, objs_list, parent_list_before)
					index = obj.parent.childs.index(obj)
					objs_list.reverse()
					for item in objs_list:
						parent_list_after.append([item, obj.parent])
						item.parent = obj.parent
						obj.parent.childs.insert(index, item)
						sel_after.append(item)
					obj.parent.childs.remove(obj)
				else:
					sel_after.append(obj)

			after = self._get_layers_snapshot()
			self.selection.set(sel_after)
			transaction = [
				[[self._set_layers_snapshot, before],
				[self._restore_parents, parent_list_before],
				[self._set_selection, sel_before]],
				[[self._set_layers_snapshot, after],
				[self._restore_parents, parent_list_after],
				[self._set_selection, sel_after]],
				False]
			self.add_undo(transaction)
			self.selection.update()

	def select_container(self):
		self.presenter.canvas.set_temp_mode(modes.PICK_MODE, self.set_container)

	def set_container(self, obj):
		if len(obj) == 1 and obj[0].cid > model.PRIMITIVE_CLASS and not \
		obj[0] in self.selection.objs:
			self.pack_container(obj[0])
			return False

		if not len(obj):
			first = _("There is no selected object.")
		elif obj[0] in self.selection.objs:
			first = _("Object from current selection cannot be container.")
		else:
			first = _("Selected object cannot be container.")

		second = _('Do you want to try again?')

		ret = dialogs.warning_dialog(self.app.mw, self.app.appdata.app_name,
				first, second,
				[(gtk.STOCK_NO, gtk.RESPONSE_CANCEL),
				(gtk.STOCK_YES, gtk.RESPONSE_OK)])

		if ret == gtk.RESPONSE_OK:
			return True
		return False

	def pack_container(self, container):
		if self.selection.objs:
			before = self._get_layers_snapshot()
			objs = [] + [container] + self.selection.objs
			sel_before = [] + self.selection.objs

			parent = container.parent
			group = model.Container(container.config, parent, objs)
			group.update()
			for obj in objs:
				obj.parent.childs.remove(obj)
			parent.childs.append(group)
			parent_list = []
			for obj in objs:
				parent_list.append([obj, obj.parent])
				obj.parent = group

			after = self._get_layers_snapshot()
			sel_after = [group]
			self.selection.set([group])
			transaction = [
				[[self._set_layers_snapshot, before],
				[self._restore_parents, parent_list],
				[self._set_selection, sel_before]],
				[[self._set_layers_snapshot, after],
				[self._set_parent, sel_after, group],
				[self._set_selection, sel_after]],
				False]
			self.add_undo(transaction)
			self.selection.update()

	def unpack_container(self):
		group = self.selection.objs[0]
		before = self._get_layers_snapshot()
		objs = [] + group.childs
		sel_before = [] + self.selection.objs
		parent = group.parent
		index = parent.childs.index(group)

		objs.reverse()
		parent.childs.remove(group)
		parent_list = []

		for obj in objs:
			parent.childs.insert(index, obj)
			obj.parent = parent
			parent_list.append([obj, group])

		after = self._get_layers_snapshot()
		sel_after = objs
		self.selection.set(sel_after)
		transaction = [
			[[self._set_layers_snapshot, before],
			[self._set_parent, sel_after, group],
			[self._set_selection, sel_before]],
			[[self._set_layers_snapshot, after],
			[self._restore_parents, parent_list],
			[self._set_selection, sel_after]],
			False]
		self.add_undo(transaction)
		self.selection.update()

	def combine_selected(self):
		before = self._get_layers_snapshot()
		sel_before = [] + self.selection.objs
		objs = self.selection.objs
		parent = objs[0].parent
		index = parent.childs.index(objs[0])

		style = deepcopy(objs[0].style)
		parent = objs[0].parent
		config = objs[0].config
		paths = []
		for obj in objs:
			paths += libgeom.get_transformed_path(obj)
		result = model.Curve(config, parent)
		result.paths = paths
		result.style = style
		result.update()

		for obj in objs:
			obj.parent.childs.remove(obj)

		parent.childs.insert(index, result)
		after = self._get_layers_snapshot()
		self.selection.set([result, ])
		transaction = [
			[[self._set_layers_snapshot, before],
			[self._set_selection, sel_before]],
			[[self._set_layers_snapshot, after],
			[self._set_selection, [result, ]]],
			False]
		self.add_undo(transaction)
		self.selection.update()


	def break_apart_selected(self):
		before = self._get_layers_snapshot()
		sel_before = [] + self.selection.objs
		obj = self.selection.objs[0]

		parent = obj.parent
		index = parent.childs.index(obj)
		config = obj.config

		paths = libgeom.get_transformed_path(obj)

		objs = []

		obj.parent.childs.remove(obj)
		for path in paths:
			if path and path[1]:
				curve = model.Curve(config, parent)
				curve.paths = [path, ]
				curve.style = deepcopy(obj.style)
				objs += [curve, ]
				parent.childs.insert(index, curve)
				curve.update()

		after = self._get_layers_snapshot()
		self.selection.set(objs)
		transaction = [
			[[self._set_layers_snapshot, before],
			[self._set_selection, sel_before]],
			[[self._set_layers_snapshot, after],
			[self._set_selection, objs]],
			False]
		self.add_undo(transaction)
		self.selection.update()

	def merge_doc(self, doc_presenter):
		objs = []
		layers = doc_presenter.methods.get_page().childs
		for layer in layers:
			for obj in [] + layer.childs:
				objs.append(obj)
				doc_presenter.methods.delete_object(obj)

		if objs:
			before = self._get_layers_snapshot()
			sel_before = [] + self.selection.objs

			self.presenter.active_layer.childs += objs
			self.presenter.active_layer.do_update()

			after = self._get_layers_snapshot()
			self.selection.set(objs)
			transaction = [
				[[self._set_layers_snapshot, before],
				[self._set_selection, sel_before]],
				[[self._set_layers_snapshot, after],
				[self._set_selection, objs]],
				False]
			self.add_undo(transaction)
			self.selection.update()


