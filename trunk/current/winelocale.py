#!/usr/bin/python2.5
# -*- coding: utf-8 -*-

'''
Title  : WineLocale
Version: 0.6.1
Author : Derrick Sobodash <derrick@cinnamonpirate.com>
Web    : http://code.google.com/p/winelocale/
License: BSD License

Copyright (c) 2007-2009, Derrick Sobodash
All rights reserved

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:

* Redistributions of source code must retain the above copyright notice,
  this list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.
* Neither the name of Derrick Sobodash nor the names of his contributors
  may be used to endorse or promote products derived from this software
  without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
'''

'''
-------------------------------------------------------------------------------
Python imports
-------------------------------------------------------------------------------
'''
import os, pygtk, gtk, pango, ConfigParser
pygtk.require('2.0')
from optparse import OptionParser # handle config files
from struct import pack           # int to binary
from struct import unpack         # binary to int
from gnome import url_show        # handle URL clicks in GUI

'''
-------------------------------------------------------------------------------
Program information
-------------------------------------------------------------------------------
'''
PROGRAM = "WineLocale"
AUTHOR  = "Derrick Sobodash"
COPY    = "Copyright © 2007-2009 " + AUTHOR
VERSION = "0.6.1"
LICENSE = "BSD"
DESCRIP = "WineLocale clones the functionality of Microsoft AppLocale in " + \
          "Wine. It is used to manage global locale settings and font " + \
          "settings in the Wine registry to ensure proper display of " + \
          "non-Latin type in pre-Unicode portable executables."
WEBSITE = "http://code.google.com/p/winelocale/"
CONFIG  = os.environ["HOME"] + "/.winelocalerc"
I18N    = "i18n"
ICON    = "winelocale.svg"
LICENSE = "LICENSE"

'''
-------------------------------------------------------------------------------
Pull in the translation that matches our locale
-------------------------------------------------------------------------------
'''
## Pull in strings
if(os.environ["LANG"][0:5] != "en_US"):
  try:
    file = open(I18N + "/" + os.environ["LANG"][0:5] + ".lang")
  except IOError:
    print "Unable to find a language file for " + os.environ["LANG"][0:5] + ", using en_US"
    I18N_FILE = I18N + "/en_US.lang"
  else:
    I18N_FILE = I18N + "/" + os.environ["LANG"][0:5] + ".lang"
else:
  I18N_FILE = I18N + "/en_US.lang"
STRINGSFP = open(I18N_FILE,'r')
STRINGS = ConfigParser.ConfigParser()
STRINGS.readfp(STRINGSFP)
STRINGSFP.close()

'''
-------------------------------------------------------------------------------
Pango gotchas
-------------------------------------------------------------------------------
'''
PANGO_SCALE  = 1024   # Why isn't this set in Python's pango module?
WINE_MENUBAR = 0      # Need to hack this to match

GTKTABLE_96 = { # 96dpi table (default)
  6: (9, 15),
  7: (10, 17),  # Pango sizes do not match up to the sizes at which Wine draws
  8: (11, 18),  # the menubar. We need to hack the Pango size to the Wine font
  9: (13, 20),  # size and make the menubar match up.
  10: (14, 22),
  11: (15, 23), # Hope a beta tester can help if someone needs another dpi!
  12: (16, 24),
  13: (18, 27), # And no, this has NOTHING to do with the Wine dpi setting.
  14: (20, 28), # lrn2reghack, fag :(
  16: (22, 31)
  }             # *PROVE* to me someone is blind enough to use 18.

'''
-------------------------------------------------------------------------------
LOGFONT-related constants

Microsoft defines all these, and so should we.
-------------------------------------------------------------------------------
'''
# Font weights
FW_DONTCARE            = 0
FW_THIN                = 100
FW_EXTRALIGHT          = 200
FW_LIGHT               = 300
FW_NORMAL              = 400
FW_MEDIUM              = 500
FW_SEMIBOLD            = 600
FW_BOLD                = 700
FW_EXTRABOLD           = 800
FW_HEAVY               = 900

# Locale character sets
ANSI_CHARSET           = 0
DEFAULT_CHARSET        = 1
SYMBOL_CHARSET         = 2
SHIFTJIS_CHARSET       = 128
HANGUL_CHARSET         = 129
JOHAB_CHARSET          = 130
GB2312_CHARSET         = 134
CHINESEBIG5_CHARSET    = 136
GREEK_CHARSET          = 161
TURKISH_CHARSET        = 162
VIETNAMESE_CHARSET     = 163
BALTIC_CHARSET         = 186
RUSSIAN_CHARSET        = 204
EASTEUROPE_CHARSET     = 238
OEM_CHARSET            = 255

