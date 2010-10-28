#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#
# Copyright, V2.2
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

# create an output function that redirects to gimp's Error Console
def gprint( text ):
  pdb.gimp_message(text)
  return

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
    "Generate a line border around an image and optionaly place text on borders, inside the image.",
    "Line border 2.2",
    "Marian Kyral (mkyral@email.cz)",
    "Copyright 2010, Marian Kyral, Czech",
    "28.10.2010",
    "<Image>/Filters/Decor/Borders/Line Border 2",
    "RGB*,GRAY*",
    [],
    [],
    plugin_main
    #  , menu="<Image>/Filters/Decor/Borders/Line Border 2"
    )

  main()

