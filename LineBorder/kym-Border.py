#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
from gimpfu import *

#
# Copyright, V2.0
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

#
# Define the function
#
def kym_Line_Border (InImage, InLayer, InOuterTotalWidth, InOuterTotalHeight, InExtBottomBorder,
                     InInnerSize, InDistanceImage, InOuterSize, InDistanceBorder, InUseSysColors,
                     InLineColor, InBorderColor, InFeather, InFont, InLeftText, InLeftTextSize,
                     InCenterText, InCenterTextSize, InRightText, InRightTextSize, InFlattenImage,
                     InWorkOnCopy) :
#
# define variables
#

  TheWidth = 0
  TheHeight = 0
  inner_border_width = 0
  inner_border_height = 0
  total_border_width = 0
  total_border_height = 0
  outer_border_width = 0
  outer_border_height = 0
  image_width = 0
  image_height = 0
  LeftTextLayer = 0
  LeftTextWidth = 0
  LeftTextHeight = 0
  CenterTextLayer = 0
  CenterTextWidth = 0
  CenterTextHeight = 0
  RightTextLayer = 0
  RightTextWidth = 0
  RightTextHeight = 0

  if InWorkOnCopy :
    TheImage = InImage.duplicate()
    pdb.gimp_image_undo_disable(TheImage)
    pdb.gimp_selection_none(TheImage)
  else :
    # work with original image
    TheImage = InImage
    pdb.gimp_image_undo_group_start(TheImage)
    pdb.gimp_selection_all(TheImage)

  # initial setting of variables
  TheLayer = pdb.gimp_image_flatten(TheImage)
  TheWidth = pdb.gimp_image_width(TheImage)
  TheHeight = pdb.gimp_image_height(TheImage)
  inner_border_width = InInnerSize
  inner_border_height = inner_border_width
  outer_border_width  = InOuterSize
  outer_border_height = outer_border_width
  total_border_width  = InOuterTotalWidth
  total_border_height = InOuterTotalHeight
  image_width = TheWidth + (2 * total_border_width)
  image_height = TheHeight + (2 * total_border_height)

  TheBackupColor = pdb.gimp_context_get_foreground()

  if InUseSysColors : # use system colors
    TheLineColor = pdb.gimp_context_get_foreground()
    TheBorderColor = pdb.gimp_context_get_background()
  else :
    TheLineColor = InLineColor
    TheBorderColor = InBorderColor

  TheLayer  = pdb.gimp_layer_copy(TheLayer, True)
  pdb.gimp_drawable_set_name(TheLayer, "With Border")