# Display precision (usually 0)
OUT_DEFAULT_PRECIS     = 0
OUT_STRING_PRECIS      = 1
OUT_CHARACTER_PRECIS   = 2
OUT_STROKE_PRECIS      = 3
OUT_TT_PRECIS          = 4
OUT_DEVICE_PRECIS      = 5
OUT_RASTER_PRECIS      = 6
OUT_TT_ONLY_PRECIS     = 7
OUT_OUTLINE_PRECIS     = 8
OUT_PS_ONLY_PRECIS     = 10

# Clipping precision (usually 0)
CLIP_DEFAULT_PRECIS    = 0
CLIP_CHARACTER_PRECIS  = 1
CLIP_STROKE_PRECIS     = 2
CLIP_LH_ANGLES         = 1 << 4
CLIP_TT_ALWAYS         = 2 << 4
CLIP_DFA_DISABLE       = 4 << 4
CLIP_EMBEDDED          = 8 << 4

# Font smoothing
DEFAULT_QUALITY        = 0
DRAFT_QUALITY          = 1
PROOF_QUALITY          = 2
NONANTIALIASED_QUALITY = 3
ANTIALIASED_QUALITY    = 4
CLEARTYPE_QUALITY      = 5

# Font spacing
DEFAULT_PITCH          = 0
FIXED_PITCH            = 1
VARIABLE_PITCH         = 2

# Font style
FF_DONTCARE            = 0 << 4
FF_ROMAN               = 1 << 4
FF_SWISS               = 2 << 4
FF_MODERN              = 3 << 4
FF_SCRIPT              = 4 << 4
FF_DECORATIVE          = 5 << 4

'''
-------------------------------------------------------------------------------
Registry patches

Since we are no longer depending on outside files, we store all basic patches
in this file. The program will collect related patches, write a file to /tmp,
and apply it with Wine's regedit.
-------------------------------------------------------------------------------
'''
REGEDIT       = "REGEDIT4\n\n"

REG_SET120DPI = "[HKEY_CURRENT_CONFIG\Software\Fonts]\n" + \
                "\"LogPixels\"=dword:00000078\n\n"

REG_SMOOTHING = "[HKEY_CURRENT_USER\Control Panel\Desktop]\n" + \
                "\"FontSmoothing\"=\"2\"\n" + \
                "\"FontSmoothingGamma\"=dword:00000578\n" + \
                "\"FontSmoothingOrientation\"=dword:00000001\n" + \
                "\"FontSmoothingType\"=dword:00000002\n\n"

REG_FONTLINK  = "[HKEY_LOCAL_MACHINE\Software\Microsoft\Windows NT\CurrentVersion\FontLink\SystemLink]\n" + \
                "\"Bitstream Vera Sans\"=str(7):\"kochi-gothic-subst.ttf,Kochi Gothic\\0uming.ttc,AR PL UMing\\0UnDotum.ttf,UnDotum\\0\"\n" + \
                "\"Bitstream Vera Serif\"=str(7):\"kochi-mincho-subst.ttf,Kochi Mincho\\0ukai.ttc,AR PL UKai\\0UnBatang.ttf,UnBatang\\0\"\n" + \
                "\"Lucida Sans Unicode\"=str(7):\"kochi-gothic-subst.ttf,Kochi Gothic\\0\"\n" + \
                "\"Microsoft Sans Serif\"=str(7):\"VeraSe.ttf,Bitstream Vera Sans\\0kochi-gothic-subst.ttf,Kochi Gothic\\0uming.ttc,AR PL UMing\\0UnDotum.ttf,UnDotum\\0\"\n" + \
                "\"MS PGothic\"=str(7):\"VeraSe.ttf,Bitstream Vera Sans\\0\"\n" + \
                "\"MS UI Gothic\"=str(7):\"VeraSe.ttf,Bitstream Vera Sans\\0kochi-gothic-subst.ttf,Kochi Gothic\\0\"\n" + \
                "\"Tahoma\"=str(7):\"VeraSe.ttf,Bitstream Vera Sans\\0kochi-gothic-subst.ttf,Kochi Gothic\\0uming.ttc,AR PL UMing\\0UnDotum.ttf,UnDotum\\0\"\n\n"

