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
# * ADD: Units could be pixels or %
# * ADD: Corner rounding
# * ADD: More text improvements:
#           Text on left, right side,on top
#           Support of more lines of text
#           Each text could have own font
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


import math
from gimpfu import *

#
# Helper functions
#

def smaller(a, b):
    if a < b :
      return a
    else :
      return b

def bigger(a, b):
    if a > b :
      return a
    else :
      return b

def recalc_units (InUnit, InValue, InBase):
    if InUnit == 'pixels' :
      return InValue
    else : # calculate percents
      if InValue == 0 :
        return 0
      else :
        return bigger(round((InBase * InValue / 100)), 1)

def degree2radians(degree):
    return degree * 0.0174532925
#
# Define the function
#
def LineBorder (InImage, InLayer,
                InOuterTotalWidth, InOuterTotalWidthUnit,
                InOuterTotalHeight, InOuterTotalHeightUnit,
                InExtBottomBorder, InExtBottomBorderUnit,
                InInnerSize, InInnerSizeUnit,
                InDistanceImage, InDistanceImageUnit,
                InOuterSize, InOuterSizeUnit,
                InDistanceBorder, InDistanceBorderUnit,
                InRoundOuter, InRoundOuterUnits,
                InRoundInner, InRoundInnerUnits,
                InUseSysColors, InLineColor, InBorderColor, InFeather,
                InLeftFont, InLeftTextSize, InLeftTextJustify, InLeftText,
                InCenterFont, InCenterTextSize, InCenterTextJustify, InCenterText,
                InRightFont, InRightTextSize, InRightTextJustify, InRightText,
                InTextPosition, InRotateText,
                InFlattenImage, InWorkOnCopy,
                InWmType, InWmOpacity, InWmRotation, InWmPosition,
                InWmDistToBorder, InWmDistToBorderUnits,
                InWmFontName, InWmFontSize,
                InWmJustify, InWmColor, InWmText, InWmImagePath
               ) :
