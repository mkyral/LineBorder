#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#
# Copyright, V2.3
#
# Marian Kyral (mkyral@email.cz)
# (C) 2006, 2008, 2010, Frydek-Mistek, Czech Republic
#
# This plugin was tested with Gimp 2.6
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

#
# Changelog
#
# 31.10.2010 - v2.3
# * CHANGE: gui improvements
# * ADD: Inner/Outer line flag
# * ADD: border rounding
# * ADD: localization support (cs, nl)
# * CHANGE: correct issues with extreme values
#           (e.g.: border width = 0 - a panorama style)
#
# 28.10.2010 - v2.2
# * ADD: allow to put sign/watermark inside the image
#
# 25.10.2010 - v2.1
# * CHANGE: use own glade dialog
# * CHANGE: remember plugin setting between sessions
# * CHANGE: Text could have more lines
# * ADD: posibility to place text on sides and on upper border
# * ADD: sizes could be in pixels or in percents
# * ADD: corner rounding
#
# 12.10.2010 - v2.0
# * Initial conversion to python
#
# 08.10.2008 - v1.4
# * CHANGE: Fixed to work with gimp 2.6
#
# 12.07.2008 - v1.3
# * CHANGE: Outer line size is independent on inner line size
# * ADD: Distance between inner line and image
# * ADD: Distance between outer line and border
#
# 13.06.2008 - v1.2
# * ADD: The size of the bottom border can be extended
# * ADD: Text in the border
#

import os, locale, gettext

APP = "LineBorder"               #name of the translation file
PO_DIR = os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)),APP), 'locale')

locale.setlocale(locale.LC_ALL, '')
gettext.install(APP, PO_DIR, unicode=True)

def plugin_main(TheImage, TheDrawable):
    import LineBorder.gui  # import package that is meat of plugin
    app = LineBorder.gui.LineBorderApp(TheImage, TheDrawable)  # create instance of gtkBuilder app
    app.main()  # event loop for app

#
# Register the function with the GIMP
#
if __name__ == "__main__":
  from gimpfu import *
  register(
    "python-fu-Line-Border",
    _("Generate a line border around an image and optionaly place text on borders and inside the image."),
    _("Generate a line border around an image and optionaly place text on borders and inside the image."),
    "Marian Kyral (mkyral@email.cz)",
    "Copyright 2010, Marian Kyral, Czech Republic",
    "28.10.2010",
    "<Image>/Filters/Decor/Borders/Line border 2",
    "RGB*,GRAY*",
    [],
    [],
    plugin_main #, menu="<Image>/Filters/Decor/Borders"
    )

  main()

