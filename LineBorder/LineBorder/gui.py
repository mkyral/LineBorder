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

import math
from gimpfu import *

import os, ConfigParser
try:
  import gtk, gtk.glade
except ImportError,  e :
  self.on_error(_("Libraries not found!"), _("The Gtk or Glade library not found.\nCheck your installation please!\n"+str(e)))

try:
  import pygtk
  pygtk.require("2.0")
except ImportError,  e :
  self.on_error(_("Libraries not found!"), _("The pygtk library not found.\nCheck your installation please!\n"+str(e)))

from LineBorder import LineBorder
from . import LineBorderProfile

import locale, gettext

APP = "LineBorder"               #name of the translation file
PO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'locale')

locale.setlocale(locale.LC_ALL, '')
gettext.install(APP, PO_DIR, unicode=True)
gtk.glade.bindtextdomain(APP,PO_DIR)
gtk.glade.textdomain(APP)

UI_FILENAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'LineBorder.glade')

# Combobox values - do not store translated strings in configuration file
UNITS = ['pixels', '%']
FEATHER = ['None', 'Inner', 'Outer', 'Both']
JUSTIFY = ['Center', 'Left', 'Right', 'Block']
TEXT_POSITION = ['Bottom', 'Upper', 'Left', 'Right']
WM_POSITION = ['Upper-Left', 'Upper-Center', 'Upper-Right', 'Middle-Left', 'Center', 'Middle-Right', 'Bottom-Left', 'Bottom-Center', 'Bottom-Right']