#
# Inicialize variables
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
  ext_bottom = 0
  ext_upper = 0
  ext_left = 0
  ext_right = 0

  if InFeather == "Inner" or InFeather == "Both" :
     FeatherInner = True
  else :
     FeatherInner = False

  if InFeather == "Outer" or InFeather == "Both" :
     FeatherOuter = True
  else :
     FeatherOuter = False

  if InLeftTextJustify == "Center" :
    LeftTextJustify = TEXT_JUSTIFY_CENTER
  elif InLeftTextJustify == "Left" :
    LeftTextJustify = TEXT_JUSTIFY_LEFT
  elif InLeftTextJustify == "Right" :
    LeftTextJustify = TEXT_JUSTIFY_RIGHT
  else :
    LeftTextJustify = TEXT_JUSTIFY_FILL

  if InCenterTextJustify == "Center" :
    CenterTextJustify = TEXT_JUSTIFY_CENTER
  elif InCenterTextJustify == "Left" :
    CenterTextJustify = TEXT_JUSTIFY_LEFT
  elif InCenterTextJustify == "Right" :
    CenterTextJustify = TEXT_JUSTIFY_RIGHT
  else :
    CenterTextJustify = TEXT_JUSTIFY_FILL

  if InRightTextJustify == "Center" :
    RightTextJustify = TEXT_JUSTIFY_CENTER
  elif InRightTextJustify == "Left" :
    RightTextJustify = TEXT_JUSTIFY_LEFT
  elif InRightTextJustify == "Right" :
    RightTextJustify = TEXT_JUSTIFY_RIGHT
  else :
    RightTextJustify = TEXT_JUSTIFY_FILL

  if InWmJustify == "Center" :
    WmJustify = TEXT_JUSTIFY_CENTER
  elif InWmJustify == "Left" :
    WmJustify = TEXT_JUSTIFY_LEFT
  elif InWmJustify == "Right" :
    WmJustify = TEXT_JUSTIFY_RIGHT
  else :
    WmJustify = TEXT_JUSTIFY_FILL

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

  inner_border_width = recalc_units (InInnerSizeUnit, InInnerSize, smaller(TheWidth, TheHeight))
  inner_border_height = inner_border_width
  distance_to_image = recalc_units(InDistanceImageUnit, InDistanceImage, smaller(TheWidth, TheHeight))
  round_inner = recalc_units(InRoundInnerUnits, InRoundInner, smaller(TheWidth, TheHeight))

  outer_border_width  = recalc_units (InOuterSizeUnit, InOuterSize, smaller(TheWidth, TheHeight))
  outer_border_height = outer_border_width
  distance_to_border = recalc_units (InDistanceBorderUnit, InDistanceBorder, smaller(TheWidth, TheHeight))
  extent_border = recalc_units(InExtBottomBorderUnit, InExtBottomBorder, TheHeight)
  round_outer = recalc_units(InRoundOuterUnits, InRoundOuter, smaller(TheWidth, TheHeight))

  total_border_width  = recalc_units (InOuterTotalWidthUnit, InOuterTotalWidth, TheWidth)
  total_border_height = recalc_units (InOuterTotalHeightUnit, InOuterTotalHeight, TheHeight)
  image_width = TheWidth + (2 * total_border_width)
  image_height = TheHeight + (2 * total_border_height)

  wm_dist_to_border = recalc_units (InWmDistToBorderUnits, InWmDistToBorder, TheWidth)

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

  if extent_border > 0  : # extend the bottom border
    if InTextPosition == "Bottom":
      ext_bottom = extent_border
      image_height = image_height + ext_bottom
      pdb.gimp_image_resize(TheImage, image_width, image_height, 0, 0)
    elif InTextPosition == "Upper":
      ext_upper = extent_border
      image_height = image_height + ext_upper
      pdb.gimp_image_resize(TheImage, image_width, image_height, 0, ext_upper)
    elif InTextPosition == "Left":
      ext_left = extent_border
      image_width = image_width + ext_left
      pdb.gimp_image_resize(TheImage, image_width, image_height, ext_left, 0)
    else: # Right
      ext_right = extent_border
      image_width = image_width + ext_right
      pdb.gimp_image_resize(TheImage, image_width, image_height, 0, 0)

  BorderLayer = pdb.gimp_layer_new(TheImage, image_width, image_height, RGBA_IMAGE, "TempLayer", 100, NORMAL_MODE)

  pdb.gimp_image_add_layer(TheImage, BorderLayer, -1)
  pdb.gimp_edit_clear(BorderLayer)

  pdb.gimp_rect_select(TheImage, 0, 0, image_width, image_height, CHANNEL_OP_REPLACE, False, 0)
  pdb.gimp_rect_select(TheImage, total_border_width + ext_left, total_border_height + ext_upper, TheWidth, TheHeight, CHANNEL_OP_SUBTRACT, False, 0)
  pdb.gimp_palette_set_foreground(TheBorderColor)
  pdb.gimp_edit_fill(BorderLayer, FOREGROUND_FILL)
  #
  # Make the outer border line
  #
  if outer_border_width > 0 :
    pdb.gimp_round_rect_select(TheImage, distance_to_border,
                                   distance_to_border,
                         (image_width - (distance_to_border * 2)),
                         (image_height  - (distance_to_border * 2)),
                         round_inner, round_inner,
                         CHANNEL_OP_REPLACE, True, FeatherOuter, (1.2 * outer_border_width), (1.2 * outer_border_width)
                        )

    pdb.gimp_rect_select(TheImage,
                               total_border_width + ext_left, total_border_height + ext_upper,
                               TheWidth, TheHeight,
                               CHANNEL_OP_SUBTRACT, False, 0)
    pdb.gimp_palette_set_foreground(TheLineColor)
    pdb.gimp_edit_fill(BorderLayer, FOREGROUND_FILL)

    pdb.gimp_round_rect_select(TheImage, (outer_border_width + distance_to_border),
                                         (outer_border_height + distance_to_border),
                        (image_width - ((outer_border_width * 2) + (distance_to_border * 2))),
                        (image_height - ((outer_border_height * 2) + (distance_to_border * 2))),
                         round_inner, round_inner,
                         CHANNEL_OP_REPLACE, True,
                         FeatherOuter, (1.2 * outer_border_width),(1.2 * outer_border_width)
                        )

    pdb.gimp_rect_select(TheImage, total_border_width + ext_left, total_border_height + ext_upper, TheWidth, TheHeight, CHANNEL_OP_SUBTRACT, False, 0)
    pdb.gimp_palette_set_foreground(TheBorderColor)
    pdb.gimp_edit_fill(BorderLayer, FOREGROUND_FILL)
  #
  # Make the inner border line
  #
  if InInnerSize > 0 :
    pdb.gimp_round_rect_select(TheImage,
                                (total_border_width - (inner_border_width + distance_to_image) + ext_left),
                                (total_border_height - (inner_border_height + distance_to_image) + ext_upper),
                        (image_width - ((total_border_width * 2) - ((inner_border_width + distance_to_image) * 2)) - ext_left - ext_right),
                        ((image_height - ((total_border_height * 2) - ((inner_border_width + distance_to_image) * 2)) ) - ext_bottom - ext_upper),
                        round_outer, round_outer,
                         CHANNEL_OP_REPLACE, True, FeatherInner, (1.2 * inner_border_width), (1.2 * inner_border_width)
                        )
    pdb.gimp_rect_select(TheImage, total_border_width + ext_left, total_border_height + ext_upper, TheWidth, TheHeight, CHANNEL_OP_SUBTRACT, False, 0)
    pdb.gimp_palette_set_foreground(TheLineColor)
    pdb.gimp_edit_fill(BorderLayer, FOREGROUND_FILL)

    if distance_to_image > 0 :
      pdb.gimp_round_rect_select(TheImage,
                                  (total_border_width - distance_to_image + ext_left),
                                  (total_border_height - distance_to_image + ext_upper),
                          (image_width - ((total_border_width * 2) - (distance_to_image * 2)) - ext_left - ext_right),
                          ((image_height - ((total_border_height * 2) - (distance_to_image * 2))) - ext_bottom - ext_upper),
                          round_outer, round_outer,
                          CHANNEL_OP_REPLACE, True, FeatherInner, (1.2 * inner_border_width), (1.2 * inner_border_width)
                          )
      pdb.gimp_rect_select(TheImage, total_border_width + ext_left, total_border_height + ext_upper, TheWidth, TheHeight, CHANNEL_OP_SUBTRACT, False, 0)
      pdb.gimp_palette_set_foreground(TheBorderColor)
      pdb.gimp_edit_fill(BorderLayer, FOREGROUND_FILL)
  #
  if InFlattenImage :
    pdb.gimp_image_merge_down(TheImage, BorderLayer, CLIP_TO_IMAGE)
  pdb.gimp_selection_none(TheImage)