REG_FONTSUBS  = "[HKEY_LOCAL_MACHINE\Software\Microsoft\Windows NT\CurrentVersion\FontSubstitutes]\n" + \
                "\"Arial\"=\"Bitstream Vera Sans\"\n" + \
                "\"Batang\"=\"UnBatang\"\n" + \
                "\"BatangChe\"=\"UnBatang\"\n" + \
                "\"Dotum\"=\"UnDotum\"\n" + \
                "\"DotumChe\"=\"UnDotum\"\n" + \
                "\"Gulim\"=\"UnDotum\"\n" + \
                "\"GulimChe\"=\"UnDotum\"\n" + \
                "\"Helvetica\"=\"Bitstream Vera Sans\"\n" + \
                "\"MingLiU\"=\"AR PL UMing TW\"\n" + \
                "\"MS Gothic\"=\"Kochi Gothic\"\n" + \
                "\"MS Mincho\"=\"Kochi Mincho\"\n" + \
                "\"MS PGothic\"=\"Kochi Gothic\"\n" + \
                "\"MS PMincho\"=\"Kochi Mincho\"\n" + \
                "\"MS Shell Dlg\"=\"Bitstream Vera Sans\"\n" + \
                "\"MS Shell Dlg 2\"=\"Bitstream Vera Sans\"\n" + \
                "\"MS UI Gothic\"=\"Bitstream Vera Sans\"\n" + \
                "\"PMingLiU\"=\"AR PL UMing TW\"\n" + \
                "\"SimSun\"=\"AR PL UMing CN\"\n" + \
                "\"Songti\"=\"AR PL UMing CN\"\n" + \
                "\"Tahoma\"=\"Bitstream Vera Sans\"\n" + \
                "\"Times\"=\"Bitstream Vera Serif\"\n" + \
                "\"Tms Rmn\"=\"Bitstream Vera Serif\"\n\n"

REG_PATCHDLG   = {
  "ANSI":        "[HKEY_LOCAL_MACHINE\Software\Microsoft\Windows NT\CurrentVersion\FontSubstitutes]\n" + \
                 "\"MS Shell Dlg\"=\"Bitstream Vera Sans\"\n\n",
  "SHIFTJIS":    "[HKEY_LOCAL_MACHINE\Software\Microsoft\Windows NT\CurrentVersion\FontSubstitutes]\n" + \
                 "\"MS Shell Dlg\"=\"Kochi Gothic\"\n\n",
  "HANGUL":      "[HKEY_LOCAL_MACHINE\Software\Microsoft\Windows NT\CurrentVersion\FontSubstitutes]\n" + \
                 "\"MS Shell Dlg\"=\"UnDotum\"\n\n",
  "GB2312":      "[HKEY_LOCAL_MACHINE\Software\Microsoft\Windows NT\CurrentVersion\FontSubstitutes]\n" + \
                 "\"MS Shell Dlg\"=\"AR PL UMing CN\"\n\n",
  "CHINESEBIG5": "[HKEY_LOCAL_MACHINE\Software\Microsoft\Windows NT\CurrentVersion\FontSubstitutes]\n" + \
                 "\"MS Shell Dlg\"=\"AR PL UMing TW\"\n\n"
  }

REG_MENUH      = "[HKEY_CURRENT_USER\Control Panel\Desktop\WindowMetrics]\n\"MenuHeight\"="

REG_MENUW      = "[HKEY_CURRENT_USER\Control Panel\Desktop\WindowMetrics]\n\"MenuWidth\"="

REG_METRICS    = {
  "CaptionFont":   "[HKEY_CURRENT_USER\Control Panel\Desktop\WindowMetrics]\n\"CaptionFont\"=",
  "MenuFont":      "[HKEY_CURRENT_USER\Control Panel\Desktop\WindowMetrics]\n\"MenuFont\"=",
  "MessageFont":   "[HKEY_CURRENT_USER\Control Panel\Desktop\WindowMetrics]\n\"MessageFont\"=",
  "SmCaptionFont": "[HKEY_CURRENT_USER\Control Panel\Desktop\WindowMetrics]\n\"SmCaptionFont\"=",
  "StatusFont":    "[HKEY_CURRENT_USER\Control Panel\Desktop\WindowMetrics]\n\"StatusFont\"="
  }

'''
-------------------------------------------------------------------------------
Initialize global variables
-------------------------------------------------------------------------------
'''
HAVE_FONTS = {
  "AR PL UMing CN": False,
  "AR PL UMing TW": False,
  "Kochi Gothic":   False,
  "Kochi Mincho":   False,
  "UnBatang":       False,
  "UnDotum":        False
  }

DEFAULT_LOCALE = "en_US"
DEFAULT_EXE    = None
USE_SMOOTHING  = False
USE_HIDPIFONT  = False
USE_SHORTCUT   = False

LOGFONT = {
  "lfHeight":         10,
  "lfWidth":          0,
  "lfEscapement":     0,
  "lfOrientation":    0,
  "lfWeight":         400,
  "lfItalic":         0,
  "lfUnderline":      0,
  "lfStrikeOut":      0,
  "lfCharSet":        0,
  "lfOutPrecision":   0,
  "lfClipPrecision":  0,
  "lfQuality":        0,
  "lfPitchAndFamily": VARIABLE_PITCH ^ FF_SWISS,
  "lfFaceName":       "Bitstream Vera Sans"
  }

