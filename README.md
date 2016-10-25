SublimeZilla
============

A [Sublime Text 2](http://www.sublimetext.com/) and [3](http://www.sublimetext.com/3) plugin that imports server entries from [FileZilla](http://filezilla-project.org/) to Sublime Text as a sftp-config.json file for use with the excellent [Sublime SFTP](http://wbond.net/sublime_packages/sftp) plugin.

## Installation

### Using [Package Control](http://wbond.net/sublime_packages/package_control) (preferred way):
Run `Package Control: Install Package` command, find and install `SublimeZilla` plugin.

### Manual / Old School:
Clone or [download](https://github.com/ment4list/SublimeZilla/archive/master.zip) git repository into your Packages folder.

## Usage

1. You can run the plugin by using the Command Palette (`Ctrl+Alt+Z`, Windows/Linux | `Cmd+Alt+Z`, OS X) type SublimeZilla or `fz` and hit enter, or by going to Tools -> SublimeZilla.

2. On the first run, you'll be asked to browse to your FileZilla XML file (sitemanager.xml) via the input panel (at the bottom of the screen) which is located by default as follows:

	* Windows – `C:\Users\[USER_NAME]\AppData\Roaming\FileZilla\sitemanager.xml`
	* OS X – `/Users/[USER_NAME]/.config/filezilla/sitemanager.xml`
	* Linux – `/home/[USER_NAME]/.filezilla/sitemanager.xml`

3. A quick search will pop up with a list of all the servers contained in the FileZilla database. Select the one you want.

4. A new file will be opened called `sftp-config.json`. Save this file in the root of your project.

5. You can now interact with this server via the SFTP plugin.

### Alternate locations

Only 2 locations are supported at the moment. To save the first one follow steps 1 and 2 above.

A new file will have been created in `/Packages/User/SublimeZilla.sublime-settings` and it will contain a path to the default FileZilla DB:

`"filezilla_db_path": "C:\Users\[USER_NAME]\AppData\Roaming\FileZilla\sitemanager.xml"`

To add another path you can add a `"filezilla_db_path2"` setting with the secondary path as it's value.


Help
====

The plugin has been tested with Sublime Text 2 and 3, using FileZilla 3.7.4.1, on Windows 7, OS X 10.9.1 and Ubuntu Linux 13.10.

Please report bugs here so we can try and fix it.

Troubleshooting
====

### FileZilla not found error

If the plugin has trouble accessing FileZilla try changing the default location to your `sitemanager.xml` file.

To do this, create a new file called `SublimeZilla.sublime-settings` in `/Packages/User/`. 

Add the following to this new file:

* For Windows: 
`{"filezilla_db_path": "C:\Users\[USER_NAME]\AppData\Roaming\FileZilla\sitemanager.xml"}`
* For OSX: 
`{"filezilla_db_path" : "/Users/[OSX_USER]/.config/filezilla/sitemanager.xml"}`

Thanks for trying it out!
