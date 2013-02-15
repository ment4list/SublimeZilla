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
			self.window.show_input_panel( 'Browse to FileZilla directory', "c:\\", self.save_config, None, None )

		server_names = self.get_server_names()

		self.window.show_quick_panel( server_names, self.server_chosen, sublime.MONOSPACE_FONT )

	# A server was chosen
	def server_chosen(self, server_index):
		if server_index == -1:
			return

		self.server = self.get_server(server_index)
		print self.server["name"]

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

		project_folder = self.getProjectFolder()

		# Copy the default SFTP config file to the project
		# shutil.copy2(sftp_path_default_config, project_folder + "/config.sftp-config")
		f = project_folder + "/config.sftp-config"

		config_file = open(f, 'w')

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
			"remote_path": "/",
			# "remote_path": self.server["remote_path"],
			"connect_timeout": 30
		}

		config_json = json.dumps(server_config)
		print config_json

		config_file.write(config_json)
		config_file.close()

		config_view = self.window.open_file(f)
		config_view.set_syntax_file('Packages/JavaScript/JSON.tmLanguage')

		# sublime_plugin.on_load(config_view)

		# config_edit = config_view.begin_edit()
		# config_view.insert(config_edit, 0, str( config_json ) )
		# config_view.end_edit(config_edit)

		# if not config_view.is_loading():
			# config = sublime.load_settings("config.sftp-config")

			# config.set( "type", "ftp" )

			# config.set( "save_before_upload", True )
			# config.set( "upload_on_save", False )
			# config.set( "sync_down_on_open", False )
			# config.set( "sync_skip_deletes", False )
			# config.set( "confirm_downloads", False )
			# config.set( "confirm_sync", True )
			# config.set( "confirm_overwrite_newer", False )

			# config.set( "host", self.server["host"] )
			# config.set( "user", self.server["user"] )
			# config.set( "password", self.server["password"] )
			# config.set( "port", self.server["port"] )
			# config.set( "remote_path", "/" )
			# # config.set( "remote_path", self.server["remote_path"] )
			# config.set( "connect_timeout", 30 )

			# sublime.save_settings("config.sftp-config")

	def save_config(self, filezilla_db_path):
		print "DB Path:"
		print filezilla_db_path
		settings = sublime.load_settings("SublimeZilla.sublime-settings")
		settings.set("filezilla_db_path", filezilla_db_path)
		sublime.save_settings("SublimeZilla.sublime-settings")

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
		fz_xml = "c:\Users\Jurgens\AppData\Roaming\FileZilla\sitemanager.xml"
		xmldoc = minidom.parse(fz_xml)
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
			# print Port[0].firstChild.nodeValue
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

			RemoteDir = server.getElementsByTagName('RemoteDir')

			if( RemoteDir[0].firstChild is not None ):
				RemoteDirVal = RemoteDir[0].firstChild.nodeValue
				server_obj["remote_path"] = str(RemoteDirVal)

			# Add this server to the array
			server_array.append(server_obj)

		return server_array

	def get_server(self, server_index):
		return self.servers[server_index]

	# getDirectories taken from Packages\SideBarEnhancements\sidebar\SideBarProject.py
	def getDirectories(self):
		return sublime.active_window().folders()

	# getProjectFile taken from Packages\SideBarEnhancements\sidebar\SideBarProject.py
	def getProjectFile(self):
		if not self.getDirectories():
			return None
		import json
		data = file(os.path.normpath(os.path.join(sublime.packages_path(), '..', 'Settings', 'Session.sublime_session')), 'r').read()
		data = data.replace('\t', ' ')
		data = json.loads(data, strict=False)
		projects = data['workspaces']['recent_workspaces']

		if os.path.lexists(os.path.join(sublime.packages_path(), '..', 'Settings', 'Auto Save Session.sublime_session')):
			data = file(os.path.normpath(os.path.join(sublime.packages_path(), '..', 'Settings', 'Auto Save Session.sublime_session')), 'r').read()
			data = data.replace('\t', ' ')
			data = json.loads(data, strict=False)
			if 'workspaces' in data and 'recent_workspaces' in data['workspaces'] and data['workspaces']['recent_workspaces']:
				projects += data['workspaces']['recent_workspaces']
			projects = list(set(projects))
		for project_file in projects:
			project_file = re.sub(r'^/([^/])/', '\\1:/', project_file);
			project_json = json.loads(file(project_file, 'r').read(), strict=False)
			if 'folders' in project_json:
				folders = project_json['folders']
				found_all = True
				for directory in self.getDirectories():
					found = False
					for folder in folders:
						folder_path = re.sub(r'^/([^/])/', '\\1:/', folder['path']);
						if folder_path == directory.replace('\\', '/'):
							found = True
							break;
					if found == False:
						found_all = False
						break;
			if found_all:
				return project_file
		return None

	# Use SidebarEnhancement's getProjectFile and remove the last file
	def getProjectFolder(self):
		import string
		project_file = self.getProjectFile()

		paths = string.split(project_file, "/")
		del paths[-1]

		return "/".join( paths )

# Create a config file relative to the current file
class SublimeZillaConfigCommand(sublime_plugin.TextCommand):
	def run(self, edit, new_file):
		print new_file
		new_file.insert(edit, 0, 'Yay')

class SublimeZillaSFTPConfig(sublime_plugin.EventListener):
	def on_load(self, view):
		return
		# print "VIEW LOADED"