'''
-------------------------------------------------------------------------------
List of locales

This list is used to populate the drop-down menu and to know which UTF-8
setting to apply to the environment.

Greek/Hebrew/Arabic are currently borked.
-------------------------------------------------------------------------------
'''
LOCALES = {
  #"ar_AR": ("العربية", "ar_SA.UTF-8"),
  #"el_GR": ("Ελληνικά", "el_GR.UTF-8"),
  "en_US": ("English", "en_US.UTF-8"),
  #"he_IL": ("עברית", "he_IL.UTF-8"),
  "ja_JP": ("日本语", "ja_JP.UTF-8"),
  "ko_KR": ("한국어", "ko_KR.UTF-8"),
  "ru_RU": ("Русский", "ru_RU.UTF-8"),
  "zh_CN": ("中文(简体)", "zh_CN.UTF-8"),
  "zh_TW": ("中文(繁體)", "zh_TW.UTF-8"),
  }

LOCALE_TOGGLE = {
  #"ar_AR": False,
  #"el_GR": False,
  "en_US": True,
  #"he_IL": False,
  "ja_JP": False,
  "ko_KR": False,
  "ru_RU": True,
  "zh_CN": False,
  "zh_TW": False,
  }

'''
-------------------------------------------------------------------------------
class Base

Contains the GUI and all necessary function hooks.
-------------------------------------------------------------------------------
'''
class BaseForm:
  def __init__(self):
    # Window assignment
    self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    self.window.set_title(PROGRAM)
    self.window.set_size_request(400, -1)
    self.window.set_icon_from_file(ICON)
    self.window.set_border_width(8)
    
    # Container element
    self.box = gtk.VBox()
    self.box.set_spacing(8)
    self.window.add(self.box)
    
    # Row 1
    row1 = gtk.VBox()
    lblinstruct1 = gtk.Label(STRINGS.get("gui", "lblinstruct1"))
    lblinstruct1.set_alignment(0, 0)
    row1.pack_start(lblinstruct1, False, False)
    row1opts = gtk.HBox()
    row1opts.set_spacing(5)
    self.txtfile = gtk.Entry()
    row1opts.pack_start(self.txtfile, True, True)
    self.btnfile = gtk.Button(STRINGS.get("gui", "btnfile"), gtk.STOCK_OPEN)
    self.btnfile.set_size_request(90, -1)
    row1opts.pack_start(self.btnfile, False, False)
    row1.pack_start(row1opts, False, False)
    self.box.pack_start(row1, False, False)
    
    # Row 2
    row2 = gtk.VBox()
    lblinstruct2 = gtk.Label(STRINGS.get("gui", "lblinstruct2"))
    lblinstruct2.set_alignment(0, 0)
    row2.pack_start(lblinstruct2, False, False)
    self.cmblocales = gtk.combo_box_new_text()
    row2.pack_start(self.cmblocales, False, False)
    self.box.pack_start(row2, False, False)
    
    # Row 3
    row3 = gtk.Expander(STRINGS.get("gui", "expander"))
    row3rows = gtk.VBox()
    self.chksmoothing = gtk.CheckButton(STRINGS.get("gui", "chksmoothing"))
    row3rows.pack_start(self.chksmoothing, False, False)
    self.chk120dpi = gtk.CheckButton(STRINGS.get("gui", "chk120dpi"))
    row3rows.pack_start(self.chk120dpi, False, False)
    self.chkshortcut = gtk.CheckButton(STRINGS.get("gui", "chkshortcut"))
    row3rows.pack_start(self.chkshortcut, False, False)
    row3.add(row3rows)
    self.box.pack_start(row3, True, True)
    row3.connect("activate", self.resize)
    
    # Row 4
    row4 = gtk.HBox()
    row4.set_spacing(5)
    self.btnhelp = gtk.Button(STRINGS.get("gui", "btnhelp"), gtk.STOCK_HELP)
    self.btnhelp.set_size_request(90, -1)
    row4.pack_start(self.btnhelp, False, False)
    row4.pack_start(gtk.Label(""), True, True)
    self.btnclose = gtk.Button(STRINGS.get("gui", "btnclose"), gtk.STOCK_CLOSE)
    self.btnclose.set_size_request(90, -1)
    row4.pack_start(self.btnclose, False, False)
    self.btnexecute = gtk.Button(STRINGS.get("gui", "btnexecute"), gtk.STOCK_EXECUTE)
    self.btnexecute.set_size_request(90, -1)
    row4.pack_start(self.btnexecute, False, False)
    self.box.pack_start(row4, False, False)
    
    # Check which fonts exist (globals)
    context = self.txtfile.get_pango_context()
    set_fonts(context.list_families())
    
    # Store our current Gtk font info to a LOGFONT
    set_logfont_from_gtk(context.get_font_description())
    
    # Populate the locales drop-down
    LOCALES_LIST = get_locales()
    for s in LOCALES_LIST:
      self.cmblocales.append_text(s[0])
    self.cmblocales.set_active(0)
    
    # Fix the expander to suit work area
    self.expanded = False
    self.flatsize = None
    self.expasize = None
    
    # Events
    self.window.connect("destroy", self.destroy)
    self.window.connect("delete_event", self.delete)
    self.btnfile.connect("clicked", self.open)
    self.btnclose.connect("clicked", self.destroy)
    self.btnhelp.connect("clicked", self.about)
    self.btnexecute.connect("clicked", self.execute)
    get_logfont()
    
    # Update settings
    if(USE_SHORTCUT == True):
      self.chkshortcut.set_active(True)
    if(USE_SMOOTHING == True):
      self.chksmoothing.set_active(True)
    if(USE_HIDPIFONT == True):
      self.chk120dpi.set_active(True)
    for i in range(0, len(LOCALES_LIST)):
      if(LOCALES_LIST[i][1][0:5] == DEFAULT_LOCALE):
        self.cmblocales.set_active(i)
    
    if(DEFAULT_EXE != None):
      self.txtfile.set_text(DEFAULT_EXE)
      self.window.set_focus(self.btnexecute)
    
    self.window.show_all()
  
  '''
  void resize()
  
  Fix the expander to suit our work area.
  '''
  def resize(self, widget):
    if(self.expasize == None and self.flatsize == None):
      self.flatsize = self.window.get_size()
    elif(self.expasize == None):
      self.expasize = self.window.get_size()
    if(self.expanded == False and self.expasize != None):
      self.window.set_size_request(self.expasize[0], self.expasize[1])
      self.window.resize(self.expasize[0], self.expasize[1])
      self.expanded = True
    elif(self.expanded == True and self.flatsize != None):
      self.window.set_size_request(self.flatsize[0], self.flatsize[1])
      self.window.resize(self.flatsize[0], self.flatsize[1])
      self.expanded = False
    elif(self.expanded == False):
      self.expanded = True
  
  '''
  void open()
  
  Opens file dialog and sets self.txtfile to the selected file. 
  '''
  def open(self, widget, file_name=""):
    buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, \
               gtk.STOCK_OPEN, gtk.RESPONSE_OK)
    dialog = gtk.FileChooserDialog(STRINGS.get("file", "title"), None, \
                                   gtk.FILE_CHOOSER_ACTION_OPEN, buttons)
    # Add filters
    filter = gtk.FileFilter()
    filter.set_name(STRINGS.get("file", "exefilter"))
    filter.add_pattern("*.exe")
    filter.add_pattern("*.EXE")
    dialog.add_filter(filter)
    filter = gtk.FileFilter()
    filter.set_name(STRINGS.get("file", "allfilter"))
    filter.add_pattern("*")
    dialog.add_filter(filter)
    if dialog.run() == gtk.RESPONSE_OK:
      self.txtfile.set_text(dialog.get_filename())
    dialog.destroy()
  
  def click_website(self, dialog, link, data = None):
        url_show(link)
  '''
  void about()
  
  Create and display Gtk About dialog.
  '''
  def about(self, widget):
    gtk.about_dialog_set_url_hook(self.click_website)
    
    dialog = gtk.AboutDialog()
    dialog.set_icon_from_file(ICON)
    dialog.set_name(PROGRAM)
    dialog.set_version(VERSION)
    dialog.set_comments(STRINGS.get("about", "comments"))
    dialog.set_copyright(COPY)
    license = open(LICENSE, "r")
    dialog.set_license(license.read())
    dialog.set_logo(gtk.gdk.pixbuf_new_from_file(ICON))
    dialog.set_website(WEBSITE)
    dialog.run()
    dialog.destroy()
  
  '''
  void execute()
  
  Test if everything is set that needs to be for execution. commit all
  settings to the local config file.
  
  LOADING READY RUN!
  '''
  def execute(self, widget):
    # Should we even be doing this?
    if(self.txtfile.get_text() == ""):
      message = STRINGS.get("dialogs", "noexe1") + "\n\n" + \
                STRINGS.get("dialogs", "noexe2")
      dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, \
                                 gtk.BUTTONS_OK, message);
      dialog.set_title(STRINGS.get("dialogs", "errortitle"))
      dialog.set_icon_from_file(ICON)
      dialog.run()
      dialog.destroy()
      return(0)
    elif(os.path.exists(self.txtfile.get_text()) == False):
      message = STRINGS.get("dialogs", "exenotfound1") + "\n\n" + \
                STRINGS.get("dialogs", "exenotfound2")
      dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, \
                                 gtk.BUTTONS_OK, message);
      dialog.set_title(STRINGS.get("dialogs", "errortitle"))
      dialog.set_icon_from_file(ICON)
      dialog.run()
      dialog.destroy()
      return(0)
    
    self.window.hide()
    
    # Update settings
    global DEFAULT_LOCALE, USE_SMOOTHING, USE_HIDPIFONT, USE_SHORTCUT
    if(self.chkshortcut.get_active() == True):
      USE_SHORTCUT = True
    else:
      USE_SHORTCUT = False
    if(self.chksmoothing.get_active() == True):
      USE_SMOOTHING = True
    else:
      USE_SMOOTHING = False
    if(self.chk120dpi.get_active() == True):
      USE_HIDPIFONT = True
    else:
      USE_HIDPIFONT = False
    DEFAULT_LOCALE = self.cmblocales.get_active()
    
    configfp = open(CONFIG, "w+")
    config.write(configfp)
    configfp.close()
    
    shellwine(self.txtfile.get_text(), CODES[self.cmblocales.get_active()], \
              self.chkmsfonts.get_active())
    
    gtk.main_quit()
  
  '''
  void destroy()
  
  Hook to quit the GUI.
  '''
  def destroy(self, widget):
    gtk.main_quit()
  
  '''
  void delete()
  
  Hook to quit the GUI.
  '''
  def delete(self, widget, event):
    return False
  
  '''
  void main()
  
  The main GUI loop.
  '''
  def main(self):
    gtk.main()

