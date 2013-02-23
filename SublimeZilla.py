import sublime, sublime_plugin
import shutil
import os
import re

from xml.dom import minidom

class SublimeZillaCommand(sublime_plugin.WindowCommand):
	def run(self):
		# check settings
		settings = sublime.load_settings("SublimeZilla.sublime-settings")

		if settings.get("filezilla_db_path", "") == "":
			self.window.show_input_panel( 'Browse to FileZilla directory', self.get_xml(), self.save_config, None, None )
		else:
			self.quick_panel()

	def quick_panel(self):
		server_names = self.get_server_names()
		self.window.show_quick_panel( server_names, self.server_chosen, sublime.MONOSPACE_FONT )

	# A server was chosen
	def server_chosen(self, server_index):
		if server_index == -1:
			return

		self.server = self.get_server(server_index)

		# Copy default SFTP config to current project root
		packages_path = sublime.packages_path()
		sftp_path = packages_path + "/SFTP/"
		sftp_path_default_config = sftp_path + "SFTP.default-config"

		if not os.path.exists( sftp_path ):
			sublime.error_message("SFTP not installed. Exiting...")
			return None

		if not os.path.exists( sftp_path_default_config ):
			sublime.error_message("SFTP default config not found. Exiting...")
			return None

		self.set_sftp_config();

	def set_sftp_config(self):

		import json

		server_config = {
			"type": "ftp",
			"save_before_upload": True,
			"upload_on_save": False,
			"sync_down_on_open": False,
			"sync_skip_deletes": False,
			"confirm_downloads": False,
			"confirm_sync": True,
			"confirm_overwrite_newer": False,
			"host": self.server["host"],
			"user": self.server["user"],
			"password": self.server["password"],
			"port": self.server["port"],
			"remote_path": self.server["remote_path"],
			"connect_timeout": 30
		}

		config_json = json.dumps(server_config)

		config_view = self.window.new_file()
		config_view.set_name("sftp-config.json")
		config_view.set_syntax_file("Packages/JavaScript/JSON.tmLanguage")

		config_edit = config_view.begin_edit()

		config_view.insert(config_edit, 0, config_json)
		config_view.end_edit(config_edit)

	def get_xml(self):

		current_os = sublime.platform()
		os_username = os.environ.get( "USERNAME" )

		# The default locations for FileZilla's XML database
		if( current_os == "windows" ):
			default_xml = "c:\\Users\\" + os_username + "\\AppData\\Roaming\\FileZilla\\sitemanager.xml"
		elif( current_os == "linux" ):
			default_xml = "/home/" + os_username + "/.filezilla/sitemanager.xml"
		elif( current_os == "osx" ):
			default_xml = "/users/" + os_username + "/.filezilla/sitemanager.xml"

		settings = sublime.load_settings("SublimeZilla.sublime-settings")
		path = settings.get("filezilla_db_path", default_xml)

		if not os.path.exists( path ):
			path = settings.get("filezilla_db_path2", default_xml)

		return path


	def save_config(self, filezilla_db_path):
		settings = sublime.load_settings("SublimeZilla.sublime-settings")
		settings.set("filezilla_db_path", filezilla_db_path)
		sublime.save_settings("SublimeZilla.sublime-settings")

		# Now, show the quick panel
		self.quick_panel()

	def create_project_config(self):
		self.config_view = self.window.new_file()
		self.window.run_command('sublime_zilla_config', new_file=self.config_view)

	def get_server_names(self):
		self.servers = self.get_server_entries()
		server_names = []

		for server_name in self.servers:
			server_names.append(server_name["name"])

		return server_names

	def get_server_entries(self):
		xmldoc = minidom.parse( self.get_xml() )
		itemlist = xmldoc.getElementsByTagName('Server')
		server_array = []

		for server in itemlist :

			server_obj = {}

			Name = server.getElementsByTagName('Name')
			NameVal = Name[0].firstChild.nodeValue
			server_obj["name"] = str(NameVal)

			Host = server.getElementsByTagName('Host')
			HostVal = Host[0].firstChild.nodeValue
			server_obj["host"] = str(HostVal)

			Port = server.getElementsByTagName('Port')
			PortVal = Port[0].firstChild.nodeValue
			server_obj["port"] = str(PortVal)

			User = server.getElementsByTagName('User')
			UserVal = User[0].firstChild.nodeValue
			server_obj["user"] = str(UserVal)

			Pass = server.getElementsByTagName('Pass')
			PassVal = Pass[0].firstChild.nodeValue
			server_obj["password"] = str(PassVal)

			LocalDir = server.getElementsByTagName('LocalDir')

			if( LocalDir[0].firstChild is not None ):
				LocalDirVal = LocalDir[0].firstChild.nodeValue
				server_obj["local_path"] = str(LocalDirVal)
			else:
				server_obj["local_path"] = ""

			RemoteDir = server.getElementsByTagName('RemoteDir')

			if( RemoteDir[0].firstChild is not None ):
				RemoteDirVal = RemoteDir[0].firstChild.nodeValue
				server_obj["remote_path"] = self.convertRemoteDir( str(RemoteDirVal) )
			else:
				server_obj["remote_path"] = ""

			# Add this server to the array
			server_array.append(server_obj)

		return server_array

	# Converts FileZilla's weird export method for remote directories to actual directories
	def convertRemoteDir( self, filezilla_dir ):

		# @Note botg's comment here: http://forum.filezilla-project.org/viewtopic.php?f=1&t=15923 might shed some light on why FileZilla exports the directories this way

		regex = "^((\d{1,2}\s){3})(.+)?$"
		modifiers = "gm"

		re_compile = re.compile( regex, re.M )
		results = re.split( regex, filezilla_dir )

		try:
			fz_remote_dir = results[3]
			# Replace all instances of \s\d{1,2}\s within capture group 3 with a "/" because it is seen as a directory by FileZilla
			slash_regex = "\s\d{1,2}\s"

			with_slashes = re.split( slash_regex, fz_remote_dir )

			return "/" + "/".join( with_slashes ) + "/"

		except IndexError:
			return '/'

	def get_server(self, server_index):
		return self.servers[server_index]

	# getDirectories taken from Packages\SideBarEnhancements\sidebar\SideBarProject.py
	def getDirectories(self):
		return sublime.active_window().folders()
