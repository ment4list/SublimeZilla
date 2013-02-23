SublimeZilla
============

A [Sublime Text 2](http://www.sublimetext.com/) plugin that imports server entries from [FileZilla](http://filezilla-project.org/) to Sublime Text as a sftp-config.json file for use with the excellent [Sublime SFTP](http://wbond.net/sublime_packages/sftp) plugin

## Installation

### Manual / Old School:
Clone or [download](https://github.com/ment4list/SublimeZilla/archive/master.zip) git repo into your packages folder

### Using [Package Control](http://wbond.net/sublime_packages/package_control):
Run `Package Control: Install Package` command, find and install `SublimeZilla` plugin.

## Usage

1. You can run the plugin by using the Command Palette (`Ctrl+Alt+Z`) type SublimeZilla or `fz` (yay fuzzy search! =D ) and hit enter. Or by going to Tools -> Sublime Zilla

2. On the first run you'll be asked to browse to your FileZilla XML file via the input panel (at the bottom of the screen) which is located as follows:

	* Windows 7 & Vista – `C:\Users\[USER_NAME]\AppData\Roaming\FileZilla\sitemanager.xml`
	* Mac OS X – `/users/[USER_NAME]/.filezilla/sitemanager.xml`
	* Linux – `/home/[USER_NAME]/.filezilla/sitemanager.xml`

3. A quick search will pop up with a list of all the servers contained in the FileZilla database. Select the one you want.

4. A new file will be opened called `sftp-config.json`. Save this file in the root of your project

5. You can now interact with this server via the SFTP plugin

Help
====

Unfortunatly I'm unable to test it on Linux or OSX. Please let me know if it is working!

Please report bugs here so I can try and fix it.

Thanks for trying it out!