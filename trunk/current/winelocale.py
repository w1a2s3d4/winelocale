#!/usr/bin/python2.5
# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------
import os
from optparse import OptionParser
import pygtk
pygtk.require('2.0')
import gtk
import ConfigParser

#------------------------------------------------------------------------------
# Program information
#------------------------------------------------------------------------------
PROGRAM = "WineLocale"
AUTHOR  = "Derrick Sobodash"
COPY    = "Copyright © 2007-2008 Derrick Sobodash"
VERSION = "0.1.0"
LICENSE = "BSD"
DESCRIP = "WineLocale clones the functionality of Microsoft AppLocale in " + \
          "Wine. It is used to manage global locale settings and font " + \
          "settings in the Wine registry to ensure proper display of " + \
          "non-Latin type in pre-Unicode portable executables."
WEBSITE = "http://cinnamonpirate.com/"
CONFIG  = "user/.winelocalerc"
PATH    = "winelocale"
ICON    = PATH + "/winelocale.svg"
LICENSE = PATH + "/LICENSE"

#------------------------------------------------------------------------------
# Fetch config file to variable
#------------------------------------------------------------------------------
configfp = open(CONFIG,'r')
config = ConfigParser.ConfigParser()
config.readfp(configfp)
configfp.close()
#config.get("settings", "winfonts")
#config.write(CONFIG)

#------------------------------------------------------------------------------
# List of available languages
#------------------------------------------------------------------------------
LOCALES = [
  "English",
  "Ελληνικά",
  "Русский",
  "עברית",
  "العربية",
  "中文(简体)",
  "中文(繁體)",
  "한국어",
  "日本语"]

CODES   = [
  "en",
  "el_GR",
  "ru_RU",
  "he_IL",
  "ar_SA",
  "zh_CN",
  "zh_TW",
  "ko_KR",
  "ja_JP"]

LANG    = [
  "en",
  "el_GR.ISO-8859-7",
  "ru_RU.ISO-8859-5",
  "he_IL.ISO-8859-8",
  "ar_SA.ISO-8859-6",
  "zh_CN",
  "zh_TW",
  "ko_KR.EUC-KR",
  "ja_JP"]

