SublimeZilla
============

A [Sublime Text 2](http://www.sublimetext.com/) plugin that imports server entries from [FileZilla](http://filezilla-project.org/) to Sublime Text as a sftp-config.json file for use with the excellent [Sublime SFTP](http://wbond.net/sublime_packages/sftp) plugin

## Installation

### Manual / Old School:
Clone or [download](https://github.com/ment4list/SublimeZilla/archive/master.zip) git repo into your packages folder

### Using [Package Control](http://wbond.net/sublime_packages/package_control):
Run `Package Control: Install Package` command, find and install `SublimeZilla` plugin.

## Usage

1. You can run the plugin by using the Command Palette (`Ctrl+Shif+P`) type SublimeZilla or `fz` (yay fuzzy search! =D ) and hit enter. Or by going to Tools -> Sublime Zilla

2. On the first run you'll be asked to browse to your FileZilla XML file which is in `c:\Users\[USER_NAME]\AppData\Roaming\FileZilla\sitemanager.xml` by default

3. A quick search will pop up with a list of all the servers contained in the FileZilla database. Select the one you want.

4. A new file will be opened called `sftp-config.json`. Save this file in the root of your project