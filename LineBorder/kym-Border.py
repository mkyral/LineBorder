#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright, V2.1
#
# Marian Kyral (mkyral@email.cz)
# (C) 2006, 2008, 2010, Frydek-Mistek, Czech
#
# This plugin was tested with Gimp 2.6
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#
# Changelog
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
    "Generate a line border around an image.",
    "Line border 2",
    "Marian Kyral (mkyral@email.cz)",
    "Copyright 2010, Marian Kyral, Czech",
    "12.10.2010",
    "<Image>/Filters/Decor/Borders/Line Border 2",
    "RGB*,GRAY*",
    [
      #(PF_IMAGE,      "The Image"    0),
      #(PF_DRAWABLE,   "The Layer"    0),
      #(PF_ADJUSTMENT, "total_width",      "Total border size (width in pixels)", 25, (0, 400, 1) ),
      #(PF_ADJUSTMENT, "total_height",     "Total border size (height in pixels)" , 25, (0, 400, 1) ),
      #(PF_ADJUSTMENT, "ext_botton",       "Extend bottom border (in pixels)" , 0, (0, 400, 1) ),
      #(PF_ADJUSTMENT, "inner_line",       "Inner line size (in pixels)" , 1, (0, 50, 1) ),
      #(PF_ADJUSTMENT, "dist_to_image",    "Distance to image (in pixels)" , 1, (0, 50, 1) ),
      #(PF_ADJUSTMENT, "outer_line",       "Outer line size (in pixels)" , 0, (0, 50, 1) ),
      #(PF_ADJUSTMENT ,"dist_to_border",   "Distance to border (in pixels)" , 1, (0, 50, 1) ),
      #(PF_TOGGLE,     "actual_colors",    "Use actual palette colors", False),
      #(PF_COLOR,      "line_color",       "Line color", (0, 0, 0) ),
      #(PF_COLOR,      "border_color",     "Border color", (255, 255, 255) ),
      #(PF_TOGGLE,     "feather_inner",    "Feather inner line", False),
      #(PF_FONT,       "InFont", "Font",    "Sans"),
      #(PF_STRING,     "left_text",        "Left text", "" ),
      #(PF_ADJUSTMENT, "left_text_size",   "Left text size", 25, (1, 400, 1) ),
      #(PF_STRING,     "center_text",      "Center text", "" ),
      #(PF_ADJUSTMENT, "center_text_size", "Center text size", 25, (1, 400, 1) ),
      #(PF_STRING,     "right_text",       "Right text", "" ),
      #(PF_ADJUSTMENT, "right_text_size",  "Right text size", 25, (1, 400, 1) ),
      #(PF_TOGGLE,     "flatten_image",    "Flatten image", True ),
      #(PF_TOGGLE,     "work_on_copy",     "Work on copy", False )
    ],
    [],
    plugin_main
    #  , menu="<Image>/Filters/Decor/Borders/Line Border 2"
    )

  main()

