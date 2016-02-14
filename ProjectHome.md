# WineLocale #

_A lightweight locale changer for executing applications with Wine_

Author: `Derrick Sobodash <derrick＠cinnamonpirate.com>`

## About ##
WineLocale clones the functionality of [Microsoft AppLocale](http://www.microsoft.com/globaldev/tools/apploc.mspx) in [Wine](http://www.winehq.org/). It is used to manage locale and font settings in the Wine registry to ensure proper display of non-Latin type in pre-Unicode portable executables.

## Mission ##
The code must be readable. The code must be clean. The software must not deviate into areas that do not involve locale support in Wine. The software will make as few changes to the operating system as possible to function. The software will integrate as much as is possible into the Ubuntu desktop.

## Pictures ##

![http://winelocale.googlecode.com/svn/trunk/winelocale.png](http://winelocale.googlecode.com/svn/trunk/winelocale.png)

## Support ##

### Locales ###
  * ~~ar - Arabic~~ broken :(
  * en - English
  * ~~el\_GR - Greek~~ broken :(
  * ~~he\_IL - Hebrew~~ broken :(
  * ja\_JP - Japanese
  * ko\_KR - Korean
  * ru\_RU - Russian
  * zh\_CN - Chinese
  * zh\_TW - Chinese (Traditional)

You can help to get more locales supported by supplying a small, sample Windows application in the target locale.

### GUI localizations ###
  * Dansk _by Askrates_
  * English (US) _by author_
  * Español (Latin America) _by Alejandro Moreno_
  * Español (Mexico) _by Alejandro Moreno_
  * Italiano _by Daniele Dell'Erba_
  * Portuguese (Brasil) _by gamer\_boy & tvtoon_
  * 한국어 _by Tong Pa Jung_ ([incomplete](http://winelocale.googlecode.com/svn/trunk/current/i18n/ko_KR.lang))
  * 中文(简体) (China) _by Jacky Waiss_

## Features ##
  * Create a "shortcut" script in ~/.local/bin to skip the GUI. Creation of a .desktop shortcut is left to the user.
  * Fixes the menubar in Wine software to match the size and fonts used by your Gtk theme. Users will have to set colors on their own through WineCfg.
  * Optional support registry patches to enable 120dpi fonts and font smoothing (not as nice as ClearType).
  * Picks up the executable name from the path, meaning it is safe to associate Windows executables with WineLocale.
  * Ties into the Ubuntu locale manager and lists only those languages for which you have added support.

## Donations ##
Donations I receive for this project are associated with it exclusively. Donating to WineLocale **does not** send money to Wine developers.

This means donations only encourage the investigation and development of this locale tool. If an application cannot function at all in Wine, donations to WineLocale will not help to solve this problem.

If you still wish to donate, you may send a small sum to dsobodash＠gmail.com via [PayPal](https://www.paypal.com/).