'''
-------------------------------------------------------------------------------
bool get_ja()

Checks if fonts needed for Japanese support are present.
-------------------------------------------------------------------------------
'''
def get_ja():
  if(HAVE_FONTS["Kochi Gothic"] == True and HAVE_FONTS["Kochi Mincho"] == True):
    return(True)
  else:
    return(False)

'''
-------------------------------------------------------------------------------
bool get_ko()

Checks if fonts needed for Korean support are present.
-------------------------------------------------------------------------------
'''
def get_ko():
  if(HAVE_FONTS["UnBatang"] == True and HAVE_FONTS["UnDotum"] == True):
    return(True)
  else:
    return(False)

'''
-------------------------------------------------------------------------------
bool get_cn()

Checks if fonts needed for Simplified Chinese support are present.
-------------------------------------------------------------------------------
'''
def get_cn():
  if(HAVE_FONTS["AR PL UMing CN"] == True):
    return(True)
  else:
    return(False)

'''
-------------------------------------------------------------------------------
bool get_tw()

Checks if fonts needed for Traditional Chinese support are present.
-------------------------------------------------------------------------------
'''
def get_tw():
  if(HAVE_FONTS["AR PL UMing TW"] == True):
    return(True)
  else:
    return(False)

'''
-------------------------------------------------------------------------------
list get_locales()

Returns a list of all present locales.
-------------------------------------------------------------------------------
'''
def get_locales():
  LOCALE_LIST = [LOCALES["en_US"], LOCALES["ru_RU"]]
  if(get_cn() == True):
    LOCALE_LIST.append(LOCALES["zh_CN"])
  if(get_tw() == True):
    LOCALE_LIST.append(LOCALES["zh_TW"])
  if(get_ko() == True):
    LOCALE_LIST.append(LOCALES["ko_KR"])
  if(get_ja() == True):
    LOCALE_LIST.append(LOCALES["ja_JP"])
  return(LOCALE_LIST)

