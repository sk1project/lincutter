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
from uc2 import libgeom


def _check_group(doc, group):
	for obj in [] + group.childs:
		_check_object(doc, obj)
	if not group.childs:
		doc.methods.delete_object(group)

def _check_object(doc, obj):
	if obj.cid < model.PRIMITIVE_CLASS:
		if obj.cid == model.GROUP:
			_check_group(doc, obj)
		else:
			doc.methods.delete_object(obj)

def simplify_doc(doc):
	#Other pages deleting
	page = doc.methods.get_page()
	page.parent.childs = [page, ]

	#Master layers merging
	master_layers = doc.methods.get_master_layers()
	if master_layers:
		page.childs += master_layers
		master_layers[0].parent.childs = []

	#Model update
	doc.update()

	#Unsupported and empty objects removing
	for layer in [] + page.childs:
		for obj in [] + layer.childs:
			_check_object(doc, obj)
		if not layer.childs and len(page.childs) > 1:
			doc.methods.delete_object(layer)

	#Collect all objects
	objs = []
	for layer in page.childs:
		for obj in layer.childs:
			objs.append(obj)

	if not objs: return False

	#Move to origin
	bbox = []
	bbox += objs[0].cache_bbox
	for obj in objs:
		bbox = libgeom.sum_bbox(bbox, obj.cache_bbox)

	dx = -bbox[0]
	dy = -bbox[1]

	trafo = [1.0, 0.0, 0.0, 1.0, dx, dy]
	for obj in objs:
		obj.apply_trafo(trafo)

	return True
