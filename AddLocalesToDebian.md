## Introduction ##

Generally, Debian, and especially its cousin Ubuntu, attempt to make using Linux as easy as possible. Nearly anything a user could want to do can be accomplished through supplied interface or through apt.

While both maintain language support packages, these packages center on Unicode -- specifically UTF-8 -- encodings and most packages will not provide the other code pages on which Windows applications depend.

Unfortunately, this leaves the end user to bash the system until necessary code pages become available: no easy task since no one anywhere has ever bothered to write how this works.

Assuming you are installing WineLocale from its supplied Debian package, these steps will be handled for you. However, if you are one of those truly distrustful users who will trust an author's software but not his package, then these steps may be for you.

## Querying Locales ##

Before attempting to add new code pages to your system locales, it is a good idea to make sure you do not already have said code page installed. The command to display all currently installed locales is:

```
locale -a
```

This command, when executed on a default install of Debian or Ubuntu, should display something similar to the following output:

```
d@cinnamon:~$ locale -a
C
en_AU.utf8
en_BW.utf8
en_CA.utf8
en_DK.utf8
en_GB.utf8
en_HK.utf8
en_IE.utf8
en_IN
en_NZ.utf8
en_PH.utf8
en_SG.utf8
en_US.utf8
en_ZA.utf8
en_ZW.utf8
POSIX
```

That's really useful if we speak English, but even installing extra language packs will not add anything more than "ja\_JP.utf8". Great for word processing, browsing or displaying Japanese localizations of software, but bad for displaying the text in pre-Unicode Windows software.

Assuming the code page you need to add is not shown above, the next step will be to add it.

## Adding a Code Page ##

First thing is first: you need to know which code page to add. If this is for WineLocale or Wine in general, it would be a good idea to check [LocaleEquivalentsForWindowsLanguages](LocaleEquivalentsForWindowsLanguages.md) to find out which code page you must add.

Debian stores its locale settings in /var/lib/locales/supported.d. There is one file for each available language, each named using the two letter codes specified in the [ISO 639-2](http://www.loc.gov/standards/iso639-2/php/English_list.php) standard. If the file for your language does not exist yet, you must create it.

For the following example, we will add the Shift-JIS code page for Japanese language to the system's list of supported locales.

Since the ISO 639-2 code for Japanese is "ja", we must create /var/lib/locales/supported.d/ja as a file. We will use the touch command for this:

```
sudo touch /var/lib/locales/supported.d/ja
```

This will create an empty file for Japanese locale. We now need to add the line for a Shift-JIS code page to it. While we are at it, we should also add Japanese Unicode and EUC-JP encoding, two other code pages common in Japanese software.

Using that wonderful tool echo, let's add some lines to the new Japanese file.

```
sudo echo "ja_JP.UTF-8 UTF-8" >>/var/lib/locales/supported.d/ja
sudo echo "ja_JP SJIS" >>/var/lib/locales/supported.d/ja
sudo echo "ja_JP.EUC-JP EUC-JP" >>/var/lib/locales/supported.d/ja
```

You may want to use cat on the file to make sure all three entries are stored correctly. Assuming they are, the only remaining step is to update your system locales using dpkg.

```
sudo dpkg-reconfigure locales
```

This should print out a lot of information, and hopefully a "done" for each new encoding. Try running the command a second time if you encounter any errors. Shift-JIS has a tendency to throw a notice, though it will be enabled. Subsequent runs of the command should not display said notice.

## Errors ##

None known. Comment on this page if you encounter any trouble!