'''
-------------------------------------------------------------------------------
void set_fonts()

Updates globals with present system fonts.
-------------------------------------------------------------------------------
'''
def set_fonts(fonts):
  global HAS_BATANG, HAS_DOTUM, HAS_UMINGT, HAS_UMINGC, HAS_KGOTH, HAS_KMIN
  for font in fonts:
    if font.get_name() == 'UnBatang':
      HAS_BATANG = True
    elif font.get_name() == 'UnDotum':
      HAS_DOTUM  = True
    elif font.get_name() == 'AR PL UMing TW':
      HAS_UMINGT = True
    elif font.get_name() == 'AR PL UMing CN':
      HAS_UMINGC = True
    elif font.get_name() == 'Kochi Gothic':
      HAS_KGOTH  = True
    elif font.get_name() == 'Kochi Mincho':
      HAS_KMIN   = True

'''
-------------------------------------------------------------------------------
string get_logfont()

Build a binary LOGFONT value to pump into the registry. Wine default is
184 bytes long, so let's stick with that.

typedef struct tagLOGFONT { 
  LONG lfHeight;
  LONG lfWidth;
  LONG lfEscapement;     //leave it deafult
  LONG lfOrientation;    //leave it deafult
  LONG lfWeight;
  BYTE lfItalic;
  BYTE lfUnderline;      //bool False
  BYTE lfStrikeOut;      //bool False
  BYTE lfCharSet;
  BYTE lfOutPrecision;   //leave it default
  BYTE lfClipPrecision;  //leave it default
  BYTE lfQuality;        //try for ClearType?
  BYTE lfPitchAndFamily; 
  TCHAR lfFaceName[LF_FACESIZE]; //32 chars max including \0
} LOGFONT, *PLOGFONT;
-------------------------------------------------------------------------------
'''
def get_logfont():
  # Make sure we don't go over 32 character with the \0
  tempfont = LOGFONT["lfFaceName"]
  tempfon2 = ""
  if(len(tempfont) > 31):
    tempfont = tempfont[0:31]
  # Translate it to shorts
  for i in range(0, len(tempfont)):
    tempfon2 += tempfont[i:i+1] + "\0"
  # Make the binary string
  newstring = pack("<lllllbbbbbbbb",
                LOGFONT["lfHeight"] * -1, \
                LOGFONT["lfWidth"], \
                LOGFONT["lfEscapement"], \
                LOGFONT["lfOrientation"], \
                LOGFONT["lfWeight"], \
                LOGFONT["lfItalic"], \
                LOGFONT["lfUnderline"], \
                LOGFONT["lfStrikeOut"], \
                LOGFONT["lfCharSet"], \
                LOGFONT["lfOutPrecision"], \
                LOGFONT["lfClipPrecision"], \
                LOGFONT["lfQuality"], \
                LOGFONT["lfPitchAndFamily"], \
                ) + \
              tempfon2
  
  # Convert our LOGFONT to hex
  hexstring = "hex:"
  for i in range(0, len(newstring)):
    byte = unpack("B", newstring[i:i+1])
    hexnib = hex(byte[0])[2:]
    if(len(hexnib) < 2):
      hexnib = "0" + hexnib
    hexstring += hexnib + ","
  while(len(hexstring) < 277):
    hexstring += "00,"
  hexstring += "00"
  return(0)

