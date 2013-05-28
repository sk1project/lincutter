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

import os, shutil

from uc2.uc_conf import UCConfig
from uc2.utils import system
from uc2.utils.fs import expanduser_unicode
from uc2.uc2const import cm_to_pt
from uc2 import uc2const
from uc2.formats.pdxf.const import DOC_STRUCTURE
from uc2.cms import libcms

from lincutter import events

class AppData:

	app_name = 'LinCutter'
	app_proc = 'lincutter'
	app_org = 'sK1 Project'
	app_domain = 'sk1project.org'
	app_icon = None
	doc_icon = None
	version = "1.0"

	def __init__(self):
		#Check config root directory
		self.app_config_dir = expanduser_unicode(os.path.join('~', '.config', 'lincutter'))
		if not os.path.lexists(self.app_config_dir):
			os.makedirs(self.app_config_dir)

		#Check color profiles directory	
		self.app_color_profile_dir = os.path.join(self.app_config_dir, 'profiles')
		if not os.path.lexists(self.app_color_profile_dir):
			os.makedirs(self.app_color_profile_dir)

		for item in uc2const.COLORSPACES + [uc2const.COLOR_DISPLAY, ]:
			filename = 'built-in_%s.icm' % item
			path = os.path.join(self.app_color_profile_dir, filename)
			if not os.path.lexists(path):
				libcms.cms_save_default_profile(path, item)


		#Check clipboard directory
		self.app_clipboard_dir = os.path.join(self.app_config_dir, 'clipboard')
		if not os.path.lexists(self.app_clipboard_dir):
			os.makedirs(self.app_clipboard_dir)
		for item in DOC_STRUCTURE:
			path = os.path.join(self.app_clipboard_dir, item)
			if not os.path.lexists(path):
				os.makedirs(path)

		#Config file path 
		self.app_config = os.path.join(self.app_config_dir, 'preferences.cfg')


class AppConfig(UCConfig):

	def __setattr__(self, attr, value):
		if not hasattr(self, attr) or getattr(self, attr) != value:
			self.__dict__[attr] = value
			events.emit(events.CONFIG_MODIFIED, attr, value)

	#============== GENERIC SECTION ===================
	system_encoding = 'utf-8'	# default encoding (GUI uses utf-8 only)
	actual_version = "1.0"

	default_unit = uc2const.UNIT_CM
	tolerance = 0.5
	new_doc_on_start = True
	#============== UI SECTION ===================
	mw_maximized = 0

	mw_width = 1000
	mw_height = 700

	mw_min_width = 1000
	mw_min_height = 700

	show_splash = 1

	set_doc_icon = 1

	#-----------------CANVAS---------------------------
	desktop_color = [0.95, 0.95, 0.95]
	axes_color = [0.0, 0.0, 1.0]
	page_color = [1.0, 1.0, 1.0]
	page_border_color = [1.0, 0.0, 0.0]
	paths_color = [0.196, 0.329, 0.635]

	sel_frame_offset = 10.0
	sel_frame_color = (0.0, 0.0, 0.0)
	sel_frame_dash = [5, 5]

	sel_marker_size = 9.0
	sel_marker_frame_color = (0.0, 0.0, 0.0)
	sel_marker_frame_dash = [5, 5]
	sel_marker_fill = (1.0, 1.0, 1.0)
	sel_marker_stroke = (0.0, 0.3, 1.0)

	rotation_step = 5.0 #in degrees
	stroke_sensitive_size = 5.0 #in pixels
	#-----------------RULERS---------------------------
	ruler_style = 0
	ruler_min_tick_step = 3
	ruler_min_text_step = 50
	ruler_max_text_step = 100

	# 0 - page center
	# 1 - lower-left page corner
	# 2 - upper-left page corner 
	ruler_coordinates = 0
	#--------------------------------------------------

	#============== PLOTTER SECTION ==============

	plotter_name = 'Generic plotter'
	plotter_page_height = 50.0 * cm_to_pt
	plotter_page_width = 200.0 * cm_to_pt

	#============== I/O SECTION ===================
	open_dir = '~'
	save_dir = '~'
	import_dir = '~'
	export_dir = '~'
	make_backup = True
	resource_dir = ''
	output_file = '~/plotter.plt'
	cut_bbox = False
	#=============== Release check ================
	allow_release_check = True
	check_counter = 0
	check_timestamp = 1333831234

	def __init__(self, path):
		pass




class LinuxConfig(AppConfig):
	os = system.LINUX

class MacosxConfig(AppConfig):
	os = system.MACOSX
	mw_maximized = 0
	set_doc_icon = 0
	ruler_style = 0

class WinConfig(AppConfig):
	os = system.WINDOWS
	ruler_style = 0



def get_app_config(path):
	os_family = system.get_os_family()
	if os_family == system.MACOSX:
		return MacosxConfig(path)
	elif os_family == system.WINDOWS:
		return WinConfig(path)
	else:
		return LinuxConfig(path)
