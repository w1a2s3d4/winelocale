#! /bin/sh

#-----------------------------------------------------------------------------
# WineLocale
#-----------------------------------------------------------------------------

all:
	@echo "Makefile: Available actions: install, uninstall"

# install the script
install:
	mkdir /usr/local/share/wineloc
	cp -r ./src/* /usr/local/share/wineloc
	ln -s /usr/local/bin/wineloc /usr/local/share/wineloc/wineloc.php