class LineBorderApp():
  def __init__(self, Image = None, Drawable = None):
      if not os.path.exists(UI_FILENAME):
        print _("Cannot find the glade file: ") + UI_FILENAME
        self.on_error(_("No dialog file found!"), _("Sorry, the dialog file LineBorder.glade was not found.\nCheck your installation please!"))
        return

      builder = gtk.Builder()
      builder.add_from_file(UI_FILENAME)
      builder.connect_signals(self)

      self.image = Image
      self.drawable = Drawable
      self.dialog = builder.get_object("window1")
      self.about = builder.get_object("aboutdialog1")

      self.border_width = builder.get_object("spinbutton_width")
      self.border_width_units = builder.get_object("combobox_units_width")
      self.border_height = builder.get_object("spinbutton_height")
      self.border_height_units = builder.get_object("combobox_units_height")
      self.border_ext_text = builder.get_object("spinbutton_ext_text")
      self.border_ext_text_units = builder.get_object("combobox_units_ext_text")
      self.border_inner_border_round = builder.get_object("spinbutton_border_round_inner")
      self.border_inner_border_round_units = builder.get_object("combobox_units_border_round_inner")
      self.border_outer_border_round = builder.get_object("spinbutton_border_round_outer")
      self.border_outer_border_round_units = builder.get_object("combobox_units_border_round_outer")

      self.border_inner_line = builder.get_object("checkbutton_inner_line")
      self.border_inner_size = builder.get_object("spinbutton_inner_size")
      self.border_inner_size_units = builder.get_object("combobox_units_inner")
      self.border_inner_round = builder.get_object("spinbutton_inner_round")
      self.border_inner_round_units = builder.get_object("combobox_units_inner_round")
      self.border_dist_to_image = builder.get_object("spinbutton_dist_to_image")
      self.border_dist_to_image_units = builder.get_object("combobox_units_dist_to_image")

      self.border_outer_line = builder.get_object("checkbutton_outer_line")
      self.border_outer_size = builder.get_object("spinbutton_outer_size")
      self.border_outer_size_units = builder.get_object("combobox_units_outer")
      self.border_outer_round = builder.get_object("spinbutton_outer_round")
      self.border_outer_round_units = builder.get_object("combobox_units_outer_round")
      self.border_dist_to_border = builder.get_object("spinbutton_dist_to_border")
      self.border_dist_to_border_units = builder.get_object("combobox_units_dist_to_border")

      self.actual_pallete_colors = builder.get_object("checkbutton_actual_palette")
      self.line_color = builder.get_object("line_color")
      self.border_color = builder.get_object("border_color")

      self.feather_line = builder.get_object("combobox_feather_line")
      self.flatten_image = builder.get_object("checkbutton_flatten_image")
      self.work_on_copy = builder.get_object("checkbutton_work_on_copy")

      self.label_border_inner_size = builder.get_object("label_inner_size")
      self.label_border_dist_to_image = builder.get_object("label_dist_to_image")
      self.label_border_inner_round = builder.get_object("label_inner_round")
      self.label_border_outer_size = builder.get_object("label_outer_size")
      self.label_border_dist_to_border = builder.get_object("label_dist_to_border")
      self.label_border_outer_round = builder.get_object("label_outer_round")

      self.left_text_font = builder.get_object("fontbutton_left")
      self.left_text_justify = builder.get_object("combobox_left_justify")
      self.left_text = builder.get_object("textview_left")

      self.center_text_font = builder.get_object("fontbutton_center")
      self.center_text_justify = builder.get_object("combobox_center_justify")
      self.center_text = builder.get_object("textview_center")

      self.right_text_font = builder.get_object("fontbutton_right")
      self.right_text_justify = builder.get_object("combobox_right_justify")
      self.right_text = builder.get_object("textview_right")

      self.text_position = builder.get_object("combobox_text_position")
      self.rotate_text = builder.get_object("checkbutton_rotate_text")

      self.label_line_color = builder.get_object("label12")
      self.label_border_color = builder.get_object("label13")
      self.label_rotate_text = builder.get_object("label24")

      self.wm_type_text = builder.get_object('radiobutton_wm_text')
      self.wm_type_image = builder.get_object('radiobutton_wm_image')
      self.wm_opacity = builder.get_object('spinbutton_wm_opacity')
      self.wm_rotation = builder.get_object('spinbutton_wm_rotation')
      self.wm_position = builder.get_object('combobox_wm_position')
      self.wm_dist_to_border = builder.get_object('spinbutton_wm_dist_to_border')
      self.wm_dist_to_border_units = builder.get_object('combobox_wm_dist_to_border_units')
      self.wm_font = builder.get_object('fontbutton_wm_font')
      self.wm_justify = builder.get_object('combobox_wm_justify')
      self.wm_color = builder.get_object('colorbutton_wm_color')
      self.wm_text = builder.get_object('textview_wm_text')
      self.wm_image_path = builder.get_object('entry_wm_image_path')

      self.label_wm_font = builder.get_object('label_wm_font')
      self.label_wm_justify = builder.get_object('label_wm_justify')
      self.label_wm_color = builder.get_object('label_wm_color')
      self.button_wm_file_open = builder.get_object('button_wm_file_open')

      # Initialize profiles
      self.profile_list = LineBorderProfile.LineBorderProfileList()
      self.profile_list.configFile = os.path.join(gimp.directory, "LineBorder.cfg")
      self.profile_list.loadProfiles()
      self.default_profile = self.profile_list.profiles['DEFAULT']

      if not self.apply_profile(self.default_profile) :
        # Workaround :-/ (http://www.listware.net/201004/gtk-app-devel-list/88663-default-values-for-spin-buttons-in-glade.html)
        self.border_width.set_value(25)
        self.border_height.set_value(25)
        self.border_inner_size.set_value(1)
        self.border_dist_to_image.set_value(1)
        self.border_dist_to_border.set_value(1)
        self.wm_opacity.set_value(25)
        self.wm_dist_to_border.set_value(5)

      self.dialog.show()

  def main(self):
      gtk.main()  # event loop

  def on_button_about_clicked(self, widget):
      self.about.show()

  def on_aboutdialog1_destroy(self, widget, responseID = None):
      widget.hide()

  def on_error(self, title, text = None):
      md = gtk.MessageDialog(None,
           gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR,
           gtk.BUTTONS_CLOSE, title)
      md.format_secondary_text(text)
      md.run()
      md.destroy()

  def combobox_get_id_from_desc(self, inSeq, inDesc):
      i = 0
      while i < len(inSeq):
        if inSeq[i] == inDesc :
          return i
        i = i + 1
      return 0

  def on_checkbutton_actual_palette_toggled (self, widget):
      if self.actual_pallete_colors.get_active() == True:
        self.line_color.set_sensitive(False)
        self.border_color.set_sensitive(False)
        self.label_line_color.set_sensitive(False)
        self.label_border_color.set_sensitive(False)
      else:
        self.line_color.set_sensitive(True)
        self.border_color.set_sensitive(True)
        self.label_line_color.set_sensitive(True)
        self.label_border_color.set_sensitive(True)

  def on_combobox_text_position_changed(self, widget):
      active = self.text_position.get_active()
      if active == self.combobox_get_id_from_desc(TEXT_POSITION, "Left") or \
         active == self.combobox_get_id_from_desc(TEXT_POSITION, "Right") :
        self.rotate_text.set_sensitive(True)
        self.label_rotate_text.set_sensitive(True)
      else:
        self.rotate_text.set_sensitive(False)
        self.label_rotate_text.set_sensitive(False)

  def on_radiobutton_wm_text_toggled(self, widget):
      if self.wm_type_text.get_active() == True:
         self.wm_image_path.set_sensitive(False)
         self.button_wm_file_open.set_sensitive(False)

         self.wm_font.set_sensitive(True)
         self.wm_justify.set_sensitive(True)
         self.wm_color.set_sensitive(True)
         self.wm_text.set_sensitive(True)
         self.label_wm_font.set_sensitive(True)
         self.label_wm_justify.set_sensitive(True)
         self.label_wm_color.set_sensitive(True)
      else:
         self.wm_image_path.set_sensitive(True)
         self.button_wm_file_open.set_sensitive(True)

         self.wm_font.set_sensitive(False)
         self.wm_justify.set_sensitive(False)
         self.wm_color.set_sensitive(False)
         self.wm_text.set_sensitive(False)
         self.label_wm_font.set_sensitive(False)
         self.label_wm_justify.set_sensitive(False)
         self.label_wm_color.set_sensitive(False)

  def on_button_wm_file_open_clicked(self, widget):
      chooser = gtk.FileChooserDialog (
                      title=_('Open image'),
                      action=gtk.FILE_CHOOSER_ACTION_OPEN,
                      buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK)
                    )

      if self.wm_image_path.get_text():
        chooser.set_filename(self.wm_image_path.get_text())

      filter = gtk.FileFilter()
      filter.set_name(_("Images") + " (*.png, *.jpg, *.gif, *.tif, *.svg, *.xpm)")
      filter.add_mime_type("image/png")
      filter.add_mime_type("image/jpeg")
      filter.add_mime_type("image/gif")
      filter.add_mime_type("image/svg")
      filter.add_pattern("*.png")
      filter.add_pattern("*.jpg")
      filter.add_pattern("*.gif")
      filter.add_pattern("*.tif")
      filter.add_pattern("*.xpm")
      filter.add_pattern("*.svg")
      chooser.add_filter(filter)

      response = chooser.run()
      if response == gtk.RESPONSE_OK:
          self.wm_image_path.set_text(chooser.get_filename())
      elif response == gtk.RESPONSE_CANCEL:
          pass
      chooser.destroy()

  def on_checkbutton_inner_line_toggled(self, widget):
      state = self.border_inner_line.get_active()
      self.border_inner_size.set_sensitive(state)
      self.border_inner_size_units.set_sensitive(state)
      self.border_inner_round.set_sensitive(state)
      self.border_inner_round_units.set_sensitive(state)
      self.border_dist_to_image.set_sensitive(state)
      self.border_dist_to_image_units.set_sensitive(state)
      self.label_border_inner_size.set_sensitive(state)
      self.label_border_dist_to_image.set_sensitive(state)
      self.label_border_inner_round.set_sensitive(state)

  def on_checkbutton_outer_line_toggled(self, widget):
      state = self.border_outer_line.get_active()
      self.border_outer_size.set_sensitive(state)
      self.border_outer_size_units.set_sensitive(state)
      self.border_outer_round.set_sensitive(state)
      self.border_outer_round_units.set_sensitive(state)
      self.border_dist_to_border.set_sensitive(state)
      self.border_dist_to_border_units.set_sensitive(state)
      self.label_border_outer_size.set_sensitive(state)
      self.label_border_dist_to_border.set_sensitive(state)
      self.label_border_outer_round.set_sensitive(state)

  def on_button_ok_clicked(self, widget):
      self.call_LineBorder()
      gtk.main_quit()

  def on_window1_destroy(self, widget):
      gtk.main_quit()

  #  --- Utils ---
  # extract font name form the FontButton
  def extract_font_name (self, inFont):
      delim = " "
      delim_idx = inFont.rfind(delim)
      if delim_idx >= 0 :
         return inFont[0: delim_idx]
      else :
         return ""

  # extract font size form the FontButton
  def extract_font_size (self, inFont):
      delim = " "
      delim_idx = inFont.rfind(delim)
      if delim_idx >= 0 :
         return inFont[delim_idx + 1: len(inFont)]
      else :
         return ""

  # extract text from the TextView
  def extract_text (self, inTextView):
      buff = inTextView.get_buffer()
      (iter_first, iter_last) = buff.get_bounds()
      return buff.get_text(iter_first, iter_last)

  # return the integer value of a hexadecimal string s
  def hex2dec(self, s):
      return int(s, 16)

  # extract color definition (r,g,b)
  def extract_color (self, inColor):
      red_hexa = inColor.to_string()[1:3]
      green_hexa = inColor.to_string()[5:7]
      blue_hexa = inColor.to_string()[9:11]
      return (self.hex2dec(red_hexa), self.hex2dec(green_hexa), self.hex2dec(blue_hexa))

  # get watermark type (text or image)
  def get_wm_type(self):
      if self.wm_type_text.get_active() == True :
        return "text"
      else :
        return "image"

  # Extract parameters, call main function
  def call_LineBorder(self):
      image = self.image
      drawable = self.drawable

      self.parse_form_values(self.default_profile)
      self.profile_list.saveProfiles()

      if self.default_profile.wmType == 'image' and self.default_profile.wmImagePath :
        if not os.path.exists(wm_image_path.decode('unicode_escape')):
          print _("Cannot find the image file:") + " " + self.default_profile.wmImagePath
          self.on_error(_("File does not exists!"), _("The watermark image file:") + "\n\n" + self.default_profile.wmImagePath + "\n\n" + _("does not exists or is not readable!\n"))
          return

      d = self.default_profile
      LineBorder ( image, drawable,
                   d.width, d.widthUnits,
                   d.height, d.heightUnits,
                   d.extText, d.extTextUnits,
                   d.roundInnerBorder, d.roundInnerBorderUnits,
                   d.roundOuterBorder, d.roundOuterBorderUnits,
                   d.innerLine, d.innerSize, d.innerUnits,
                   d.distToImage, d.distToImageUnits,
                   d.outerLine, d.outerSize, d.outerUnits,
                   d.distToBorder, d.distToBorderUnits,
                   d.innerRound, d.innerRoundUnits,
                   d.outerRound, d.outerRoundUnits,
                   d.actualPallete, d.lineColor,d. borderColor, d.featherLine,
                   d.leftTextFont, d.leftTextFontSize, d.leftTextJustify, d.leftText,
                   d.centerTextFont, d.centerTextFontSize, d.centerTextJustify, d.centerText,
                   d.rightTextFont, d.rightTextFontSize, d.rightTextJustify, d.rightText,
                   d.textPosition, d.rotateText,
                   d.flattenImage, d.workOnCopy,
                   d.wmType, d.wmOpacity, d.wmRotation, d.wmPosition,
                   d.wmDistToBorder, d.wmDistToBorderUnits,
                   d.wmFontName, d.wmFontSize,
                   d.wmJustify, d.wmColor, d.wmText, d.wmImagePath
                 )
      gtk.main_quit()


  # Add text to the TextView
  def set_text (self, inTextView, inText):
      buff = inTextView.get_buffer()
      buff.set_text(inText)

  def apply_profile(self, profile):
      # Section: Border
      if 'all' in profile.sections or 'border' in profile.sections :
        self.border_width.set_value(profile.width)
        self.border_width_units.set_active(self.combobox_get_id_from_desc(UNITS, profile.widthUnits))
        self.border_height.set_value(profile.height)
        self.border_height_units.set_active(self.combobox_get_id_from_desc(UNITS, profile.heightUnits))
        self.border_ext_text.set_value(profile.extText)
        self.border_ext_text_units.set_active(self.combobox_get_id_from_desc(UNITS, profile.extTextUnits))
        self.border_inner_border_round.set_value(profile.roundInnerBorder)
        self.border_inner_border_round_units.set_active(self.combobox_get_id_from_desc(UNITS, profile.roundInnerBorderUnits))
        self.border_outer_border_round.set_value(profile.roundOuterBorder)
        self.border_outer_border_round_units.set_active(self.combobox_get_id_from_desc(UNITS, profile.roundOuterBorderUnits))
        self.border_inner_line.set_active(profile.innerLine)
        self.border_inner_size.set_value(profile.innerSize)
        self.border_inner_size_units.set_active(self.combobox_get_id_from_desc(UNITS, profile.innerUnits))
        self.border_inner_round.set_value(profile.innerRound)
        self.border_inner_round_units.set_active(self.combobox_get_id_from_desc(UNITS, profile.innerRoundUnits))
        self.border_dist_to_image.set_value(profile.distToImage)
        self.border_dist_to_image_units.set_active(self.combobox_get_id_from_desc(UNITS, profile.distToImageUnits))
        self.border_outer_line.set_active(profile.outerLine)
        self.border_outer_size.set_value(profile.outerSize)
        self.border_outer_size_units.set_active(self.combobox_get_id_from_desc(UNITS, profile.outerUnits))
        self.border_outer_round.set_value(profile.outerRound)
        self.border_outer_round_units.set_active(self.combobox_get_id_from_desc(UNITS, profile.outerRoundUnits))
        self.border_dist_to_border.set_value(profile.distToBorder)
        self.border_dist_to_border_units.set_active(self.combobox_get_id_from_desc(UNITS, profile.distToBorderUnits))
        self.feather_line.set_active(self.combobox_get_id_from_desc(FEATHER, profile.featherLine))

      if 'all' in profile.sections or 'color' in profile.sections :
        self.actual_pallete_colors.set_active(profile.actualPallete)
        self.line_color.set_color(profile.lineColor)
        self.border_color.set_color(profile.borderColor)

      if 'all' in profile.sections or 'text' in profile.sections :
        # Left text
        self.left_text_font.set_font_name(profile.leftTextFont + " " + str(profile.leftTextFontSize))
        self.left_text_justify.set_active(self.combobox_get_id_from_desc(JUSTIFY, profile.leftTextJustify))
        self.set_text(self.left_text, profile.leftText)
        # Center text
        self.center_text_font.set_font_name(profile.centerTextFont + " " + str(profile.centerTextFontSize))
        self.center_text_justify.set_active(self.combobox_get_id_from_desc(JUSTIFY, profile.centerTextJustify))
        self.set_text(self.center_text, profile.centerText)
        # Right text
        self.right_text_font.set_font_name(profile.rightTextFont + " " + str(profile.rightTextFontSize))
        self.right_text_justify.set_active(self.combobox_get_id_from_desc(JUSTIFY, profile.rightTextJustify))
        self.set_text(self.right_text, profile.rightText)

        self.text_position.set_active(self.combobox_get_id_from_desc(TEXT_POSITION, profile.textPosition))
        self.rotate_text.set_active(profile.rotateText)

      # Section: general
      if 'all' in profile.sections or 'general' in profile.sections :
        # Section: General
        self.flatten_image.set_active(profile.flattenImage)
        self.work_on_copy.set_active(profile.workOnCopy)

      # Section: Watermark
      if 'all' in profile.sections or 'wm' in profile.sections :
        if profile.wmType == 'text':
          self.wm_type_text.set_active(True)
          self.on_radiobutton_wm_text_toggled(self.dialog) # trigger call on_radiobutton_wm_text_toggled()
        else:
          self.wm_type_image.set_active(True)

      self.wm_opacity.set_value(profile.wmOpacity)
      self.wm_rotation.set_value(profile.wmRotation)
      self.wm_position.set_active(self.combobox_get_id_from_desc(WM_POSITION, profile.wmPosition))
      self.wm_dist_to_border.set_value(profile.wmDistToBorder)
      self.wm_dist_to_border_units.set_active(self.combobox_get_id_from_desc(UNITS, profile.wmDistToBorderUnits))
      self.wm_font.set_font_name(profile.wmFontName + " " + str(profile.wmFontSize))
      self.wm_justify.set_active(self.combobox_get_id_from_desc(JUSTIFY, profile.wmJustify))
      self.wm_color.set_color(profile.wmColor)
      self.set_text(self.wm_text, profile.wmText)
      self.wm_image_path.set_text(profile.wmImagePath)

      return True

  def parse_form_values(self, profile):
      # Border tab
      profile.width = self.border_width.get_value()
      profile.widthUnits = UNITS[self.border_width_units.get_active()]
      profile.height = self.border_height.get_value()
      profile.heightUnits = UNITS[self.border_height_units.get_active()]
      profile.extText = self.border_ext_text.get_value()
      profile.extTextUnits = UNITS[self.border_ext_text_units.get_active()]
      profile.roundInnerBorder = self.border_inner_border_round.get_value()
      profile.roundInnerBorderUnits = UNITS[self.border_inner_border_round_units.get_active()]
      profile.roundOuterBorder = self.border_outer_border_round.get_value()
      profile.roundOuterBorderUnits = UNITS[self.border_outer_border_round_units.get_active()]

      profile.innerLine = self.border_inner_line.get_active()
      profile.innerSize = self.border_inner_size.get_value()
      profile.innerUnits = UNITS[self.border_inner_size_units.get_active()]
      profile.innerRound = self.border_inner_round.get_value()
      profile.innerRoundUnits = UNITS[self.border_inner_round_units.get_active()]
      profile.distToImage = self.border_dist_to_image.get_value()
      profile.distToImageUnits = UNITS[self.border_dist_to_image_units.get_active()]

      profile.outerLine = self.border_outer_line.get_active()
      profile.outerSize = self.border_outer_size.get_value()
      profile.outerUnits = UNITS[self.border_outer_size_units.get_active()]
      profile.outerRound = self.border_outer_round.get_value()
      profile.outerRoundUnits = UNITS[self.border_outer_round_units.get_active()]
      profile.distToBorder = self.border_dist_to_border.get_value()
      profile.distToBorderUnits = UNITS[self.border_dist_to_border_units.get_active()]

      profile.actualPallete = self.actual_pallete_colors.get_active()
      profile.lineColor = self.extract_color(self.line_color.get_color())
      profile.borderColor = self.extract_color(self.border_color.get_color())
      profile.featherLine = FEATHER[self.feather_line.get_active()]
      profile.flattenImage = self.flatten_image.get_active()
      profile.workOnCopy = self.work_on_copy.get_active()

      # Text tab
      profile.leftTextFont = self.extract_font_name(self.left_text_font.get_font_name())
      profile.leftTextFontSize = self.extract_font_size(self.left_text_font.get_font_name())
      profile.leftTextJustify = JUSTIFY[self.left_text_justify.get_active()]
      profile.leftText = self.extract_text(self.left_text)
      profile.centerTextFont = self.extract_font_name(self.center_text_font.get_font_name())
      profile.centerTextFontSize = self.extract_font_size(self.center_text_font.get_font_name())
      profile.centerTextJustify = JUSTIFY[self.center_text_justify.get_active()]
      profile.centerText = self.extract_text(self.center_text)
      profile.rightTextFont = self.extract_font_name(self.right_text_font.get_font_name())
      profile.rightTextFontSize = self.extract_font_size(self.right_text_font.get_font_name())
      profile.rightTextJustify = JUSTIFY[self.right_text_justify.get_active()]
      profile.rightText = self.extract_text(self.right_text)
      profile.textPosition = TEXT_POSITION[self.text_position.get_active()]
      profile.rotateText = self.rotate_text.get_active()

      # Watermark tab
      profile.wmType = self.get_wm_type()
      profile.wmOpacity = self.wm_opacity.get_value()
      profile.wmRotation = self.wm_rotation.get_value()
      profile.wmPosition = WM_POSITION[self.wm_position.get_active()]
      profile.wmDistToBorder = self.wm_dist_to_border.get_value()
      profile.wmDistToBorderUnits = UNITS[self.wm_dist_to_border_units.get_active()]
      profile.wmFontName = self.extract_font_name(self.wm_font.get_font_name())
      profile.wmFontSize = self.extract_font_size(self.wm_font.get_font_name())
      profile.wmJustify = JUSTIFY[self.wm_justify.get_active()]
      profile.wmColor =  self.extract_color(self.wm_color.get_color())
      profile.wmText = self.extract_text(self.wm_text)
      profile.wmImage_path = self.wm_image_path.get_text()