# Add text if entered
#
  outer_border_size = outer_border_height + distance_to_border
  inner_border_size = inner_border_height + distance_to_image
# Left text
#
  if InLeftText :
    pdb.gimp_palette_set_foreground(TheLineColor)
    # render text in new layer
    LeftTextLayer = pdb.gimp_text_layer_new(TheImage, InLeftText, InLeftFont, InLeftTextSize, PIXELS)
    pdb.gimp_image_add_layer(TheImage, LeftTextLayer, -1)
    pdb.gimp_text_layer_set_justification(LeftTextLayer, LeftTextJustify)
    # rotate text
    if ( InTextPosition == "Left" or InTextPosition == "Right") and InRotateText :
      LeftTextLayer = pdb.gimp_drawable_transform_rotate(LeftTextLayer, -1.570795, True, 0, 0, TRANSFORM_FORWARD, INTERPOLATION_CUBIC, False, 3, TRANSFORM_RESIZE_ADJUST )
    else :
      pdb.gimp_text_layer_set_antialias(LeftTextLayer, True)

    # get rendered text size
    LeftTextWidth = pdb.gimp_drawable_width(LeftTextLayer)
    LeftTextHeight = pdb.gimp_drawable_height(LeftTextLayer)
    # move text to correct position
    pdb.gimp_layer_resize(LeftTextLayer, LeftTextWidth, LeftTextHeight, 0, 0)
    if InTextPosition == "Bottom":
      x = bigger(total_border_width, 5)
      y = ((image_height -outer_border_size - ((total_border_height + ext_bottom - outer_border_size - inner_border_size ) / 2)) - (LeftTextHeight / 2))
    elif InTextPosition == "Upper":
      x = bigger(total_border_width, 5)
      y = outer_border_size + (((total_border_height + ext_upper - outer_border_size - inner_border_size) / 2) - (LeftTextHeight / 2))
    elif InTextPosition == "Left":
      x = outer_border_size + ((((total_border_width + extent_border) - (outer_border_size + inner_border_size)) / 2) - (LeftTextWidth / 2))
      y = bigger(total_border_height, 5)
    else : # InTextPosition == "Right"
      x = image_width - (outer_border_size + ((((total_border_width + extent_border)  - (outer_border_size + inner_border_size)) / 2) + (LeftTextWidth / 2)))
      y = bigger(total_border_height, 5)

    pdb.gimp_layer_set_offsets(LeftTextLayer, x, y)
    pdb.gimp_layer_resize_to_image_size(LeftTextLayer)

