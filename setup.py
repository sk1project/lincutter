#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
#   Setup script for LinCutter
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
#
# Usage: 
# --------------------------------------------------------------------------
#  to build package:   python setup.py build
#  to install package:   python setup.py install
# --------------------------------------------------------------------------
#  to create source distribution:   python setup.py sdist
# --------------------------------------------------------------------------
#  to create binary RPM distribution:  python setup.py bdist_rpm
# --------------------------------------------------------------------------
#  to create binary DEB package:  python setup.py bdist_deb
# --------------------------------------------------------------------------
#
#  help on available distribution formats: python setup.py bdist --help-formats
#

import os, shutil, sys

DEBIAN = False
VERSION = '1.0'

############################################################
#
# File system utilities
#
############################################################

def get_dirs(path='.'):
	"""
	Return directory list for provided path
	"""
	list = []
	if path:
		if os.path.isdir(path):
			try:
				names = os.listdir(path)
			except os.error:
				return []
		names.sort()
		for name in names:
			if os.path.isdir(os.path.join(path, name)):
				list.append(name)
		return list

def get_dirs_withpath(path='.'):
	"""
	Return full  directory names list for provided path
	"""
	list = []
	names = []
	if os.path.isdir(path):
		try:
			names = os.listdir(path)
		except os.error:
			return names
	names.sort()
	for name in names:
		if os.path.isdir(os.path.join(path, name)) and not name == '.svn':
			list.append(os.path.join(path, name))
	return list

def get_files(path='.', ext='*'):
	"""
	Return file list for provided path
	"""
	list = []
	if path:
		if os.path.isdir(path):
			try:
				names = os.listdir(path)
			except os.error:
				return []
		names.sort()
		for name in names:
			if not os.path.isdir(os.path.join(path, name)):
				if ext == '*':
					list.append(name)
				elif '.' + ext == name[-1 * (len(ext) + 1):]:
					list.append(name)
	return list

def get_files_withpath(path='.', ext='*'):
	"""
	Return full file names list for provided path
	"""
	import glob
	list = glob.glob(os.path.join(path, "*." + ext))
	list.sort()
	result = []
	for file in list:
		if os.path.isfile(file):
			result.append(file)
	return result

def get_dirs_tree(path='.'):
	"""
	Return recursive directories list for provided path
	"""
	tree = get_dirs_withpath(path)
	res = [] + tree
	for node in tree:
		subtree = get_dirs_tree(node)
		res += subtree
	return res

def get_files_tree(path='.', ext='*'):
	"""
	Return recursive files list for provided path
	"""
	tree = []
	dirs = [path, ]
	dirs += get_dirs_tree(path)
	for dir in dirs:
		list = get_files_withpath(dir, ext)
		list.sort()
		tree += list
	return tree

############################################################
#
# Main build procedure
#
############################################################

if __name__ == "__main__":

	if len(sys.argv) > 1 and sys.argv[1] == 'bdist_deb':
		DEBIAN = True
		sys.argv[1] = 'build'

	from distutils.core import setup, Extension

	share_dirs = []

	for item in ['share/*.*',
				'share/icons/*.*',
				'share/icons/tools/*.*',
				'share/cursors/*.*', ]:
		share_dirs.append(item)

	print share_dirs

	setup (name='lincutter',
			version=VERSION,
			description='Vector graphics editor for cutting plotters',
			author='Igor E. Novikov',
			author_email='igor.e.novikov@gmail.com',
			maintainer='Igor E. Novikov',
			maintainer_email='igor.e.novikov@gmail.com',
			license='GPL v3',
			url='http://sk1project.org',
			download_url='http://sk1project.org/modules.php?name=Products',
			long_description='''
LinCutter is an open source vector graphics editor for cutting plotters similar 
to Roland CutStudio, Artcut, or PostCut. The software is designed for HPGL 
compatible cutting plotters.
sK1 Project (http://sk1project.org), copyright (C) 2011-2012 by Igor E. Novikov.
			''',
		classifiers=[
			'Development Status :: 6 - Mature',
			'Environment :: Desktop',
			'Intended Audience :: End Users/Desktop',
			'License :: OSI Approved :: GPL v3',
			'Operating System :: POSIX',
			'Operating System :: MacOS :: MacOS X',
			'Programming Language :: Python',
			"Topic :: Multimedia :: Graphics :: Editors :: Vector-Based",
			],

			packages=['lincutter',
				'lincutter.context',
				'lincutter.dialogs',
				'lincutter.dialogs.prefs',
				'lincutter.view',
				'lincutter.widgets',
			],

			package_dir={'lincutter': 'src/lincutter',
			},

			package_data={'lincutter': share_dirs,
			},

			scripts=['lincutter'],

			data_files=[
					('/usr/share/applications', ['src/lincutter.desktop', ]),
					('/usr/share/pixmaps', ['src/lincutter.png', 'src/lincutter.xpm', ]),
					],
			)

#################################################
# .py source compiling
#################################################
if sys.argv[1] == 'build':
	import compileall
	compileall.compile_dir('build/')


#################################################
# Implementation of bdist_deb command
#################################################
if DEBIAN:
	print '\nDEBIAN PACKAGE BUILD'
	print '===================='
	import string, platform
	version = (string.split(sys.version)[0])[0:3]

	arch, bin = platform.architecture()
	if arch == '64bit':
		arch = 'amd64'
	else:
		arch = 'i386'

	target = 'build/deb-root/usr/lib/python' + version + '/dist-packages'

	if os.path.lexists(os.path.join('build', 'deb-root')):
		os.system('rm -rf build/deb-root')
	os.makedirs(os.path.join('build', 'deb-root', 'DEBIAN'))

	os.system("cat debian/control |sed 's/<PLATFORM>/" + arch + "/g'|sed 's/<VERSION>/" + VERSION + "/g'> build/deb-root/DEBIAN/control")

	os.makedirs(target)
	os.makedirs('build/deb-root/usr/bin')
	os.makedirs('build/deb-root/usr/share/applications')
	os.makedirs('build/deb-root/usr/share/pixmaps')

	os.system('cp -R build/lib.linux-' + platform.machine() + '-' + version + '/lincutter ' + target)
	os.system('cp src/lincutter.desktop build/deb-root/usr/share/applications')
	os.system('cp src/lincutter.png build/deb-root/usr/share/pixmaps')
	os.system('cp src/lincutter.xpm build/deb-root/usr/share/pixmaps')
	os.system('cp lincutter build/deb-root/usr/bin')
	os.system('chmod +x build/deb-root/usr/bin/lincutter')

	if os.path.lexists('dist'):
		os.system('rm -rf dist/*.deb')
	else:
		os.makedirs('dist')

	os.system('dpkg --build build/deb-root/ dist/python-lincutter-' + VERSION + '_' + arch + '.deb')
