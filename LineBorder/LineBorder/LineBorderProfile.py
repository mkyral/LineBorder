#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#
# A class to handle profiles for LineBorder python-fu Gimp script
#
# (C) 2010  Marian Kyral (mkyral@email.cz)
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


import os, ConfigParser
import gtk, pygtk


class LineBorderProfile :
  def __init__ (self, profileId, name,
                      comment = "",
                      sections = ["all",],
                      width = 25,
                      widthUnits = "pixels",
                      height = 25,
                      heightUnits = "pixels",
                      extText = 0,
                      extTextUnits = "pixels",
                      roundInnerBorder = 0,
                      roundInnerBorderUnits = "pixels",
                      roundOuterBorder = 0,
                      roundOuterBorderUnits = "pixels",
                      innerLine = True,
                      innerSize = 1,
                      innerUnits = "pixels",
                      distToImage = 1,
                      distToImageUnits = "pixels",
                      outerLine = True,
                      outerSize = 0,
                      outerUnits = "pixels",
                      distToBorder = 0,
                      distToBorderUnits = "pixels",
                      innerRound = 0,
                      innerRoundUnits = "pixels",
                      outerRound = 0,
                      outerRoundUnits = "pixels",
                      actualPallete = False,
                      lineColor = (0, 0, 0),
                      borderColor = (255, 255, 255),
                      featherLine = "None",
                      leftTextFont = "Sans",
                      leftTextFontSize = 14,
                      leftTextJustify = "Center",
                      leftText = "",
                      centerTextFont = "Sans",
                      centerTextFontSize = 16,
                      centerTextJustify = "Center",
                      centerText = "",
                      rightTextFont = "Sans",
                      rightTextFontSize = 14,
                      rightTextJustify = "Center",
                      rightText = "",
                      textPosition = "Bottom",
                      rotateText = False,
                      flattenImage = True,
                      workOnCopy = False,
                      wmType = "text",
                      wmOpacity = 25,
                      wmRotation = 0,
                      wmPosition = "Bottom-Center",
                      wmDistToBorder = 5,
                      wmDistToBorderUnits = "pixels",
                      wmFontName = "Sans",
                      wmFontSize = 12,
                      wmJustify = "Center",
                      wmColor = (0, 0, 0),
                      wmText = "" ,
                      wmImagePath = ""
               ) :
      self.profileId = profileId
      self.name = name
      self.comment = comment
      self.sections = sections
      self.width = width
      self.widthUnits = widthUnits
      self.height = height
      self.heightUnits = heightUnits
      self.extText = extText
      self.extTextUnits = extTextUnits
      self.roundInnerBorder = roundInnerBorder
      self.roundInnerBorderUnits = roundInnerBorderUnits
      self.roundOuterBorder = roundOuterBorder
      self.roundOuterBorderUnits = roundOuterBorderUnits
      self.innerLine = innerLine
      self.innerSize = innerSize
      self.innerUnits = innerUnits
      self.distToImage = distToImage
      self.distToImageUnits = distToImageUnits
      self.outerLine = outerLine
      self.outerSize = outerSize
      self.outerUnits = outerUnits
      self.distToBorder = distToBorder
      self.distToBorderUnits = distToBorderUnits
      self.innerRound = innerRound
      self.innerRoundUnits = innerRoundUnits
      self.outerRound = outerRound
      self.outerRoundUnits = outerRoundUnits
      self.actualPallete = actualPallete
      self.lineColor = lineColor
      self.borderColor = borderColor
      self.featherLine = featherLine
      self.leftTextFont = leftTextFont
      self.leftTextFontSize = leftTextFontSize
      self.leftTextJustify = leftTextJustify
      self.leftText = leftText
      self.centerTextFont = centerTextFont
      self.centerTextFontSize = centerTextFontSize
      self.centerTextJustify = centerTextJustify
      self.centerText = centerText
      self.rightTextFont = rightTextFont
      self.rightTextFontSize = rightTextFontSize
      self.rightTextJustify = rightTextJustify
      self.rightText = rightText
      self.textPosition = textPosition
      self.rotateText = rotateText
      self.flattenImage = flattenImage
      self.workOnCopy = workOnCopy
      self.wmType = wmType
      self.wmOpacity = wmOpacity
      self.wmRotation = wmRotation
      self.wmPosition = wmPosition
      self.wmDistToBorder = wmDistToBorder
      self.wmDistToBorderUnits = wmDistToBorderUnits
      self.wmFontName = wmFontName
      self.wmFontSize = wmFontSize
      self.wmJustify = wmJustify
      self.wmColor = wmColor
      self.wmText = wmText
      self.wmImagePath = wmImagePath

      self.deleted = False