#
# Center text
#
  if InCenterText :
    pdb.gimp_palette_set_foreground(TheLineColor)
    # render text in new layer
    CenterTextLayer = pdb.gimp_text_layer_new(TheImage, InCenterText, InCenterFont, InCenterTextSize, PIXELS)
    pdb.gimp_image_add_layer(TheImage, CenterTextLayer, -1)
    pdb.gimp_text_layer_set_justification(CenterTextLayer, CenterTextJustify)
    # rotate text
    if ( InTextPosition == "Left" or InTextPosition == "Right") and InRotateText :
      CenterTextLayer = pdb.gimp_drawable_transform_rotate(CenterTextLayer, -1.570795, True, 0, 0, TRANSFORM_FORWARD, INTERPOLATION_CUBIC, False, 3, TRANSFORM_RESIZE_ADJUST )
    else :
      pdb.gimp_text_layer_set_antialias(CenterTextLayer, True)

    # get rendered text size
    CenterTextWidth = pdb.gimp_drawable_width(CenterTextLayer)
    CenterTextHeight = pdb.gimp_drawable_height(CenterTextLayer)
    # move text to correct position
    pdb.gimp_layer_resize(CenterTextLayer, CenterTextWidth, CenterTextHeight, 0, 0)
    if InTextPosition == "Bottom":
      x = ((total_border_width + (TheWidth / 2)) - (CenterTextWidth / 2))
      y = ((image_height -outer_border_size - ((total_border_height + ext_bottom - outer_border_size - inner_border_size ) / 2)) - (CenterTextHeight / 2))
    elif InTextPosition == "Upper":
      x = ((total_border_width + (TheWidth / 2)) - (CenterTextWidth / 2))
      y = outer_border_size + (((total_border_height + ext_upper - outer_border_size - inner_border_size) / 2) - (CenterTextHeight / 2))
    elif InTextPosition == "Left":
      x = outer_border_size + ((((total_border_width + extent_border) - (outer_border_size + inner_border_size)) / 2) - (CenterTextWidth / 2))
      y = ((total_border_height + (TheHeight / 2)) - (CenterTextHeight / 2))
    else : # InTextPosition == "Right"
      x = image_width - (outer_border_size + ((((total_border_width + extent_border)  - (outer_border_size + inner_border_size)) / 2) + (CenterTextWidth / 2)))
      y = ((total_border_height + (TheHeight / 2)) - (CenterTextHeight / 2))

    pdb.gimp_layer_set_offsets( CenterTextLayer, x, y )
    pdb.gimp_layer_resize_to_image_size(CenterTextLayer)

#
# Right text
#
  if InRightText :
    pdb.gimp_palette_set_foreground(TheLineColor)
    # render text in new layer
    RightTextLayer = pdb.gimp_text_layer_new(TheImage, InRightText, InRightFont, InRightTextSize, PIXELS)
    pdb.gimp_image_add_layer(TheImage, RightTextLayer, -1)
    pdb.gimp_text_layer_set_justification(RightTextLayer, RightTextJustify)
    # rotate text
    if ( InTextPosition == "Left" or InTextPosition == "Right") and InRotateText :
      RightTextLayer = pdb.gimp_drawable_transform_rotate(RightTextLayer, -1.570795, True, 0, 0, TRANSFORM_FORWARD, INTERPOLATION_CUBIC, False, 3, TRANSFORM_RESIZE_ADJUST )
    else :
      pdb.gimp_text_layer_set_antialias(RightTextLayer, True)

    # get rendered text size
    RightTextWidth = pdb.gimp_drawable_width(RightTextLayer)
    RightTextHeight = pdb.gimp_drawable_height(RightTextLayer)
    # move text to correct position
    pdb.gimp_layer_resize(RightTextLayer, RightTextWidth, RightTextHeight, 0, 0)
    if InTextPosition == "Bottom":
      x = (image_width - bigger(total_border_width, 5) - RightTextWidth )
      y = ((image_height -outer_border_size - ((total_border_height + ext_bottom - outer_border_size - inner_border_size ) / 2)) - (RightTextHeight / 2))
    elif InTextPosition == "Upper":
      x = (image_width - bigger(total_border_width, 5) - RightTextWidth )
      y = outer_border_size + (((total_border_height + ext_upper - outer_border_size - inner_border_size) / 2) - (RightTextHeight / 2))
    elif InTextPosition == "Left":
      x = outer_border_size + ((((total_border_width + extent_border) - (outer_border_size + inner_border_size)) / 2) - (RightTextWidth / 2))
      y = image_height - bigger(total_border_height, 5) - RightTextHeight
    else : # InTextPosition == "Right"
      x = image_width - (outer_border_size + ((((total_border_width + extent_border)  - (outer_border_size + inner_border_size)) / 2) + (RightTextWidth / 2)))
      y = image_height - bigger(total_border_height, 5) - RightTextHeight

    pdb.gimp_layer_set_offsets( RightTextLayer, x, y)
    pdb.gimp_layer_resize_to_image_size(RightTextLayer)