#------------------------------------------------------------------------------
# Base window
#------------------------------------------------------------------------------
class Base:
  def __init__(self):
    # Window setup
    self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    self.window.set_title(PROGRAM)
    self.window.set_size_request(400, -1)
    self.window.set_icon_from_file(ICON)
    self.window.set_border_width(8)
    
    # VBox
    self.box = gtk.VBox()
    self.box.set_spacing(8)
    self.window.add(self.box)
    
    # Row 1
    row1 = gtk.VBox()
    lblinstruct1 = gtk.Label("Select a portable executable (PE) file:")
    lblinstruct1.set_alignment(0, 0)
    row1.pack_start(lblinstruct1, False, False)
    row1opts = gtk.HBox()
    row1opts.set_spacing(5)
    self.txtfile = gtk.Entry()
    row1opts.pack_start(self.txtfile, True, True)
    self.btnfile = gtk.Button("Open", gtk.STOCK_OPEN)
    self.btnfile.set_size_request(90, -1)
    row1opts.pack_start(self.btnfile, False, False)
    row1.pack_start(row1opts, False, False)
    self.box.pack_start(row1, False, False)
    
    # Row 2
    row2 = gtk.VBox()
    lblinstruct2 = gtk.Label("Select a system language:")
    lblinstruct2.set_alignment(0, 0)
    row2.pack_start(lblinstruct2, False, False)
    self.cmblocales = gtk.combo_box_new_text()
    for s in LOCALES:
      self.cmblocales.append_text(s)
    self.cmblocales.set_active(0)
    row2.pack_start(self.cmblocales, False, False)
    self.box.pack_start(row2, False, False)
    
    # Row 3
    row3 = gtk.Expander("Extended options:")
    row3rows = gtk.VBox()
    self.chkmsfonts = gtk.CheckButton("Use Microsoft fonts")
    row3rows.pack_start(self.chkmsfonts, False, False)
    self.chkshortcut = gtk.CheckButton("Create shortcut in ~/.local/bin")
    row3rows.pack_start(self.chkshortcut, False, False)
    row3.add(row3rows)
    self.box.pack_start(row3, True, True)
    row3.connect("activate", self.resize)
    
    # Row 4
    row4 = gtk.HBox()
    row4.set_spacing(5)
    self.btnhelp = gtk.Button("Help", gtk.STOCK_HELP)
    self.btnhelp.set_size_request(90, -1)
    row4.pack_start(self.btnhelp, False, False)
    row4.pack_start(gtk.Label(""), True, True)
    self.btnclose = gtk.Button("Close", gtk.STOCK_CLOSE)
    self.btnclose.set_size_request(90, -1)
    row4.pack_start(self.btnclose, False, False)
    self.btnexecute = gtk.Button("Execute", gtk.STOCK_EXECUTE)
    self.btnexecute.set_size_request(90, -1)
    row4.pack_start(self.btnexecute, False, False)
    self.box.pack_start(row4, False, False)
    
    # Fix the expander to suit work area
    self.expanded = False
    self.flatsize = None
    self.expasize = None
    
    # Events
    self.window.connect("destroy", self.destroy)
    self.window.connect("delete_event", self.delete_event)
    self.btnfile.connect("clicked", self.fileopen)
    self.btnclose.connect("clicked", self.destroy)
    self.btnhelp.connect("clicked", self.about)
    self.btnexecute.connect("clicked", self.execute)
    
    # Update settings
    if(config.get("settings", "msfonts") == "1"):
      self.chkmsfonts.set_active(True)
    if(config.get("settings", "shortcut") == "1"):
      self.chkshortcut.set_active(True)
    if(config.get("settings", "locale")):
      self.cmblocales.set_active(int(config.get("settings", "locale")))
    if(executable != None):
      self.txtfile.set_text(executable)
      self.window.set_focus(self.btnexecute)
    
    self.window.show_all()
  
  # Fix the expander to suit our work area
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
  
  # Open file dialog
  def fileopen(self, widget, file_name=""):
    buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, \
               gtk.STOCK_OPEN, gtk.RESPONSE_OK)
    dialog = gtk.FileChooserDialog("Open File", None, \
                                   gtk.FILE_CHOOSER_ACTION_OPEN, buttons)
    # Add filters
    filter = gtk.FileFilter()
    filter.set_name("Portable executable")
    filter.add_pattern("*.exe")
    filter.add_pattern("*.EXE")
    dialog.add_filter(filter)
    filter = gtk.FileFilter()
    filter.set_name("All files")
    filter.add_pattern("*")
    dialog.add_filter(filter)
    if dialog.run() == gtk.RESPONSE_OK:
      self.txtfile.set_text(dialog.get_filename())
    dialog.destroy()
  
  # Display Gtk About dialog
  def about(self, widget):
    dialog = gtk.AboutDialog()
    dialog.set_icon_from_file(ICON)
    dialog.set_name(PROGRAM)
    dialog.set_version(VERSION)
    dialog.set_comments("A locale manager for Wine")
    dialog.set_copyright(COPY)
    license = open(LICENSE, "r")
    dialog.set_license(license.read())
    dialog.set_logo(gtk.gdk.pixbuf_new_from_file(ICON))
    dialog.set_website(WEBSITE)
    dialog.run()
    dialog.destroy()
  
  def execute(self, widget):
    # Should we even be doing this?
    if(self.txtfile.get_text() == ""):
      message = "You have not supplied the path to an executable file.\n\n" + \
                "Please click the Open button and browse to select a file."
      dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, \
                                 gtk.BUTTONS_OK, message);
      dialog.set_title("Flagrant System Error!")
      dialog.set_icon_from_file(ICON)
      dialog.run()
      dialog.destroy()
      return(0)
    elif(os.path.exists(self.txtfile.get_text()) == False):
      message = "The system was unable to find the executable you " + \
                "specified.\n\nPlease check that the supplied path is " + \
                "correct and try again."
      dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, \
                                 gtk.BUTTONS_OK, message);
      dialog.set_title("Flagrant System Error!")
      dialog.set_icon_from_file(ICON)
      dialog.run()
      dialog.destroy()
      return(0)
    
    self.window.hide()
    
    # Update settings
    if(self.chkmsfonts.get_active() == True):
      config.set("settings", "msfonts", "1")
    else:
      config.set("settings", "msfonts", "0")
    if(self.chkshortcut.get_active() == True):
      config.set("settings", "shortcut", "1")
    else:
      config.set("settings", "shortcut", "0")
    config.set("settings", "locale", self.cmblocales.get_active())
    
    configfp = open(CONFIG, "w+")
    config.write(configfp)
    configfp.close()
    
    shellwine(self.txtfile.get_text(), CODES[self.cmblocales.get_active()], \
              self.chkmsfonts.get_active())
    
    gtk.main_quit()
  
  def destroy(self, widget):
    gtk.main_quit()
  
  def delete_event(self, widget, event):
    return False
  
  def main(self):
    gtk.main()


#------------------------------------------------------------------------------
# Welcome to the magic kingdom!
#------------------------------------------------------------------------------
def shellwine(executable, locale, msfonts = False):
  global CODES
  global LANG
  storelang = os.environ['LANG']
  os.environ['WINEDEBUG'] = "-all"
  fonts = "common"
  if(msfonts == True):
  	fonts = "win"
  os.system("wine regedit.exe \"" + PATH + "/" + fonts + "/" + locale + \
            ".reg\" > /dev/null")
  exe = "Z:\\" + executable.replace("/", "\\")
  os.environ['LANG'] = LANG[CODES.index(locale)]
  os.system("wine \"" + exe + "\" > /dev/null")
  os.environ['LANG'] = storelang
  os.system("wine regedit.exe \"" + PATH + "/remove/" + locale + \
            ".reg\" > /dev/null")
  return(0)

#------------------------------------------------------------------------------
# Execute
#------------------------------------------------------------------------------
print PROGRAM + " " + VERSION
print COPY

if(__name__ == "__main__"):
  # Pull out all command line options
  parser = OptionParser(version=VERSION, description=DESCRIP, \
                        usage="%prog [options] EXECUTABLE")
  parser.add_option("-l", "--locale", action="store", type="string", \
                    dest="locale", help="specify a locale in which to load" + \
                    " the target executable (ISO 3166 standard)")
  parser.add_option("-m", "--msfont", action="store_true", dest="msfonts", \
                    help="use Microsoft fonts instead of free fonts")
  (options, args) = parser.parse_args()
  
  if(len(args) > 0 and options.locale != None):
    if(os.path.exists(args[0]) and CODES.index(options.locale) != False):
      shellwine(args[0], options.locale, options.msfonts)
  
  else:
    if(options.locale != None):
      config.set("settings", "locale", str(CODES.index(options.locale)))
    if(options.msfonts != None):
      config.set("settings", "msfonts", "1")
    executable = None
    if(len(args) > 0):
      if(os.path.exists(args[0])):
        executable = args[0]
    
    base = Base()
    base.main()

