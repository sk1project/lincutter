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

from uc2.formats.pdxf import model

class DocumentInspector:

	def __init__(self, app):
		self.app = app

	def is_doc(self):
		if self.app.docs:
			return True
		else:
			return False

	def is_not_doc(self):
		if self.app.docs:
			return False
		else:
			return True

	def is_doc_saved(self, doc=None):
		if doc:
			return doc.saved
		elif self.app.current_doc:
			return self.app.current_doc.saved
		else:
			return True

	def is_doc_not_saved(self, doc=None):
		return self.is_doc_saved(doc) != True

	def is_any_doc_not_saved(self):
		result = False
		if self.app.docs:
			for doc in self.app.docs:
				if not doc.saved:
					result = True
					break
		return result

	def is_undo(self, doc=None):
		if doc is None:
			doc = self.app.current_doc
		if doc is None:
			return False
		if doc.api.undo:
			return True
		else:
			return False

	def is_redo(self, doc=None):
		if doc is None:
			doc = self.app.current_doc
		if doc is None:
			return False
		if doc.api.redo:
			return True
		else:
			return False

	def is_history(self, doc=None):
		if doc is None:
			doc = self.app.current_doc
		if self.is_undo(doc) or self.is_redo(doc):
			return True
		else:
			return False

	def is_selection(self, doc=None):
		if doc is None:
			doc = self.app.current_doc
		if doc is None:
			return False
		elif doc.selection is None:
			return False
		elif doc.selection.objs:
			return True
		else:
			return False

	def is_clipboard(self):
		if self.app.clipboard.contents:
			return True
		else:
			return False

	def can_be_curve(self, doc=None):
		if doc is None:
			doc = self.app.current_doc
		if doc is None:
			return False
		elif self.is_selection(doc):
			result = False
			for obj in doc.selection.objs:
				if obj.cid > model.PRIMITIVE_CLASS and not obj.cid == model.CURVE:
					result = True
					break
			return result
		else:
			return False

	def can_be_grouped(self, doc=None):
		if doc is None:
			doc = self.app.current_doc
		if doc is None:
			return False
		elif self.is_selection(doc):
			result = False
			if len(doc.selection.objs) > 1:
				result = True
			return result
		else:
			return False

	def can_be_ungrouped(self, doc=None):
		if doc is None:
			doc = self.app.current_doc
		if doc is None:
			return False
		elif self.is_selection(doc)and len(doc.selection.objs) == 1:
			result = False
			if doc.selection.objs[0].cid == model.GROUP:
				result = True
			return result
		else:
			return False

	def can_be_ungrouped_all(self, doc=None):
		if doc is None:
			doc = self.app.current_doc
		if doc is None:
			return False
		elif self.is_selection(doc):
			result = False
			for obj in doc.selection.objs:
				if obj.cid == model.GROUP:
					result = True
					break
			return result
		else:
			return False

	def is_text_selected(self, doc=None):
		if doc is None:
			doc = self.app.current_doc
		if doc is None:
			return False
		elif self.is_selection(doc):
			result = False
			objs = doc.selection.objs
			cid = objs[0].cid
			if len(objs) == 1:
				if cid == model.TEXT_BLOCK or cid == model.TEXT_COLUMN:
					result = True
			return result
		else:
			return False

	def is_container_selected(self, doc=None):
		if doc is None:
			doc = self.app.current_doc
		if doc is None:
			return False
		elif self.is_selection(doc):
			result = False
			objs = doc.selection.objs
			cid = objs[0].cid
			if len(objs) == 1:
				if cid == model.CONTAINER:
					result = True
			return result
		else:
			return False

	def can_be_combined(self, doc=None):
		if doc is None:
			doc = self.app.current_doc
		if doc is None:
			return False
		elif self.is_selection(doc):
			result = True
			objs = doc.selection.objs
			if len(objs) < 2: return False
			for obj in objs:
				if obj.cid < model.PRIMITIVE_CLASS:
					result = False
					break
			return result
		else:
			return False

	def can_be_breaked(self, doc=None):
		if doc is None:
			doc = self.app.current_doc
		if doc is None:
			return False
		elif self.is_selection(doc):
			result = False
			objs = doc.selection.objs
			if len(objs) == 1 and objs[0].cid == model.CURVE:
				if len(objs[0].paths) > 1:
					result = True
			return result
		else:
			return False
