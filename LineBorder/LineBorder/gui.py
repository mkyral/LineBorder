#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
from gimpfu import *

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

import os
import ConfigParser
import gtk
import gtk.glade
import pygtk
pygtk.require("2.0")
import locale, gettext


from LineBorder import LineBorder

APP = "LineBorder"               #name of the translation file
#DIR = gimp.locale_directory     #locale dir of gimp
#DIR=os.path.join(os.path.dirname()

#locale.setlocale(locale.LC_ALL, '')
#gettext.install(APP, DIR, unicode=True)
#gtk.glade.bindtextdomain(APP,DIR)
#gtk.glade.textdomain(APP)

UI_FILENAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'LineBorder.glade')

class LineBorderApp():
  def __init__(self, Image = None, Drawable = None):
      if not os.path.exists(UI_FILENAME):
        print "Cannot find the glade file: " + UI_FILENAME
        self.on_error("No dialog file found!", "Sorry, the dialog file LineBorder.glade was not found.\nCheck your installation please!")
        return

      builder = gtk.Builder()
      builder.add_from_file(UI_FILENAME)
      builder.connect_signals(self)

      self.image = Image
      self.drawable = Drawable
      self.dialog = builder.get_object("window1")
      self.about = builder.get_object("aboutdialog1")
      self.alert = builder.get_object("alertdialog")

      self.border_width = builder.get_object("spinbutton_width")
      self.border_width_units = builder.get_object("combobox_units_width")
      self.border_height = builder.get_object("spinbutton_height")
      self.border_height_units = builder.get_object("combobox_units_height")
      self.border_ext_text = builder.get_object("spinbutton_ext_text")
      self.border_ext_text_units = builder.get_object("combobox_units_ext_text")
      self.border_inner_size = builder.get_object("spinbutton_inner_size")
      self.border_inner_size_units = builder.get_object("combobox_units_inner")
      self.border_inner_round = builder.get_object("spinbutton_inner_round")
      self.border_inner_round_units = builder.get_object("combobox_units_inner_round")
      self.border_dist_to_image = builder.get_object("spinbutton_dist_to_image")
      self.border_dist_to_image_units = builder.get_object("combobox_units_dist_to_image")
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

      # Config file
      self.config_dir = gimp.directory
      self.config_file = os.path.join(self.config_dir, "LineBorder.cfg")

      if not self.load_config('DEFAULT') :
        # Workaround :-/ (http://www.listware.net/201004/gtk-app-devel-list/88663-default-values-for-spin-buttons-in-glade.html)
        self.border_width.set_value(25)
        self.border_height.set_value(25)
        self.border_inner_size.set_value(1)
        self.border_dist_to_image.set_value(1)
        self.border_dist_to_border.set_value(1)

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
      active = self.text_position.get_active_text()
      if active == "Left" or active == "Right" :
        self.rotate_text.set_sensitive(True)
        self.label_rotate_text.set_sensitive(True)
      else:
        self.rotate_text.set_sensitive(False)
        self.label_rotate_text.set_sensitive(False)

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

  # Extract parameters, call main function
  def call_LineBorder(self):
      image = self.image
      drawable = self.drawable
      width = self.border_width.get_value()
      width_units = self.border_width_units.get_active_text()
      height = self.border_height.get_value()
      height_units = self.border_height_units.get_active_text()
      ext_text = self.border_ext_text.get_value()
      ext_text_units = self.border_ext_text_units.get_active_text()

      inner_size = self.border_inner_size.get_value()
      inner_units = self.border_inner_size_units.get_active_text()
      inner_round = self.border_inner_round.get_value()
      inner_round_units = self.border_inner_round_units.get_active_text()
      dist_to_image = self.border_dist_to_image.get_value()
      dist_to_image_units = self.border_dist_to_image_units.get_active_text()

      outer_size = self.border_outer_size.get_value()
      outer_units = self.border_outer_size_units.get_active_text()
      outer_round = self.border_outer_round.get_value()
      outer_round_units = self.border_outer_round_units.get_active_text()
      dist_to_border = self.border_dist_to_border.get_value()
      dist_to_border_units = self.border_dist_to_border_units.get_active_text()

      actual_pallete = self.actual_pallete_colors.get_active()
      line_color = self.extract_color(self.line_color.get_color())
      border_color = self.extract_color(self.border_color.get_color())
      feather_line = self.feather_line.get_active_text()
      flatten_image = self.flatten_image.get_active()
      work_on_copy = self.work_on_copy.get_active()

      left_text_font = self.extract_font_name(self.left_text_font.get_font_name())
      left_text_font_size = self.extract_font_size(self.left_text_font.get_font_name())
      left_text_justify = self.left_text_justify.get_active_text()
      left_text = self.extract_text(self.left_text)
      center_text_font = self.extract_font_name(self.center_text_font.get_font_name())
      center_text_font_size = self.extract_font_size(self.center_text_font.get_font_name())
      center_text_justify = self.center_text_justify.get_active_text()
      center_text = self.extract_text(self.center_text)
      right_text_font = self.extract_font_name(self.right_text_font.get_font_name())
      right_text_font_size = self.extract_font_size(self.right_text_font.get_font_name())
      right_text_justify = self.right_text_justify.get_active_text()
      right_text = self.extract_text(self.right_text)
      text_position = self.text_position.get_active_text()
      rotate_text = self.rotate_text.get_active()

      self.save_config( 'DEFAULT', width, width_units,
                        height, height_units,
                        ext_text, ext_text_units,
                        inner_size, inner_units,
                        dist_to_image, dist_to_image_units,
                        outer_size, outer_units,
                        dist_to_border, dist_to_border_units,
                        inner_round, inner_round_units,
                        outer_round, outer_round_units,
                        actual_pallete, line_color, border_color, feather_line,
                        left_text_font, left_text_font_size, left_text_justify, left_text,
                        center_text_font, center_text_font_size, center_text_justify, center_text,
                        right_text_font, right_text_font_size, right_text_justify, right_text,
                        text_position, rotate_text,
                        flatten_image, work_on_copy)

      LineBorder ( image, drawable,
                   width, width_units,
                   height, height_units,
                   ext_text, ext_text_units,
                   inner_size, inner_units,
                   dist_to_image, dist_to_image_units,
                   outer_size, outer_units,
                   dist_to_border, dist_to_border_units,
                   inner_round, inner_round_units,
                   outer_round, outer_round_units,
                   actual_pallete, line_color, border_color, feather_line,
                   left_text_font, left_text_font_size, left_text_justify, left_text,
                   center_text_font, center_text_font_size, center_text_justify, center_text,
                   right_text_font, right_text_font_size, right_text_justify, right_text,
                   text_position, rotate_text,
                   flatten_image, work_on_copy
                 )
      gtk.main_quit()

  def profile_sections(self, profile):
      sec_border = profile +':' + 'border'
      sec_color = profile +':' + 'color'
      sec_text = profile +':' + 'text'
      sec_general = profile +':' + 'general'
      return sec_border, sec_color, sec_text, sec_general

  # Save plugin options for nex time
  def save_config(self, profile, width, width_units,
                        height, height_units,
                        ext_text, ext_text_units,
                        inner_size, inner_units,
                        dist_to_image, dist_to_image_units,
                        outer_size, outer_units,
                        dist_to_border, dist_to_border_units,
                        inner_round, inner_round_units,
                        outer_round, outer_round_units,
                        actual_pallete, line_color, border_color, feather_line,
                        left_text_font, left_text_font_size, left_text_justify, left_text,
                        center_text_font, center_text_font_size, center_text_justify, center_text,
                        right_text_font, right_text_font_size, right_text_justify, right_text,
                        text_position, rotate_text,
                        flatten_image, work_on_copy):

      sec_border, sec_color, sec_text, sec_general = self.profile_sections(profile)

      cfg = ConfigParser.RawConfigParser()
      cfg.add_section(sec_border)
      cfg.set (sec_border, 'width', width)
      cfg.set (sec_border, 'width_units', width_units)
      cfg.set (sec_border, 'height', height)
      cfg.set (sec_border, 'height_units', height_units)
      cfg.set (sec_border, 'ext_text', ext_text)
      cfg.set (sec_border, 'ext_text_units', ext_text_units)
      cfg.set (sec_border, 'inner_size', inner_size)
      cfg.set (sec_border, 'inner_units', inner_units)
      cfg.set (sec_border, 'dist_to_image', dist_to_image)
      cfg.set (sec_border, 'dist_to_image_units', dist_to_image_units)
      cfg.set (sec_border, 'inner_round', inner_round)
      cfg.set (sec_border, 'inner_round_units', inner_round_units)
      cfg.set (sec_border, 'outer_size', outer_size)
      cfg.set (sec_border, 'outer_units', outer_units)
      cfg.set (sec_border, 'outer_round', outer_round)
      cfg.set (sec_border, 'outer_round_units', outer_round_units)
      cfg.set (sec_border, 'dist_to_border', dist_to_border)
      cfg.set (sec_border, 'dist_to_border_units', dist_to_border_units)
      cfg.set (sec_border, 'feather_line', feather_line)

      cfg.add_section(sec_color)
      cfg.set (sec_color, 'actual_pallete', actual_pallete)
      cfg.set (sec_color, 'line_color.r', line_color[0])
      cfg.set (sec_color, 'line_color.g', line_color[1])
      cfg.set (sec_color, 'line_color.b', line_color[2])
      cfg.set (sec_color, 'border_color.r', border_color[0])
      cfg.set (sec_color, 'border_color.g', border_color[1])
      cfg.set (sec_color, 'border_color.b', border_color[2])

      cfg.add_section(sec_text)
      cfg.set (sec_text, 'left_text_font', left_text_font)
      cfg.set (sec_text, 'left_text_font_size', left_text_font_size)
      cfg.set (sec_text, 'left_text_justify', left_text_justify)
      cfg.set (sec_text, 'left_text', left_text.replace('\n','.\n'))
      cfg.set (sec_text, 'center_text_font', center_text_font)
      cfg.set (sec_text, 'center_text_font_size', center_text_font_size)
      cfg.set (sec_text, 'center_text_justify', center_text_justify)
      cfg.set (sec_text, 'center_text', center_text.replace('\n','.\n'))
      cfg.set (sec_text, 'right_text_font', right_text_font)
      cfg.set (sec_text, 'right_text_font_size', right_text_font_size)
      cfg.set (sec_text, 'right_text_justify', right_text_justify)
      cfg.set (sec_text, 'right_text', right_text.replace('\n','.\n'))
      cfg.set (sec_text, 'text_position', text_position)
      cfg.set (sec_text, 'rotate_text', rotate_text)
      cfg.add_section(sec_general)
      cfg.set (sec_general, 'flatten_image', flatten_image)
      cfg.set (sec_general, 'work_on_copy', work_on_copy)
      with open(self.config_file, 'wb') as configfile:
          cfg.write(configfile)

      return True

  def set_combobox (self, inCBox, inText) :
      #print "set_combobox: " + text
      tm = inCBox.get_model()
      tm_len = len(tm)
      i = 0
      while i <= tm_len :
        if tm.get_value(tm.get_iter(i),0) == inText :
          inCBox.set_active_iter(tm.get_iter(i))
          break
        i += 1

  # extract text from the TextView
  def set_text (self, inTextView, inText):
      buff = inTextView.get_buffer()
      buff.set_text(inText)

  def load_config(self, profile):

      if not os.path.exists(self.config_file):
        return False
      else :
        try:

          #if not os.access(self.config_file, os.R_OK) :
              #print "ERROR: cannot read from file " + self.config_file
              #return False

          sec_border, sec_color, sec_text, sec_general = self.profile_sections(profile)

          cfg = ConfigParser.RawConfigParser()
          cfg.read(self.config_file)

          try:
            try:
              width = cfg.getfloat(sec_border, 'width')
              width_units = cfg.get(sec_border, 'width_units')
              self.border_width.set_value(width)
              self.set_combobox(self.border_width_units, width_units)
            except ConfigParser.NoOptionError, err:
              pass
            except ValueError, err:
              pass

            try:
              height = cfg.getfloat(sec_border, 'height')
              height_units = cfg.get(sec_border, 'height_units')
              self.border_height.set_value(height)
              self.set_combobox(self.border_height_units, height_units)
            except ConfigParser.NoOptionError, err:
              pass
            except ValueError, err:
              pass

            try:
              ext_text = cfg.getfloat(sec_border, 'ext_text')
              ext_text_units = cfg.get(sec_border, 'ext_text_units')
              self.border_ext_text.set_value(ext_text)
              self.set_combobox(self.border_ext_text_units, ext_text_units)
            except ConfigParser.NoOptionError, err:
              pass
            except ValueError, err:
              pass

            try:
              inner_size = cfg.getfloat(sec_border, 'inner_size')
              inner_units = cfg.get(sec_border, 'inner_units')
              self.border_inner_size.set_value(inner_size)
              self.set_combobox(self.border_inner_size_units, inner_units)
            except ConfigParser.NoOptionError, err:
              pass
            except ValueError, err:
              pass

            try:
              inner_round = cfg.getfloat(sec_border, 'inner_round')
              inner_round_units = cfg.get(sec_border, 'inner_round_units')
              self.border_inner_round.set_value(inner_round)
              self.set_combobox(self.border_inner_round_units, inner_round_units)
            except ConfigParser.NoOptionError, err:
              pass
            except ValueError, err:
              pass

            try:
              dist_to_image = cfg.getfloat(sec_border, 'dist_to_image')
              dist_to_image_units = cfg.get(sec_border, 'dist_to_image_units')
              self.border_dist_to_image.set_value(dist_to_image)
              self.set_combobox(self.border_dist_to_image_units, dist_to_image_units)
            except ConfigParser.NoOptionError, err:
              pass
            except ValueError, err:
              pass

            try:
              outer_size = cfg.getfloat(sec_border, 'outer_size')
              outer_units = cfg.get(sec_border, 'outer_units')
              self.border_outer_size.set_value(outer_size)
              self.set_combobox(self.border_outer_size_units, outer_units)
            except ConfigParser.NoOptionError, err:
              pass
            except ValueError, err:
              pass

            try:
              outer_round = cfg.getfloat(sec_border, 'outer_round')
              outer_round_units = cfg.get(sec_border, 'outer_round_units')
              self.border_outer_round.set_value(outer_round)
              self.set_combobox(self.border_outer_round_units, outer_round_units)
            except ConfigParser.NoOptionError, err:
              pass
            except ValueError, err:
              pass

            try:
              dist_to_border = cfg.getfloat(sec_border, 'dist_to_border')
              dist_to_border_units = cfg.get(sec_border, 'dist_to_border_units')
              self.border_dist_to_border.set_value(dist_to_border)
              self.set_combobox(self.border_dist_to_border_units, dist_to_border_units)
            except ConfigParser.NoOptionError, err:
              pass
            except ValueError, err:
              pass

            try:
              feather_line = cfg.get(sec_border, 'feather_line')
              self.set_combobox(self.feather_line, feather_line)
            except ConfigParser.NoOptionError, err:
              pass
            except ValueError, err:
              pass
          except ConfigParser.NoSectionError, err:
            print "Missing section in config file. %s" %err

          try:
            try:
              actual_pallete = cfg.getboolean(sec_color, 'actual_pallete')
              self.actual_pallete_colors.set_active(actual_pallete)
            except ConfigParser.NoOptionError, err:
              pass
            except ValueError, err:
              pass

            try:
              line_color_r = cfg.getint(sec_color, 'line_color.r')
              line_color_g = cfg.getint(sec_color, 'line_color.g')
              line_color_b = cfg.getint(sec_color, 'line_color.b')
              # 257 - the Magic constant...
              self.line_color.set_color(gtk.gdk.Color(line_color_r * 257, line_color_g * 257, line_color_b * 257))
            except ConfigParser.NoOptionError, err:
              pass
            except ValueError, err:
              pass

            try:
              border_color_r = cfg.getint(sec_color, 'border_color.r')
              border_color_g = cfg.getint(sec_color, 'border_color.g')
              border_color_b = cfg.getint(sec_color, 'border_color.b')
              self.border_color.set_color(gtk.gdk.Color(border_color_r * 257, border_color_g * 257, border_color_b * 257))
            except ConfigParser.NoOptionError, err:
              pass
            except ValueError, err:
              pass

          except ConfigParser.NoSectionError, err:
            print "Missing section in config file. %s" %err

          try:
            # Left text
            try:
              left_text_font = cfg.get(sec_text, 'left_text_font')
              left_text_font_size = cfg.getfloat(sec_text, 'left_text_font_size')
              self.left_text_font.set_font_name(left_text_font + " " + str(left_text_font_size))
            except ConfigParser.NoOptionError, err:
              pass
            except ValueError, err:
              pass

            try:
              left_text_justify = cfg.get(sec_text, 'left_text_justify')
              self.set_combobox(self.left_text_justify, left_text_justify)
            except ConfigParser.NoOptionError, err:
              pass
            except ValueError, err:
              pass

            try:
              left_text = cfg.get(sec_text, 'left_text')
              self.set_text(self.left_text, left_text.replace('.\n','\n'))
            except ConfigParser.NoOptionError, err:
              pass
            except ValueError, err:
              pass

            # Center text
            try:
              center_text_font = cfg.get(sec_text, 'center_text_font')
              center_text_font_size = cfg.getfloat(sec_text, 'center_text_font_size')
              self.center_text_font.set_font_name(center_text_font + " " + str(center_text_font_size))
            except ConfigParser.NoOptionError, err:
              pass
            except ValueError, err:
              pass

            try:
              center_text_justify = cfg.get(sec_text, 'center_text_justify')
              self.set_combobox(self.center_text_justify, center_text_justify)
            except ConfigParser.NoOptionError, err:
              pass
            except ValueError, err:
              pass

            try:
              center_text = cfg.get(sec_text, 'center_text')
              self.set_text(self.center_text, center_text.replace('.\n','\n'))
            except ConfigParser.NoOptionError, err:
              pass
            except ValueError, err:
              pass

            # Right text
            try:
              right_text_font = cfg.get(sec_text, 'right_text_font')
              right_text_font_size = cfg.getfloat(sec_text, 'right_text_font_size')
              self.right_text_font.set_font_name(right_text_font + " " + str(right_text_font_size))
            except ConfigParser.NoOptionError, err:
              pass
            except ValueError, err:
              pass

            try:
              right_text_justify = cfg.get(sec_text, 'right_text_justify')
              self.set_combobox(self.right_text_justify, right_text_justify)
            except ConfigParser.NoOptionError, err:
              pass
            except ValueError, err:
              pass

            try:
              right_text = cfg.get(sec_text, 'right_text')
              self.set_text(self.right_text, right_text.replace('.\n','\n'))
            except ConfigParser.NoOptionError, err:
              pass
            except ValueError, err:
              pass

            try:
              text_position = cfg.get(sec_text, 'text_position')
              self.set_combobox(self.text_position, text_position)
            except ConfigParser.NoOptionError, err:
              pass
            except ValueError, err:
              pass

            try:
              rotate_text = cfg.getboolean(sec_text, 'rotate_text')
              self.rotate_text.set_active(rotate_text)
            except ConfigParser.NoOptionError, err:
              pass
            except ValueError, err:
              pass

            try:
              flatten_image = cfg.getboolean(sec_general, 'flatten_image')
              self.flatten_image.set_active(flatten_image)
            except ConfigParser.NoOptionError, err:
              pass
            except ValueError, err:
              pass

            try:
              work_on_copy = cfg.getboolean(sec_general, 'work_on_copy')
              self.work_on_copy.set_active(work_on_copy)
            except ConfigParser.NoOptionError, err:
              pass
            except ValueError, err:
              pass
          except ConfigParser.NoSectionError, err:
            print "Missing section in config file. %s" %err

          return True

        except ConfigParser.Error, err:
          print "Cannot parse configuration file. %s" %err
          self.on_error("Configuration file error", "Cannot parse configuration file. " + str(err))
        except IOError, err:
          print "Problem opening configuration file. %s" %err
          self.on_error("Configuration file loading error", "Problem opening configuration file." + str(err))