#
# WaterMark
#
  if ( InWmType == "text" and InWmText ) or ( InWmType == "image" and InWmImagePath ) :
    if ( InWmType == "text" and InWmText ) :
      # render text in new layer
      pdb.gimp_palette_set_foreground(InWmColor)
      WmLayer = pdb.gimp_text_layer_new(TheImage, InWmText, InWmFontName, InWmFontSize, PIXELS)
      pdb.gimp_image_add_layer(TheImage, WmLayer, -1)
      pdb.gimp_text_layer_set_justification(WmLayer, RightTextJustify)
      # rotate text
      if InWmRotation != 0 :
        WmLayer = pdb.gimp_drawable_transform_rotate(WmLayer, degree2radians(InWmRotation), True, 0, 0, TRANSFORM_FORWARD, INTERPOLATION_CUBIC, False, 3, TRANSFORM_RESIZE_ADJUST )
      else :
        pdb.gimp_text_layer_set_antialias(WmLayer, True)
    elif ( InWmType == "image" and InWmImagePath ) :
      # Load an image as a new layer
      WmLayer = pdb.gimp_file_load_layer(TheImage, InWmImagePath)
      pdb.gimp_image_add_layer(TheImage, WmLayer, -1)
      if InWmRotation != 0 :
        WmLayer = pdb.gimp_drawable_transform_rotate(WmLayer, degree2radians(InWmRotation), True, 0, 0, TRANSFORM_FORWARD, INTERPOLATION_CUBIC, False, 3, TRANSFORM_RESIZE_ADJUST )

    # get layer size
    WmLayerWidth = pdb.gimp_drawable_width(WmLayer)
    WmLayerHeight = pdb.gimp_drawable_height(WmLayer)

    # move text to correct position
    pdb.gimp_layer_resize(WmLayer, WmLayerWidth, WmLayerHeight, 0, 0)
    if   InWmPosition == "Upper-Left":
      x = total_border_width + wm_dist_to_border
      y = total_border_height + wm_dist_to_border
    elif InWmPosition == "Upper-Center":
      x = total_border_width + (TheWidth / 2) - (WmLayerWidth / 2)
      y = total_border_height + wm_dist_to_border
    elif InWmPosition == "Upper-Right":
      x = total_border_width + TheWidth - WmLayerWidth - wm_dist_to_border
      y = total_border_height + wm_dist_to_border
    if   InWmPosition == "Middle-Left":
      x = total_border_width + wm_dist_to_border
      y = total_border_height + (TheHeight / 2) - (WmLayerHeight / 2)
    elif InWmPosition == "Center":
      x = total_border_width + (TheWidth / 2) - (WmLayerWidth / 2)
      y = total_border_height + (TheHeight / 2) - (WmLayerHeight / 2)
    elif InWmPosition == "Middle-Right":
      x = total_border_width + TheWidth - WmLayerWidth - wm_dist_to_border
      y = total_border_height + (TheHeight / 2) - (WmLayerHeight / 2)
    if   InWmPosition == "Bottom-Left":
      x = total_border_width + wm_dist_to_border
      y = total_border_height + TheHeight - WmLayerHeight - wm_dist_to_border
    elif InWmPosition == "Bottom-Center":
      x = total_border_width + (TheWidth / 2) - (WmLayerWidth / 2)
      y = total_border_height + TheHeight - WmLayerHeight - wm_dist_to_border
    elif InWmPosition == "Bottom-Right":
      x = total_border_width + TheWidth - WmLayerWidth - wm_dist_to_border
      y = total_border_height + TheHeight - WmLayerHeight - wm_dist_to_border

    pdb.gimp_layer_set_offsets( WmLayer, x, y)
    pdb.gimp_layer_resize_to_image_size(WmLayer)
    pdb.gimp_layer_set_opacity(WmLayer, InWmOpacity)
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