#
# Generate the border
#
  pdb.gimp_image_resize(TheImage, image_width, image_height, total_border_width, total_border_height)

  if InExtBottomBorder > 0  : # extend the bottom border
    image_height = image_height + InExtBottomBorder
    pdb.gimp_image_resize(TheImage, image_width, image_height, 0, 0)

  BorderLayer = pdb.gimp_layer_new(TheImage, image_width, image_height, RGBA_IMAGE, "TempLayer", 100, NORMAL_MODE)

  pdb.gimp_image_add_layer(TheImage, BorderLayer, -1)
  pdb.gimp_edit_clear(BorderLayer)

  pdb.gimp_rect_select(TheImage, 0, 0, image_width, image_height, CHANNEL_OP_REPLACE, False, 0)
  pdb.gimp_rect_select(TheImage, total_border_width, total_border_height, TheWidth, TheHeight, CHANNEL_OP_SUBTRACT, False, 0)
  pdb.gimp_palette_set_foreground(TheBorderColor)
  pdb.gimp_edit_fill(BorderLayer, FOREGROUND_FILL)
  #
  # Make the outer border line
  #
  if outer_border_width > 0 :
    pdb.gimp_rect_select(TheImage, InDistanceBorder,
                                   InDistanceBorder,
                         (image_width - (InDistanceBorder * 2)),
                         (image_height  - (InDistanceBorder * 2)),
                         CHANNEL_OP_REPLACE, InFeather, (1.2 * outer_border_width)
                        )

    pdb.gimp_rect_select(TheImage, total_border_width, total_border_height, TheWidth, TheHeight, CHANNEL_OP_SUBTRACT, False, 0)
    pdb.gimp_palette_set_foreground(TheLineColor)
    pdb.gimp_edit_fill(BorderLayer, FOREGROUND_FILL)

    pdb.gimp_rect_select(TheImage, (outer_border_width + InDistanceBorder),
                                   (outer_border_height + InDistanceBorder),
                        (image_width - ((outer_border_width * 2) + (InDistanceBorder * 2))),
                        (image_height - ((outer_border_height * 2) + (InDistanceBorder * 2))),
                         CHANNEL_OP_REPLACE, InFeather, (1.2 * outer_border_width)
                        )

    pdb.gimp_rect_select(TheImage, total_border_width, total_border_height, TheWidth, TheHeight, CHANNEL_OP_SUBTRACT, False, 0)
    pdb.gimp_palette_set_foreground(TheBorderColor)
    pdb.gimp_edit_fill(BorderLayer, FOREGROUND_FILL)
  #
  # Make the inner border line
  #
  if InInnerSize > 0 :
    pdb.gimp_rect_select(TheImage, (total_border_width - (inner_border_width + InDistanceImage)),
                                   (total_border_height - (inner_border_height + InDistanceImage)),
                        (image_width - ((total_border_width * 2) - ((inner_border_width + InDistanceImage) * 2)) ),
                        ((image_height - ((total_border_height * 2) - ((inner_border_width + InDistanceImage) * 2)) ) - InExtBottomBorder),
                         CHANNEL_OP_REPLACE, InFeather, (1.2 * inner_border_width)
                        )
    pdb.gimp_rect_select(TheImage, total_border_width, total_border_height, TheWidth, TheHeight, CHANNEL_OP_SUBTRACT, False, 0)
    pdb.gimp_palette_set_foreground(TheLineColor)
    pdb.gimp_edit_fill(BorderLayer, FOREGROUND_FILL)

  if InDistanceImage > 0 :
    pdb.gimp_rect_select(TheImage, (total_border_width - InDistanceImage),
                                   (total_border_height - InDistanceImage),
                        (image_width - ((total_border_width * 2) - (InDistanceImage * 2))),
                        ((image_height - ((total_border_height * 2) - (InDistanceImage * 2))) - InExtBottomBorder),
                         CHANNEL_OP_REPLACE, InFeather, (1.2 * inner_border_width)
                        )
    pdb.gimp_rect_select(TheImage, total_border_width, total_border_height, TheWidth, TheHeight, CHANNEL_OP_SUBTRACT, False, 0)
    pdb.gimp_palette_set_foreground(TheBorderColor)
    pdb.gimp_edit_fill(BorderLayer, FOREGROUND_FILL)
  #
  pdb.gimp_image_merge_down(TheImage, BorderLayer, CLIP_TO_IMAGE)
  pdb.gimp_selection_none(TheImage)

# Add text if entered
#
# Left text
#
  if InLeftText :
    pdb.gimp_palette_set_foreground(TheLineColor)
    # render text in new layer
    LeftTextLayer = pdb.gimp_text_fontname(TheImage, None, 0, 0, InLeftText, 0, True, InLeftTextSize, PIXELS, InFont)
    # get rendered text size
    LeftTextWidth = pdb.gimp_drawable_width(LeftTextLayer)
    LeftTextHeight = pdb.gimp_drawable_height(LeftTextLayer)
    # move text to correct position
    pdb.gimp_layer_resize(LeftTextLayer, LeftTextWidth, LeftTextHeight, 0, 0)
    pdb.gimp_layer_set_offsets(
      LeftTextLayer,
      total_border_width, # x
      # (((total_border_height + TheHeight) + 2 ) + InInnerSize ) # y - justify upper
      # (((image_height - 2 ) - InInnerSize ) - LeftTextHeight ) # y - justify down
      ((image_height - ((total_border_height + InExtBottomBorder ) / 2)) - (LeftTextHeight / 2)) # y - justify middle
      )
    pdb.gimp_layer_resize_to_image_size(LeftTextLayer)

#
# Center text
#
  if InCenterText :
    pdb.gimp_palette_set_foreground(TheLineColor)
    # render text in new layer
    CenterTextLayer = pdb.gimp_text_fontname(TheImage, None, 0, 0, InCenterText, 0, True, InCenterTextSize, PIXELS, InFont)
    # get rendered text size
    CenterTextWidth = pdb.gimp_drawable_width(CenterTextLayer)
    CenterTextHeight = pdb.gimp_drawable_height(CenterTextLayer)
    # move text to correct position
    pdb.gimp_layer_resize(CenterTextLayer, CenterTextWidth, CenterTextHeight, 0, 0)
    pdb.gimp_layer_set_offsets(
      CenterTextLayer,
      ((total_border_width + (TheWidth / 2)) - (CenterTextWidth / 2)), # x
      # (((total_border_height + TheHeight) + 2 ) + InInnerSize ) # y - justify upper
      # (((image_height - 2 ) - InInnerSize ) - CenterTextHeight ) # y - justify down
      ((image_height - ((total_border_height + InExtBottomBorder ) / 2)) - (CenterTextHeight / 2)) # y - justify middle
      )
    pdb.gimp_layer_resize_to_image_size(CenterTextLayer)