class LineBorderProfileList :
  def __init__ (self) :
      p = LineBorderProfile("DEFAULT", "DEFAULT")
      self.profiles = { p.profileId : p }
      #self.activeProfile = a.profileId
      self.configFile = ""
      self.userProfilePrefix = 'USER'
      self.maxUserProfileId = 0

  def addProfile (self, profileId, name) :
      if not name in self.profiles :
        p = LineBorderProfile(profileId, name)
        self.profiles[profileId] = p

        # Max user profile ID
        if profileId.startswith(self.userProfilePrefix) :
          userProfileNumber = profileId.replace(self.userProfilePrefix,'')
          if userProfileNumber.isdigit() :
            userProfileNumber = int(userProfileNumber)
            if userProfileNumber > self.maxUserProfileId :
              self.maxUserProfileId = userProfileNumber

  def deleteProfile (self, profileId) :
      p = self.profiles[profileId]
      del p
      del self.profiles[profileId]

  def listProfiles (self) :
      for k, v in self.profiles.iteritems() :
        print k + " : " + v.name

  def saveProfiles (self) :

      if self.configFile == "" :
        return False

      cfg = ConfigParser.RawConfigParser()

      # save information about profiles
      cfg.add_section("Profiles")

      profileList = ""
      profileDelim = ""
      for k, v in self.profiles.iteritems() :
        if not v.deleted :
          profileList = profileList + profileDelim + k
          profileDelim = "|"

      cfg.set ("Profiles", 'List', profileList)
      cfg.set ("Profiles", 'userProfilePrefix', self.userProfilePrefix)

      # save profiles
      for k, v in self.profiles.iteritems() :
        if not v.deleted :
          self.saveOneProfile(cfg, v)

      # save configuration to the file
      with open(self.configFile, 'wb') as configfile:
        cfg.write(configfile)

      return True

  def loadProfiles(self):

      if not os.path.exists(self.configFile):
        return False
      else :
        try:
          cfg = ConfigParser.RawConfigParser()
          cfg.read(self.configFile)

          # Load Profiles
          try:
            try:
              profiles = cfg.get("Profiles", 'List').split('|')
              for profile in profiles :
                self.addProfile(profile, profile)
                self.loadOneProfile(cfg, self.profiles[profile])

            except ConfigParser.NoOptionError, err:
              pass
            except ValueError, err:
              pass

            # Load Profiles
            try:
              self.userProfilePrefix = cfg.get("Profiles", 'userProfilePrefix')
            except ConfigParser.NoOptionError, err:
              pass

          except ConfigParser.NoSectionError, err:
            print _("Missing section in config file. %s") %err
            self.loadOneProfile(cfg, self.profiles['DEFAULT'])

        except ConfigParser.Error, err:
          print _("Cannot parse configuration file. %s") %err
          self.on_error(_("Configuration file error"), _("Cannot parse configuration file. ") + str(err))
        except IOError, err:
          print "Problem opening configuration file. %s" %err
          self.on_error(_("Configuration file loading error"), _("Problem opening configuration file.") + str(err))


  def profileSections(self, profile):
      sec_main = profile +':' + 'main'
      sec_border = profile +':' + 'border'
      sec_color = profile +':' + 'color'
      sec_text = profile +':' + 'text'
      sec_general = profile +':' + 'general'
      sec_wm = profile +':' + 'watermark'
      return sec_main, sec_border, sec_color, sec_text, sec_general, sec_wm

  # Save plugin options for nex time
  def saveOneProfile(self, cfg, profile):

      sec_main, sec_border, sec_color, sec_text, sec_general, sec_wm = self.profileSections(profile.profileId)

      cfg.add_section(sec_main)
      cfg.set (sec_main, 'name', profile.name)
      cfg.set (sec_main, 'comment', profile.comment.replace('\n','.\n'))
      cfg.set (sec_main, 'sections', '|'.join(profile.sections))

      if 'all' in profile.sections or 'border' in profile.sections :
        cfg.add_section(sec_border)
        cfg.set (sec_border, 'width', profile.width)
        cfg.set (sec_border, 'width_units', profile.widthUnits)
        cfg.set (sec_border, 'height', profile.height)
        cfg.set (sec_border, 'height_units', profile.heightUnits)
        cfg.set (sec_border, 'ext_text', profile.extText)
        cfg.set (sec_border, 'ext_text_units', profile.extTextUnits)
        cfg.set (sec_border, 'round_inner_border', profile.roundInnerBorder)
        cfg.set (sec_border, 'round_inner_border_units', profile.roundInnerBorderUnits)
        cfg.set (sec_border, 'round_outer_border', profile.roundOuterBorder)
        cfg.set (sec_border, 'round_outer_border_units', profile.roundOuterBorderUnits)
        cfg.set (sec_border, 'inner_line', profile.innerLine)
        cfg.set (sec_border, 'inner_size', profile.innerSize)
        cfg.set (sec_border, 'inner_units', profile.innerUnits)
        cfg.set (sec_border, 'dist_to_image', profile.distToImage)
        cfg.set (sec_border, 'dist_to_image_units', profile.distToImageUnits)
        cfg.set (sec_border, 'inner_round', profile.innerRound)
        cfg.set (sec_border, 'inner_round_units', profile.innerRoundUnits)
        cfg.set (sec_border, 'outer_line', profile.outerLine)
        cfg.set (sec_border, 'outer_size', profile.outerSize)
        cfg.set (sec_border, 'outer_units', profile.outerUnits)
        cfg.set (sec_border, 'outer_round', profile.outerRound)
        cfg.set (sec_border, 'outer_round_units', profile.outerRoundUnits)
        cfg.set (sec_border, 'dist_to_border', profile.distToBorder)
        cfg.set (sec_border, 'dist_to_border_units', profile.distToBorderUnits)
        cfg.set (sec_border, 'feather_line', profile.featherLine)

      if 'all' in profile.sections or 'color' in profile.sections :
        cfg.add_section(sec_color)
        cfg.set (sec_color, 'actual_pallete', profile.actualPallete)
        cfg.set (sec_color, 'line_color.r', profile.lineColor[0])
        cfg.set (sec_color, 'line_color.g', profile.lineColor[1])
        cfg.set (sec_color, 'line_color.b', profile.lineColor[2])
        cfg.set (sec_color, 'border_color.r', profile.borderColor[0])
        cfg.set (sec_color, 'border_color.g', profile.borderColor[1])
        cfg.set (sec_color, 'border_color.b', profile.borderColor[2])

      if 'all' in profile.sections or 'text' in profile.sections :
        cfg.add_section(sec_text)
        cfg.set (sec_text, 'left_text_font', profile.leftTextFont)
        cfg.set (sec_text, 'left_text_font_size', profile.leftTextFontSize)
        cfg.set (sec_text, 'left_text_justify', profile.leftTextJustify)
        cfg.set (sec_text, 'left_text', profile.leftText.replace('\n','.\n'))
        cfg.set (sec_text, 'center_text_font', profile.centerTextFont)
        cfg.set (sec_text, 'center_text_font_size', profile.centerTextFontSize)
        cfg.set (sec_text, 'center_text_justify', profile.centerTextJustify)
        cfg.set (sec_text, 'center_text', profile.centerText.replace('\n','.\n'))
        cfg.set (sec_text, 'right_text_font', profile.rightTextFont)
        cfg.set (sec_text, 'right_text_font_size', profile.rightTextFontSize)
        cfg.set (sec_text, 'right_text_justify', profile.rightTextJustify)
        cfg.set (sec_text, 'right_text', profile.rightText.replace('\n','.\n'))
        cfg.set (sec_text, 'text_position', profile.textPosition)
        cfg.set (sec_text, 'rotate_text', profile.rotateText)

      if 'all' in profile.sections or 'general' in profile.sections :
        cfg.add_section(sec_general)
        cfg.set (sec_general, 'flatten_image', profile.flattenImage)
        cfg.set (sec_general, 'work_on_copy', profile.workOnCopy)

      if 'all' in profile.sections or 'wm' in profile.sections :
        cfg.add_section(sec_wm)
        cfg.set (sec_wm, 'wm_type', profile.wmType)
        cfg.set (sec_wm, 'wm_opacity', profile.wmOpacity)
        cfg.set (sec_wm, 'wm_rotation', profile.wmRotation)
        cfg.set (sec_wm, 'wm_position', profile.wmPosition)
        cfg.set (sec_wm, 'wm_dist_to_border', profile.wmDistToBorder)
        cfg.set (sec_wm, 'wm_dist_to_border_units', profile.wmDistToBorderUnits)
        cfg.set (sec_wm, 'wm_font_name', profile.wmFontName)
        cfg.set (sec_wm, 'wm_font_size', profile.wmFontSize)
        cfg.set (sec_wm, 'wm_justify', profile.wmJustify)
        cfg.set (sec_wm, 'wm_color.r', profile.wmColor[0])
        cfg.set (sec_wm, 'wm_color.g', profile.wmColor[1])
        cfg.set (sec_wm, 'wm_color.b', profile.wmColor[2])
        cfg.set (sec_wm, 'wm_text', profile.wmText.replace('\n','.\n'))
        cfg.set (sec_wm, 'wm_image_path', profile.wmImagePath)

  def loadOneProfile (self, cfg, profile):

      sec_main, sec_border, sec_color, sec_text, sec_general, sec_wm = self.profileSections(profile.profileId)

      # Section: Main
      try:
        # Profile name
        try:
          profile.name = cfg.get(sec_main, 'name')
        except ConfigParser.NoOptionError, err:
          pass
        except ValueError, err:
          pass

        try:
          profile.comment = cfg.get(sec_main, 'comment').replace('.\n','\n')
        except ConfigParser.NoOptionError, err:
          pass
        except ValueError, err:
          pass

        try:
          profile.sections = cfg.get(sec_main, 'sections').split('|')
        except ConfigParser.NoOptionError, err:
          pass
        except ValueError, err:
          pass
      except ConfigParser.NoSectionError, err:
        print _("Missing section in config file. %s") %err

      # Section: Border
      if 'all' in profile.sections or 'border' in profile.sections :
        try:
          try:
            profile.width = cfg.getfloat(sec_border, 'width')
            profile.widthUnits = cfg.get(sec_border, 'width_units')
          except ConfigParser.NoOptionError, err:
            pass
          except ValueError, err:
            pass

          try:
            profile.height = cfg.getfloat(sec_border, 'height')
            profile.heightUnits = cfg.get(sec_border, 'height_units')
          except ConfigParser.NoOptionError, err:
            pass
          except ValueError, err:
            pass

          try:
            profile.extText = cfg.getfloat(sec_border, 'ext_text')
            profile.extTextUnits = cfg.get(sec_border, 'ext_text_units')
          except ConfigParser.NoOptionError, err:
            pass
          except ValueError, err:
            pass

          try:
            profile.roundInnerBorder = cfg.getfloat(sec_border, 'round_inner_border')
            profile.roundInnerBorderUnits = cfg.get(sec_border, 'round_inner_border_units')
          except ConfigParser.NoOptionError, err:
            pass
          except ValueError, err:
            pass

          try:
            profile.roundOuterBorder = cfg.getfloat(sec_border, 'round_outer_border')
            profile.roundOuterBorder_units = cfg.get(sec_border, 'round_outer_border_units')
          except ConfigParser.NoOptionError, err:
            pass
          except ValueError, err:
            pass

          try:
            profile.innerLine = cfg.getboolean(sec_border, 'inner_line')
          except ConfigParser.NoOptionError, err:
            profile.innerLine = True
          except ValueError, err:
            pass

          try:
            profile.innerSize = cfg.getfloat(sec_border, 'inner_size')
            profile.innerUnits = cfg.get(sec_border, 'inner_units')
          except ConfigParser.NoOptionError, err:
            pass
          except ValueError, err:
            pass

          try:
            profile.innerRound = cfg.getfloat(sec_border, 'inner_round')
            profile.innerRoundUnits = cfg.get(sec_border, 'inner_round_units')
          except ConfigParser.NoOptionError, err:
            pass
          except ValueError, err:
            pass

          try:
            profile.distToImage = cfg.getfloat(sec_border, 'dist_to_image')
            profile.distToImageUnits = cfg.get(sec_border, 'dist_to_image_units')
          except ConfigParser.NoOptionError, err:
            pass
          except ValueError, err:
            pass

          try:
            profile.outerLine = cfg.getboolean(sec_border, 'outer_line')
          except ConfigParser.NoOptionError, err:
            profile.outerLine = True
          except ValueError, err:
            pass

          try:
            profile.outerSize = cfg.getfloat(sec_border, 'outer_size')
            profile.outerUnits = cfg.get(sec_border, 'outer_units')
          except ConfigParser.NoOptionError, err:
            pass
          except ValueError, err:
            pass

          try:
            profile.outerRound = cfg.getfloat(sec_border, 'outer_round')
            profile.outerRoundUnits = cfg.get(sec_border, 'outer_round_units')
          except ConfigParser.NoOptionError, err:
            pass
          except ValueError, err:
            pass

          try:
            profile.distToBorder = cfg.getfloat(sec_border, 'dist_to_border')
            profile.distToBorderUnits = cfg.get(sec_border, 'dist_to_border_units')
          except ConfigParser.NoOptionError, err:
            pass
          except ValueError, err:
            pass

          try:
            profile.featherLine = cfg.get(sec_border, 'feather_line')
          except ConfigParser.NoOptionError, err:
            pass
          except ValueError, err:
            pass
        except ConfigParser.NoSectionError, err:
          print _("Missing section in config file. %s") %err

      # Section: Color
      if 'all' in profile.sections or 'color' in profile.sections :
        try:
          try:
            profile.actualPallete = cfg.getboolean(sec_color, 'actual_pallete')
          except ConfigParser.NoOptionError, err:
            pass
          except ValueError, err:
            pass

          try:
            line_color_r = cfg.getint(sec_color, 'line_color.r')
            line_color_g = cfg.getint(sec_color, 'line_color.g')
            line_color_b = cfg.getint(sec_color, 'line_color.b')
            # 257 - the Magic constant...
            profile.lineColor = (line_color_r, line_color_g, line_color_b)
          except ConfigParser.NoOptionError, err:
            pass
          except ValueError, err:
            pass

          try:
            border_color_r = cfg.getint(sec_color, 'border_color.r')
            border_color_g = cfg.getint(sec_color, 'border_color.g')
            border_color_b = cfg.getint(sec_color, 'border_color.b')
            profile.borderColor = (border_color_r, border_color_g, border_color_b)
          except ConfigParser.NoOptionError, err:
            pass
          except ValueError, err:
            pass

        except ConfigParser.NoSectionError, err:
          print _("Missing section in config file. %s") %err

      # Section: Text
      if 'all' in profile.sections or 'text' in profile.sections :
        try:
          # Left text
          try:
            profile.leftTextFont = cfg.get(sec_text, 'left_text_font')
            profile.leftTextFontSize = cfg.getfloat(sec_text, 'left_text_font_size')
          except ConfigParser.NoOptionError, err:
            pass
          except ValueError, err:
            pass

          try:
            profile.leftTextJustify = cfg.get(sec_text, 'left_text_justify')
          except ConfigParser.NoOptionError, err:
            pass
          except ValueError, err:
            pass

          try:
            profile.leftText = cfg.get(sec_text, 'left_text').replace('.\n','\n')
          except ConfigParser.NoOptionError, err:
            pass
          except ValueError, err:
            pass

          # Center text
          try:
            profile.centerTextFont = cfg.get(sec_text, 'center_text_font')
            profile.centerTextFontSize = cfg.getfloat(sec_text, 'center_text_font_size')
          except ConfigParser.NoOptionError, err:
            pass
          except ValueError, err:
            pass

          try:
            profile.centerTextJustify = cfg.get(sec_text, 'center_text_justify')
          except ConfigParser.NoOptionError, err:
            pass
          except ValueError, err:
            pass

          try:
            profile.centerText = cfg.get(sec_text, 'center_text').replace('.\n','\n')
          except ConfigParser.NoOptionError, err:
            pass
          except ValueError, err:
            pass

          # Right text
          try:
            profile.rightTextFont = cfg.get(sec_text, 'right_text_font')
            profile.rightTextFontSize = cfg.getfloat(sec_text, 'right_text_font_size')
          except ConfigParser.NoOptionError, err:
            pass
          except ValueError, err:
            pass

          try:
            profile.rightTextJustify = cfg.get(sec_text, 'right_text_justify')
          except ConfigParser.NoOptionError, err:
            pass
          except ValueError, err:
            pass

          try:
            profile.rightText = cfg.get(sec_text, 'right_text').replace('.\n','\n')
          except ConfigParser.NoOptionError, err:
            pass
          except ValueError, err:
            pass

          try:
            profile.textPosition = cfg.get(sec_text, 'text_position')
          except ConfigParser.NoOptionError, err:
            pass
          except ValueError, err:
            pass

          try:
            profile.rotateText = cfg.getboolean(sec_text, 'rotate_text')
          except ConfigParser.NoOptionError, err:
            pass
          except ValueError, err:
            pass
        except ConfigParser.NoSectionError, err:
          print _("Missing section in config file. %s") %err

      # Section: General
      if 'all' in profile.sections or 'general' in profile.sections :
        try:
          try:
            profile.flattenImage = cfg.getboolean(sec_general, 'flatten_image')
          except ConfigParser.NoOptionError, err:
            pass
          except ValueError, err:
            pass

          try:
            profile.workOnCopy = cfg.getboolean(sec_general, 'work_on_copy')
          except ConfigParser.NoOptionError, err:
            pass
          except ValueError, err:
            pass
        except ConfigParser.NoSectionError, err:
          print _("Missing section in config file. %s") %err

      # Section:Watermark
      if 'all' in profile.sections or 'wm' in profile.sections :
        try:
          try:
            profile.wmType = cfg.get(sec_wm, 'wm_type')
          except ConfigParser.NoOptionError, err:
              pass
          except ValueError, err:
            pass

          try:
            profile.wmOpacity = cfg.getfloat(sec_wm, 'wm_opacity')
          except ConfigParser.NoOptionError, err:
            pass
          except ValueError, err:
            pass

          try:
            profile.wmRotation = cfg.getfloat(sec_wm, 'wm_rotation')
          except ConfigParser.NoOptionError, err:
            pass
          except ValueError, err:
            pass

          try:
            profile.wmPosition = cfg.get(sec_wm, 'wm_position')
          except ConfigParser.NoOptionError, err:
            pass
          except ValueError, err:
            pass

          try:
            profile.wmDistToBorder = cfg.getfloat(sec_wm, 'wm_dist_to_border')
            profile.wmDistToBorderUnits = cfg.get(sec_wm, 'wm_dist_to_border_units')
          except ConfigParser.NoOptionError, err:
            pass
          except ValueError, err:
            pass

          try:
            profile.wmFontName = cfg.get(sec_wm, 'wm_font_name')
            profile.wmFontSize = cfg.getfloat(sec_wm, 'wm_font_size')
          except ConfigParser.NoOptionError, err:
            pass
          except ValueError, err:
            pass

          try:
            profile.wmJustify = cfg.get(sec_wm, 'wm_justify')
          except ConfigParser.NoOptionError, err:
            pass
          except ValueError, err:
            pass

          try:
            wm_color_r = cfg.getint(sec_wm, 'wm_color.r')
            wm_color_g = cfg.getint(sec_wm, 'wm_color.g')
            wm_color_b = cfg.getint(sec_wm, 'wm_color.b')
            profile.wmColor = (wm_color_r, wm_color_g, wm_color_b)
          except ConfigParser.NoOptionError, err:
            pass
          except ValueError, err:
            pass

          try:
            profile.wmText = cfg.get(sec_wm, 'wm_text').replace('.\n','\n')
          except ConfigParser.NoOptionError, err:
            pass
          except ValueError, err:
            pass

          try:
            profile.wmImagePath = cfg.get(sec_wm, 'wm_image_path')
          except ConfigParser.NoOptionError, err:
            pass
          except ValueError, err:
            pass

        except ConfigParser.NoSectionError, err:
          print _("Missing section in config file. %s") %err

      return True