'''
-------------------------------------------------------------------------------
void set_logfont()

Populates the global LOGFONT using data from Gtk.
-------------------------------------------------------------------------------
'''
def set_logfont_from_gtk(pangofont):
  global LOGFONT, WINE_MENUBAR
  LOGFONT["lfFaceName"] = pangofont.get_family()
  if(pangofont.get_style() & pango.STYLE_ITALIC or pangofont.get_style() & pango.STYLE_OBLIQUE):
    LOGFONT["lfItalic"] = 1
  LOGFONT["lfWeight"] = pangofont.get_weight() + 0
  LOGFONT["lfHeight"] = GTKTABLE_96[pangofont.get_size() / PANGO_SCALE][0]
  WINE_MENUBAR = GTKTABLE_96[pangofont.get_size() / PANGO_SCALE][1]
  LOGFONT["lfPitchAndFamily"] = VARIABLE_PITCH ^ FF_SWISS

'''
-------------------------------------------------------------------------------
void get_config()

Populates globals from the config file.
-------------------------------------------------------------------------------
'''
def get_config():
  configfp = open(CONFIG,'r')
  config = ConfigParser.ConfigParser()
  config.readfp(configfp)
  configfp.close()
  global LOGFONT, HAVE_FONTS, DEFAULT_LOCALE, USE_SMOOTHING, \
         USE_HIDPIFONT, USE_SHORTCUT
  # LOGFONT
  LOGFONT["lfHeight"]    = int(config.get("settings", "gtkfontsize"))
  LOGFONT["lfWeight"]    = int(config.get("settings", "gtkfontweight"))
  LOGFONT["lfItalic"]    = bool(int(config.get("settings", "gtkfontitalic")))
  if(int(config.get("settings", "gtkfontsize")) == 1):
    LOGFONT["lfQuality"] = CLEARTYPE_QUALITY
  else:
    LOGFONT["lfQuality"] = DEFAULT_QUALITY
  LOGFONT["lfFaceName"]  = config.get("settings", "gtkfontname")
  # HAVE_FONTS
  HAVE_FONTS["AR PL UMing CN"] = bool(int(config.get("settings", "has_umingc")))
  HAVE_FONTS["AR PL UMing TW"] = bool(int(config.get("settings", "has_umingt")))
  HAVE_FONTS["Kochi Gothic"]   = bool(int(config.get("settings", "has_kgoth")))
  HAVE_FONTS["Kochi Mincho"]   = bool(int(config.get("settings", "has_kmin")))
  HAVE_FONTS["UnBatang"]       = bool(int(config.get("settings", "has_batang")))
  HAVE_FONTS["UnDotum"]        = bool(int(config.get("settings", "has_dotum")))
  # LOCALE/SMOOTH/HIDPI
  DEFAULT_LOCALE = config.get("settings", "locale")
  USE_SMOOTHING  = bool(int(config.get("settings", "smoothing")))
  USE_HIDPIFONT  = bool(int(config.get("settings", "hidpifont")))
  USE_SHORTCUT   = bool(int(config.get("settings", "shortcut")))