#
# Right text
#
  if InRightText :
    pdb.gimp_palette_set_foreground(TheLineColor)
    # render text in new layer
    RightTextLayer = pdb.gimp_text_fontname(TheImage, None, 0, 0, InRightText, 0, True, InRightTextSize, PIXELS, InFont)
    # get rendered text size
    RightTextWidth = pdb.gimp_drawable_width(RightTextLayer)
    RightTextHeight = pdb.gimp_drawable_height(RightTextLayer)
    # move text to correct position
    pdb.gimp_layer_resize(RightTextLayer, RightTextWidth, RightTextHeight, 0, 0)
    pdb.gimp_layer_set_offsets(
      RightTextLayer,
      (image_width - total_border_width - RightTextWidth ), # x
      # (((total_border_height + TheHeight) + 2 ) + InInnerSize ) # y - justify upper
      # (((image_height - 2 ) - InInnerSize ) - RightTextHeight ) # y - justify down
      ((image_height - ((total_border_height + InExtBottomBorder ) / 2)) - (RightTextHeight / 2)) # y - justify middle
      )
    pdb.gimp_layer_resize_to_image_size(RightTextLayer)

#
# Finish work
#
  if InFlattenImage :
    pdb.gimp_image_flatten(TheImage)

  if InWorkOnCopy :
    pdb.gimp_image_clean_all(TheImage)
    pdb.gimp_display_new(TheImage)
    pdb.gimp_image_undo_enable(TheImage)
  else :
    pdb.gimp_image_undo_group_end(TheImage)

  pdb.gimp_palette_set_foreground(TheBackupColor)
  pdb.gimp_displays_flush()
  return

#
# Register the function with the GIMP
#
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
    (PF_ADJUSTMENT, "total_width",      "Total border size (width in pixels)", 25, (0, 400, 1) ),
    (PF_ADJUSTMENT, "total_height",     "Total border size (height in pixels)" , 25, (0, 400, 1) ),
    (PF_ADJUSTMENT, "ext_botton",       "Extend bottom border (in pixels)" , 0, (0, 400, 1) ),
    (PF_ADJUSTMENT, "inner_line",       "Inner line size (in pixels)" , 1, (0, 50, 1) ),
    (PF_ADJUSTMENT, "dist_to_image",    "Distance to image (in pixels)" , 1, (0, 50, 1) ),
    (PF_ADJUSTMENT, "outer_line",       "Outer line size (in pixels)" , 0, (0, 50, 1) ),
    (PF_ADJUSTMENT ,"dist_to_border",   "Distance to border (in pixels)" , 1, (0, 50, 1) ),
    (PF_TOGGLE,     "actual_colors",    "Use actual palette colors", False),
    (PF_COLOR,      "line_color",       "Line color", (0, 0, 0) ),
    (PF_COLOR,      "border_color",     "Border color", (255, 255, 255) ),
    (PF_TOGGLE,     "feather_inner",    "Feather inner line", False),
    (PF_FONT,       "InFont", "Font",    "Sans"),
    (PF_STRING,     "left_text",        "Left text", "" ),
    (PF_ADJUSTMENT, "left_text_size",   "Left text size", 25, (1, 400, 1) ),
    (PF_STRING,     "center_text",      "Center text", "" ),
    (PF_ADJUSTMENT, "center_text_size", "Center text size", 25, (1, 400, 1) ),
    (PF_STRING,     "right_text",       "Right text", "" ),
    (PF_ADJUSTMENT, "right_text_size",  "Right text size", 25, (1, 400, 1) ),
    (PF_TOGGLE,     "flatten_image",    "Flatten image", True ),
    (PF_TOGGLE,     "work_on_copy",     "Work on copy", False )
  ],
  [],
  kym_Line_Border
#  , menu="<Image>/Filters/Decor/Borders/Line Border 2"
  )

main()

