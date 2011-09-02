#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#
# Copyright, V2.4
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
# 21.11.2010 - v2.4
# * ADD: profiles
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
from TreeViewTooltips import TreeViewTooltips
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

profile_list = LineBorderProfile.LineBorderProfileList()

class MyTreeViewTooltips(TreeViewTooltips):
  # Overriding get_tooltip()
  def get_tooltip(self, view, column, path):
    title = column.get_title()
    model = view.get_model()
    profile_id = model[path][0]
    profile_name = model[path][1]
    border_section_set = model[path][2]
    color_section_set = model[path][3]
    text_section_set = model[path][4]
    wm_section_set = model[path][5]
    general_section_set = model[path][6]

    if title == _('Profile name'):
      if profile_list.profiles[profile_id].comment == '' :
        return _('<u><big>Profile: %s</big></u>\n<i>%s</i>' % (profile_list.profiles[profile_id].name,
                                            _('No comment')))
      else :
        return _('<u><big>Profile: %s</big></u>\n<i>%s</i>' % (profile_list.profiles[profile_id].name,
                                           profile_list.profiles[profile_id].comment))

    elif title == _('B'):
      if border_section_set :
        return _('Profile %s\ncontains Border section' % (profile_name))
      else :
        return _('Profile %s\ndoes not contain Border section' % (profile_name))

    elif title == _('C'):
      if color_section_set :
        return _('Profile %s\ncontains Color section' % (profile_name))
      else :
        return _('Profile %s\ndoes not contain Color section' % (profile_name))

    elif title == _('T'):
      if text_section_set :
        return _('Profile %s\ncontains Text section' % (profile_name))
      else :
        return _('Profile %s\ndoes not contain Text section' % (profile_name))

    elif title == _('W'):
      if wm_section_set :
        return _('Profile %s\ncontains Watermark section' % (profile_name))
      else :
        return _('Profile %s\ndoes not contain Watermark section' % (profile_name))

    elif title == _('G'):
      if general_section_set :
        return _('Profile %s\ncontains General section' % (profile_name))
      else :
        return _('Profile %s\ndoes not General Border section' % (profile_name))

    else:
      return None

      ## By checking both column and path we have a
      ## cell-based tooltip.
      #model = view.get_model()
      #customer = model[path][2]
      #return '<big>%s %s</big>\n<i>%s</i>' % (customer.fname,
      #customer.lname,
      #customer.notes)
      ## phone
      #else:
        #return ('<big><u>Generic Column Tooltip</u></big>\n'
        #'Unless otherwise noted, all\narea codes are 888')

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
      self.main_dialog = builder.get_object("window1")
      self.about_dialog = builder.get_object("aboutdialog1")
      self.profile_dialog = builder.get_object("profile_dialog")

      # Border page
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

      # Text page
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

      # Watermark page
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

      # Profiles page
      self.profiles_treeview = builder.get_object('treeview_profiles')
      self.setup_profiles_treeview()
      self.profiles_btn_load_profile = builder.get_object('button_load_profile')
      self.profiles_btn_update_profile = builder.get_object('button_update_profile')
      self.profiles_btn_save_new_profile = builder.get_object('button_save_new_profile')
      self.profiles_btn_delete_profile = builder.get_object('button_delete_profile')

      # Add profile dialog
      self.profile_dialog_name_label = builder.get_object('label_profile_name')
      self.profile_dialog_name = builder.get_object('entry_profile_name')
      self.profile_dialog_comment = builder.get_object('textview_profile_comment')
      self.profile_dialog_border_cb = builder.get_object('cb_profile_borders')
      self.profile_dialog_color_cb = builder.get_object('cb_profiles_colors')
      self.profile_dialog_text_cb = builder.get_object('cb_profile_text')
      self.profile_dialog_wm_cb = builder.get_object('cb_profile_wm')
      self.profile_dialog_general_cb = builder.get_object('cb_profile_general')
      self.image_load_profile = builder.get_object('image_load_profile')
      #
      self.profile_dialog_mode = None # Load | Update | Save as new
      self.profile_dialog_actual = None # Profile to load or update

      # Initialize profiles
      #self.profile_list = LineBorderProfile.LineBorderProfileList()
      self.profile_list = profile_list
      self.profile_list.configFile = os.path.join(gimp.directory, "LineBorder.cfg")
      self.profile_list.loadProfiles()
      self.default_profile = self.profile_list.profiles['DEFAULT']

      # TreeViewTooltips
      self.tree_view_tips = MyTreeViewTooltips()
      self.tree_view_tips.add_view(self.profiles_treeview)

      # add profiles to the treeview list
      self.profiles_model = self.profiles_treeview.get_model()
      for k, p in self.profile_list.profiles.iteritems() :
        self.add_row_to_treeview(p)
      self.profiles_model.set_sort_column_id(1, gtk.SORT_ASCENDING)

      if not self.apply_profile(self.default_profile) :
        # Workaround :-/ (http://www.listware.net/201004/gtk-app-devel-list/88663-default-values-for-spin-buttons-in-glade.html)
        self.border_width.set_value(25)
        self.border_height.set_value(25)
        self.border_inner_size.set_value(1)
        self.border_dist_to_image.set_value(1)
        self.border_dist_to_border.set_value(1)
        self.wm_opacity.set_value(25)
        self.wm_dist_to_border.set_value(5)

      self.main_dialog.show()

  def main(self):
      gtk.main()  # event loop

  #
  #  --- Handle functions for dialog signals  ---
  #

  # show the About dialog
  def on_button_about_clicked(self, widget):
      self.about_dialog.show()

  # Hide the About dialog
  def on_aboutdialog1_destroy(self, widget, responseID = None):
      widget.hide()

  # Show an error message
  def on_error(self, title, text = None):
      md = gtk.MessageDialog(None,
           gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR,
           gtk.BUTTONS_CLOSE, title)
      md.format_secondary_text(text)
      md.run()
      md.destroy()

  # Activate/Deactivate color items
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

  # Activate/Deactivate rotate_text item
  def on_combobox_text_position_changed(self, widget):
      active = self.text_position.get_active()
      if active == self.combobox_get_id_from_desc(TEXT_POSITION, "Left") or \
         active == self.combobox_get_id_from_desc(TEXT_POSITION, "Right") :
        self.rotate_text.set_sensitive(True)
        self.label_rotate_text.set_sensitive(True)
      else:
        self.rotate_text.set_sensitive(False)
        self.label_rotate_text.set_sensitive(False)

  # Activate/Deactivate Watermart Text/Image sections
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

  # show the Fileopen dialog to choose watermark image
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

  # Activate/Deactivate the inner Line box
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

  # Activate/Deactivate the outer Line box
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

  # Add the border
  def on_button_ok_clicked(self, widget):
      self.call_LineBorder()
      gtk.main_quit()

  # quit
  def on_window1_destroy(self, widget):
      gtk.main_quit()

  # Setup treeview on the profile page
  #   (there is no possibility to translate columns directly in glade)
  def setup_profiles_treeview(self):
      # Workaround: Make column titles translatable
      self.profiles_treeview.get_column(0).set_title(_("Profile name"))
      self.profiles_treeview.get_column(1).set_title(_("B"))
      self.profiles_treeview.get_column(2).set_title(_("C"))
      self.profiles_treeview.get_column(3).set_title(_("T"))
      self.profiles_treeview.get_column(4).set_title(_("W"))
      self.profiles_treeview.get_column(5).set_title(_("G"))

  # Show "Load the selected profile?" question?
  def on_button_load_profile_clicked(self, widget):
      # prepare the dialog
      (model, iter) = self.profiles_treeview.get_selection().get_selected()
      if iter == None :
        self.on_error(_("No profile selected."), _("Select profile to load please."))
        return
      selected_profile = model.get(iter,0)[0]
      p = self.profile_list.profiles[selected_profile]

      self.reset_profile_dialog(_('Load profile?'))

      icon = self.profile_dialog.render_icon(gtk.STOCK_OPEN, gtk.ICON_SIZE_BUTTON)
      self.profile_dialog.set_icon(icon)

      self.profile_dialog_mode = 'Load'
      self.profile_dialog_actual = p.profileId

      self.profile_dialog_name_label.set_text('\n<b><big>' + _('Load profile') + ' ' + p.name +'?' + '</big></b>\n')
      self.profile_dialog_name_label.set_use_markup(True)

      self.profile_dialog_name.hide()
      #self.profile_dialog_name.set_sensitive(False)

      self.set_text(self.profile_dialog_comment,p.comment)
      self.profile_dialog_comment.set_sensitive(False)

      if 'all' in p.sections or 'border' in p.sections :
        self.profile_dialog_border_cb.set_active(True)
      else :
        self.profile_dialog_border_cb.set_sensitive(False)

      if 'all' in p.sections or 'color' in p.sections :
        self.profile_dialog_color_cb.set_active(True)
      else :
        self.profile_dialog_color_cb.set_sensitive(False)

      if 'all' in p.sections or 'text' in p.sections :
        self.profile_dialog_text_cb.set_active(True)
      else :
        self.profile_dialog_text_cb.set_sensitive(False)

      if 'all' in p.sections or 'wm' in p.sections :
        self.profile_dialog_wm_cb.set_active(True)
      else :
        self.profile_dialog_wm_cb.set_sensitive(False)

      if 'all' in p.sections or 'general' in p.sections :
        self.profile_dialog_general_cb.set_active(True)
      else :
        self.profile_dialog_general_cb.set_sensitive(False)

      self.profile_dialog.show()

  # Show "Save as new profile" dialog
  def on_button_save_new_profile_clicked(self, widget):
      self.reset_profile_dialog(_('Save as new profile'))

      icon = self.profile_dialog.render_icon(gtk.STOCK_SAVE_AS, gtk.ICON_SIZE_BUTTON)
      self.profile_dialog.set_icon(icon)

      self.profile_dialog_mode = 'SaveAs'
      self.profile_dialog_actual = None

      self.profile_dialog_border_cb.set_active(True)
      self.profile_dialog_color_cb.set_active(True)
      self.profile_dialog_general_cb.set_active(True)
      self.profile_dialog.show()

  # Show "Update profile" dialog
  def on_button_update_profile_clicked(self, widget):
      (model, iter) = self.profiles_treeview.get_selection().get_selected()
      if iter == None :
        self.on_error(_("No profile selected."), _("Select profile to update please."))
        return
      selected_profile = model.get(iter,0)[0]
      p = self.profile_list.profiles[selected_profile]

      self.reset_profile_dialog(_('Update profile'))

      icon = self.profile_dialog.render_icon(gtk.STOCK_EDIT, gtk.ICON_SIZE_BUTTON)
      self.profile_dialog.set_icon(icon)

      self.profile_dialog_mode = 'Update'
      self.profile_dialog_actual = p.profileId

      self.profile_dialog_name.set_text(p.name)
      self.set_text(self.profile_dialog_comment,p.comment)

      if 'all' in p.sections or 'border' in p.sections :
        self.profile_dialog_border_cb.set_active(True)

      if 'all' in p.sections or 'color' in p.sections :
        self.profile_dialog_color_cb.set_active(True)

      if 'all' in p.sections or 'text' in p.sections :
        self.profile_dialog_text_cb.set_active(True)

      if 'all' in p.sections or 'wm' in p.sections :
        self.profile_dialog_wm_cb.set_active(True)

      if 'all' in p.sections or 'general' in p.sections :
        self.profile_dialog_general_cb.set_active(True)

      self.profile_dialog.show()

  # show "Delete profile" dialog
  def on_button_delete_profile_clicked(self, widget):
      # prepare the dialog
      (model, iter) = self.profiles_treeview.get_selection().get_selected()
      if iter == None :
        self.on_error(_("No profile selected."), _("Select profile to delete please."))
        return
      selected_profile = model.get(iter,0)[0]
      p = self.profile_list.profiles[selected_profile]

      self.reset_profile_dialog(_('Delete profile?'))

      icon = self.profile_dialog.render_icon(gtk.STOCK_DELETE, gtk.ICON_SIZE_BUTTON)
      self.profile_dialog.set_icon(icon)

      self.profile_dialog_mode = 'Delete'
      self.profile_dialog_actual = p.profileId

      self.profile_dialog_name_label.set_text('\n<b><big>' + _('Delete profile') + ' ' + p.name +'?' + '</big></b>\n')
      self.profile_dialog_name_label.set_use_markup(True)

      self.profile_dialog_name.hide()
      self.set_text(self.profile_dialog_comment,p.comment)
      self.profile_dialog_comment.set_sensitive(False)

      if 'all' in p.sections or 'border' in p.sections :
        self.profile_dialog_border_cb.set_active(True)

      if 'all' in p.sections or 'color' in p.sections :
        self.profile_dialog_color_cb.set_active(True)

      if 'all' in p.sections or 'text' in p.sections :
        self.profile_dialog_text_cb.set_active(True)

      if 'all' in p.sections or 'wm' in p.sections :
        self.profile_dialog_wm_cb.set_active(True)

      if 'all' in p.sections or 'general' in p.sections :
        self.profile_dialog_general_cb.set_active(True)

      self.profile_dialog_border_cb.set_sensitive(False)
      self.profile_dialog_color_cb.set_sensitive(False)
      self.profile_dialog_text_cb.set_sensitive(False)
      self.profile_dialog_wm_cb.set_sensitive(False)
      self.profile_dialog_general_cb.set_sensitive(False)

      self.profile_dialog.show()

  # Changes confirmed by users
  def on_button_profile_ok_clicked (self, widget):
      self.profile_dialog.hide()

      if self.profile_dialog_mode == 'Delete' :
        self.delete_treeview_row(self.profile_dialog_actual)
        self.profile_list.deleteProfile(self.profile_dialog_actual)
        return

      name = self.profile_dialog_name.get_text()
      comment = self.extract_text(self.profile_dialog_comment)
      border_flag = self.profile_dialog_border_cb.get_active()
      color_flag = self.profile_dialog_color_cb.get_active()
      text_flag = self.profile_dialog_text_cb.get_active()
      wm_flag = self.profile_dialog_wm_cb.get_active()
      general_flag = self.profile_dialog_general_cb.get_active()

      if not border_flag and not color_flag and not text_flag and not wm_flag and not general_flag :
        if self.profile_dialog_mode == 'Load' :
          self.on_error(_("There are no sections to load!"))
          return
        elif self.profile_dialog_mode == 'Update' :
          self.on_error(_("There are no sections to save!"), _("There are no sections to save!\nTo delete profile use the 'Delete profile' button."))
          return
        elif self.profile_dialog_mode == 'SaveAs' :
          self.on_error(_("There are no sections to save!"), _("There are no sections to save!\n Profile was not saved."))
          return

      sections = []
      if border_flag and color_flag and text_flag and wm_flag and general_flag :
        sections = ['all',]
      else :
        if border_flag :
          sections.append('border')
        if color_flag :
          sections.append('color')
        if text_flag :
          sections.append('text')
        if wm_flag :
          sections.append('wm')
        if general_flag :
          sections.append('general')

      if self.profile_dialog_mode == 'Load' :
        self.apply_profile(self.profile_list.profiles[self.profile_dialog_actual], sections)

      elif self.profile_dialog_mode == 'Update' :
        profile = self.profile_list.profiles[self.profile_dialog_actual]

        # Update profile name, comment and sections
        profile.name = name
        profile.comment = comment
        profile.sections = sections

        # Parse form to the profile
        self.parse_form_values(profile)

        # update row in the treeview
        self.update_treeview_row(profile)
        self.profile_list.saveProfiles()

      elif self.profile_dialog_mode == 'SaveAs' :
        # save as a new profile
        profile_id = self.profile_list.userProfilePrefix + str(self.profile_list.maxUserProfileId + 1)
        self.profile_list.addProfile(profile_id, name)
        profile = self.profile_list.profiles[profile_id]

        # Update profile name, comment and sections
        profile.name = name
        profile.comment = comment
        profile.sections = sections

        # Parse form to the profile
        self.parse_form_values(profile)

        # add new profile to the list
        self.add_row_to_treeview(profile)
        self.profile_list.saveProfiles()

      self.profiles_model.sort_column_changed()


  def on_button_profile_cancel_clicked (self, widget, responseID = None):
      self.profile_dialog.hide()

  # Inicialization of the profile dialog
  def reset_profile_dialog(self, title):
      self.profile_dialog_name_label.set_text(_('Profile name:'))
      self.profile_dialog_name_label.set_use_markup(False)
      self.profile_dialog.set_title(title)
      self.profile_dialog_name.set_text('')
      self.profile_dialog_name.show()
      self.set_text(self.profile_dialog_comment,'')

      self.profile_dialog_border_cb.set_active(False)
      self.profile_dialog_color_cb.set_active(False)
      self.profile_dialog_text_cb.set_active(False)
      self.profile_dialog_wm_cb.set_active(False)
      self.profile_dialog_general_cb.set_active(False)

      self.profile_dialog_name.set_sensitive(True)
      self.profile_dialog_comment.set_sensitive(True)
      self.profile_dialog_border_cb.set_sensitive(True)
      self.profile_dialog_color_cb.set_sensitive(True)
      self.profile_dialog_text_cb.set_sensitive(True)
      self.profile_dialog_wm_cb.set_sensitive(True)
      self.profile_dialog_general_cb.set_sensitive(True)

  # Decode sections to be used in treeview booleans variables
  def get_profile_flags (self, profile) :
      border_flag = False
      color_flag = False
      text_flag = False
      wm_flag = False
      general_flag = False
      if 'all' in profile.sections :
        border_flag = True
        color_flag = True
        text_flag = True
        wm_flag = True
        general_flag = True
      else :
        if 'border' in profile.sections :
          border_flag = True
        if 'color' in profile.sections :
          color_flag = True
        if 'text' in profile.sections :
          text_flag = True
        if 'wm' in profile.sections :
          wm_flag = True
        if 'general' in profile.sections :
          general_flag = True

      return border_flag, color_flag, text_flag, wm_flag, general_flag

  # add a new row to the treeview
  def add_row_to_treeview(self, profile) :
      if profile.profileId != 'DEFAULT' :
        border_flag, color_flag, text_flag, wm_flag, general_flag = self.get_profile_flags(profile)
        add_iter = self.profiles_model.append([profile.profileId , profile.name, border_flag, color_flag, text_flag, wm_flag, general_flag])

  # update treeview row
  def update_treeview_row(self, profile) :
      iter = self.profiles_model.get_iter_root()
      while (iter) :
        id = self.profiles_model.get_value(iter, 0)
        if id == profile.profileId :
          border_flag, color_flag, text_flag, wm_flag, general_flag = self.get_profile_flags(profile)
          self.profiles_model.set (iter, 1, profile.name, 2, border_flag, 3, color_flag, 4, text_flag, 5, wm_flag, 6, general_flag)
          return
        iter = self.profiles_model.iter_next(iter)

  # delete treeview row
  def delete_treeview_row(self, profileId) :
      iter = self.profiles_model.get_iter_root()
      while (iter) :
        id = self.profiles_model.get_value(iter, 0)
        if id == profileId :
          self.profiles_model.remove(iter)
          return
        iter = self.profiles_model.iter_next(iter)


  #
  #  --- Utils ---
  #

  # iterate trought combobox descriptions and return item ID
  def combobox_get_id_from_desc(self, inSeq, inDesc):
    i = 0
    while i < len(inSeq):
      if inSeq[i] == inDesc :
        return i
      i = i + 1
    return 0

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

  # Add text to the TextView
  def set_text (self, inTextView, inText):
      if inText == None :
        return
      buff = inTextView.get_buffer()
      buff.set_text(inText)


  #
  #  --- Main functions ---
  #

  # Update dialog setup according to given profile
  # Sections: non mandatory - overrides the profile setting
  def apply_profile(self, profile, sections = None):
      if sections != None :
        psections = sections
      else :
        psections = profile.sections

      # Section: Border
      if 'all' in psections or 'border' in psections :
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

      if 'all' in psections or 'color' in psections :
        self.actual_pallete_colors.set_active(profile.actualPallete)
        self.line_color.set_color(gtk.gdk.Color(profile.lineColor[0] * 257, profile.lineColor[1] * 257, profile.lineColor[2] * 257))
        self.border_color.set_color(gtk.gdk.Color((profile.borderColor[0]) * 257, profile.borderColor[1] * 257, profile.borderColor[2] * 257))

      if 'all' in psections or 'text' in psections :
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
      if 'all' in psections or 'general' in psections :
        # Section: General
        self.flatten_image.set_active(profile.flattenImage)
        self.work_on_copy.set_active(profile.workOnCopy)

      # Section: Watermark
      if 'all' in psections or 'wm' in psections :
        if profile.wmType == 'text':
          self.wm_type_text.set_active(True)
          self.on_radiobutton_wm_text_toggled(self.main_dialog) # trigger call on_radiobutton_wm_text_toggled()
        else:
          self.wm_type_image.set_active(True)
        self.wm_opacity.set_value(profile.wmOpacity)
        self.wm_rotation.set_value(profile.wmRotation)
        self.wm_position.set_active(self.combobox_get_id_from_desc(WM_POSITION, profile.wmPosition))
        self.wm_dist_to_border.set_value(profile.wmDistToBorder)
        self.wm_dist_to_border_units.set_active(self.combobox_get_id_from_desc(UNITS, profile.wmDistToBorderUnits))
        self.wm_font.set_font_name(profile.wmFontName + " " + str(profile.wmFontSize))
        self.wm_justify.set_active(self.combobox_get_id_from_desc(JUSTIFY, profile.wmJustify))
        self.wm_color.set_color(gtk.gdk.Color(profile.wmColor[0] * 257, profile.wmColor[1] * 257, profile.wmColor[2] * 257))
        self.set_text(self.wm_text, profile.wmText)
        self.wm_image_path.set_text(profile.wmImagePath)

      return True

  # parse current settings from dialog and store it in the profile
  def parse_form_values(self, profile):
      # Border tab
      if 'all' in profile.sections or 'border' in profile.sections :
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

        profile.featherLine = FEATHER[self.feather_line.get_active()]

      if 'all' in profile.sections or 'color' in profile.sections :
        profile.actualPallete = self.actual_pallete_colors.get_active()
        profile.lineColor = self.extract_color(self.line_color.get_color())
        profile.borderColor = self.extract_color(self.border_color.get_color())

      if 'all' in profile.sections or 'general' in profile.sections :
        profile.flattenImage = self.flatten_image.get_active()
        profile.workOnCopy = self.work_on_copy.get_active()

      # Text tab
      if 'all' in profile.sections or 'text' in profile.sections :
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
      if 'all' in profile.sections or 'wm' in profile.sections :
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


