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

from lincutter import _, config

STOCK_ROTATE_LEFT = 'object-rotate-left'
STOCK_ROTATE_RIGHT = 'object-rotate-right'
STOCK_MOVE_TO_ORIGIN = 'object-move-to-origin'
STOCK_HOR_MIRROR = 'object-horizontal-mirror'
STOCK_VERT_MIRROR = 'object-vertical-mirror'
STOCK_MULTIPLY = 'object-multiply'

STOCK_CUTTING = 'action-cut'
STOCK_DONT_SAVE = 'action-dont-save'

def load_icons():
	items = [STOCK_ROTATE_LEFT, STOCK_ROTATE_RIGHT, STOCK_MOVE_TO_ORIGIN,
			STOCK_HOR_MIRROR, STOCK_VERT_MIRROR, STOCK_MULTIPLY]

	path = '' + os.path.join(config.resource_dir, 'icons')
	iconfactory = gtk.IconFactory()

	for item in items:
		gtk.stock_add([(item, '', 0, 0, ''), ])
		pixbuf = gtk.gdk.pixbuf_new_from_file(os.path.join(path, item + '.png'))
		source = gtk.IconSource()
		source.set_pixbuf(pixbuf)
		source.set_size_wildcarded(True)
		iconset = gtk.IconSet()
		iconset.add_source(source)
		iconfactory.add(item, iconset)

	#Creating aliased icons
	items = [(STOCK_CUTTING, _('_Cuttig'), 0, 0, None),
			(STOCK_DONT_SAVE, _("_Don't save"), 0, 0, None), ]

	aliases = [(STOCK_CUTTING, gtk.STOCK_PRINT),
			(STOCK_DONT_SAVE, gtk.STOCK_NO), ]

	gtk.stock_add(items)

	for item, alias in aliases:
		iconset = gtk.icon_factory_lookup_default(alias)
		iconfactory.add(item, iconset)

	iconfactory.add_default()


