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

from lincutter import config

#Canvas mode enumeration
SELECT_MODE = 0
SHAPER_MODE = 1
ZOOM_MODE = 2
FLEUR_MODE = 3
PICK_MODE = 4
LINE_MODE = 10
CURVE_MODE = 11
RECT_MODE = 12
ELLIPSE_MODE = 13
TEXT_MODE = 14
POLYGON_MODE = 15
ZOOM_OUT_MODE = 16
MOVE_MODE = 17
COPY_MODE = 18
RESIZE_MODE = 19
RESIZE_MODE1 = 20
RESIZE_MODE2 = 21
RESIZE_MODE3 = 22
RESIZE_MODE4 = 23
RESIZE_MODE1_COPY = 24
RESIZE_MODE2_COPY = 25
RESIZE_MODE3_COPY = 26
RESIZE_MODE4_COPY = 27
RESIZE_MODE10 = 28
RESIZE_MODE11 = 29
RESIZE_MODE13 = 30
RESIZE_MODE10_COPY = 31
RESIZE_MODE11_COPY = 32
RESIZE_MODE13_COPY = 33


MODE_LIST = [SELECT_MODE, SHAPER_MODE, ZOOM_MODE, LINE_MODE,
			CURVE_MODE, RECT_MODE, ELLIPSE_MODE, TEXT_MODE,
			POLYGON_MODE, ZOOM_OUT_MODE, MOVE_MODE, RESIZE_MODE, ]

def get_cursors():
	cursors = {
			SELECT_MODE:('cur_std.png', (5, 5)),
			ZOOM_MODE:('cur_zoom_in.png', (6, 6)),
			FLEUR_MODE:('cur_fleur.png', (11, 4)),
			PICK_MODE:('cur_pick.png', (9, 2)),
			ZOOM_OUT_MODE:('cur_zoom_out.png', (6, 6)),
			MOVE_MODE:('cur_move.png', (5, 5)),
			COPY_MODE:('cur_copy.png', (5, 5)),
			RESIZE_MODE:('cur_center.png', (5, 5)),
			RESIZE_MODE1:('cur_resize1.png', (10, 10)),
			RESIZE_MODE1_COPY:('cur_resize1_copy.png', (10, 10)),
			RESIZE_MODE2:('cur_resize2.png', (10, 10)),
			RESIZE_MODE2_COPY:('cur_resize2_copy.png', (10, 10)),
			RESIZE_MODE3:('cur_resize3.png', (10, 10)),
			RESIZE_MODE3_COPY:('cur_resize3_copy.png', (10, 10)),
			RESIZE_MODE4:('cur_resize4.png', (10, 10)),
			RESIZE_MODE4_COPY:('cur_resize4_copy.png', (10, 10)),
			RESIZE_MODE10:('cur_resize10.png', (10, 10)),
			RESIZE_MODE10_COPY:('cur_resize10_copy.png', (10, 10)),
			RESIZE_MODE11:('cur_resize11.png', (10, 10)),
			RESIZE_MODE11_COPY:('cur_resize11_copy.png', (10, 10)),
			RESIZE_MODE13:('cur_resize13.png', (10, 10)),
			RESIZE_MODE13_COPY:('cur_resize13_copy.png', (10, 10)),
			}
	keys = cursors.keys()
	for key in keys:
		path = os.path.join(config.resource_dir, 'cursors', cursors[key][0])
		w, h = cursors[key][1]
		cursors[key] = gtk.gdk.Cursor(gtk.gdk.display_get_default(),
							gtk.gdk.pixbuf_new_from_file(path), w, h)
	return cursors