'''
-------------------------------------------------------------------------------
void set_config()

Wipes the config file and populates it with default values.
-------------------------------------------------------------------------------
'''
def reset_config():
  configfp = open(CONFIG,'w')
  config = ConfigParser.ConfigParser()
  config.add_section("settings")
  # Main settings
  config.set("settings", "locale", DEFAULT_LOCALE)
  config.set("settings", "gtkfontname", LOGFONT["lfFaceName"])
  config.set("settings", "gtkfontsize", str(LOGFONT["lfHeight"]))
  config.set("settings", "gtkfontweight", str(LOGFONT["lfWeight"]))
  config.set("settings", "gtkfontitalic", str(LOGFONT["lfItalic"]))
  config.set("settings", "shortcut", str(int(USE_SHORTCUT)))
  config.set("settings", "smoothing", str(int(USE_SMOOTHING)))
  config.set("settings", "hidpifont", str(int(USE_HIDPIFONT)))
  config.set("settings", "has_batang", str(int(HAVE_FONTS["UnBatang"])))
  config.set("settings", "has_dotum", str(int(HAVE_FONTS["UnDotum"])))
  config.set("settings", "has_umingt", str(int(HAVE_FONTS["AR PL UMing TW"])))
  config.set("settings", "has_umingc", str(int(HAVE_FONTS["AR PL UMing CN"])))
  config.set("settings", "has_kgoth", str(int(HAVE_FONTS["Kochi Gothic"])))
  config.set("settings", "has_kmin", str(int(HAVE_FONTS["Kochi Mincho"])))
  config.write(configfp)
  configfp.close()
  

'''
-------------------------------------------------------------------------------
int shellwine()

Prepares the registry and shells Wine. This function will always return int 0.
-------------------------------------------------------------------------------
'''
def shellwine(executable, locale, msfonts = False):
  global CODES, LANG
  storelang = os.environ['LANG']
  os.environ['WINEDEBUG'] = "-all"
  fonts = "common"
  os.system("wine regedit.exe \"" + PATH + "/" + fonts + "/" + locale + \
            ".reg\" > /dev/null")
  exe = "Z:\\" + executable.replace("/", "\\")
  os.environ['LANG'] = LANG[CODES.index(locale)]
  os.system("wine \"" + exe + "\" > /dev/null")
  os.environ['LANG'] = storelang
  os.system("wine regedit.exe \"" + PATH + "/remove/" + locale + \
            ".reg\" > /dev/null")
  return(0)


'''
-------------------------------------------------------------------------------
Collect configuration data

***DISABLE CLI IF NOT CREATED, OTHERWISE ANGRY ELVES WILL EAT YOUR NOSEHAIR***
-------------------------------------------------------------------------------
'''
try:
  configfp = open(CONFIG,'r')
except IOError:
  reset_config()
  configfp = open(CONFIG,'r')
configfp.close()
get_config()

'''
-------------------------------------------------------------------------------
Main execution
-------------------------------------------------------------------------------
'''
print PROGRAM + " " + VERSION
print COPY

if(__name__ == "__main__"):
  # Pull out all command line options
  parser = OptionParser(version=VERSION, description=DESCRIP, \
                        usage="%prog [options] EXECUTABLE")
  parser.add_option("-l", "--locale", action="store", type="string", \
                    dest="locale", help="specify a locale in which to load" + \
                    " the target executable (ISO 3166 standard)")
  (options, args) = parser.parse_args()
  
  if(len(args) > 0 and options.locale != None):
    if(os.path.exists(args[0]) and CODES.index(options.locale) != False):
      shellwine(args[0], options.locale)
  
  else:
    if(options.locale != None):
      config.set("settings", "locale", str(CODES.index(options.locale)))
    #if(options.msfonts != None):
    #  config.set("settings", "msfonts", "1")
    executable = None
    if(len(args) > 0):
      if(os.path.exists(args[0])):
        executable = args[0]
    
    base = BaseForm()
    base.main()

