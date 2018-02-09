import sublime, sublime_plugin
import shutil
import base64
import os
import re
import binascii

from xml.dom import minidom


class SublimeZillaCommand(sublime_plugin.WindowCommand):

    def run(self):
        # check settings
        settings = sublime.load_settings("SublimeZilla.sublime-settings")

        # This is not very elegant but the get_xml() method will throw an error popup in SublimeText
        if not self.get_xml():
            return None

        if settings.get("filezilla_db_path", "") == "":
            self.window.show_input_panel('Browse to FileZilla directory', self.get_xml(), self.save_config, None, None)
        else:
            self.quick_panel()

    def quick_panel(self):
        server_names = self.get_server_names()
        self.window.show_quick_panel(server_names, self.server_chosen, sublime.MONOSPACE_FONT)

    # A server was chosen
    def server_chosen(self, server_index):
        if server_index == -1:
            return

        self.server = self.get_server(server_index)

        # Copy default SFTP config to current project root
        packages_path = sublime.packages_path()
        sftp_path = packages_path + "/SFTP/"
        sftp_path_default_config = sftp_path + "SFTP.default-config"

        if not os.path.exists(sftp_path):
            sublime.error_message("SFTP not installed. Exiting...")
            return None

        if not os.path.exists(sftp_path_default_config):
            sublime.error_message("SFTP default config not found. Exiting...")
            return None

        self.set_sftp_config()

    def set_sftp_config(self):

        import json

        server_config = {
            "host": self.server["host"],
            "user": self.server["user"],
            "password": self.server["password"],
            "port": self.server["port"],
            "remote_path": self.server["remote_path"]
        }

        # Open a new buffer and name it
        config_view = self.window.new_file()
        config_view.set_name("sftp-config.json")
        config_view.set_syntax_file("Packages/JavaScript/JSON.tmLanguage")

        # Check for SFTP config file
        SFTP_config = sublime.packages_path() + "/SFTP/SFTP.default-config"
        if os.path.exists(SFTP_config):

            # Grab the snippet text
            f = open(SFTP_config, 'r')
            config_json = f.read()
            f.close()

            # Replace snippet defaults with found variables
            snippet = self.intercept_sftp(server_config, config_json)

            # Insert the snippet. It can be tabbed through!
            config_view.run_command("insert_snippet", {'contents': snippet})

        else:
            config_json = json.dumps(server_config, sort_keys=False, indent=4, separators=(',', ': '))
            config_view.run_command("insert_snippet", {'contents': config_json})

    # A function that takes the raw snippet text from /SFTP/SFTP.default-config and replaces it with the FZ db
    # default_sftp is the object that contains the FileZilla db entries
    # sftp_snippet is the SFTP snippet contents
    def intercept_sftp(self, default_sftp, sftp_snippet):

        # print default_sftp["host"]
        variableTest = ""

        new_snippet = re.sub(r'(\$\{\d{1,2}\:)example.com(\})', r'\g<1>' + default_sftp["host"] + r'\g<2>',
                             sftp_snippet, re.M)
        new_snippet = re.sub(r'(\$\{\d{1,2}\:)username(\})', r'\g<1>' + default_sftp["user"] + r'\g<2>', new_snippet,
                             re.M)

        # Remove // before password key
        new_snippet = re.sub(r'(\$\{\d{1,2}\:)//(\})("password":)', r'\g<3>', new_snippet, re.M)
        new_snippet = re.sub(r'(\$\{\d{1,2}\:)password(\})', r'\g<1>' + default_sftp["password"] + r'\g<2>',
                             new_snippet, re.M)

        # @TODO: fix the port issue.. for some reason it inserts "Q}".. testing on http://gskinner.com/RegExr/ provides the results I expect.. strange
        # new_snippet = re.sub(r'(\$\{\d{1,2}\:)22(\})', 				r'\g<1>' + str(default_sftp["port"]) + r'\g<2>', 	new_snippet, re.M )
        new_snippet = re.sub(r'(\$\{\d{1,2}\:)/example/path/(\})', r'\g<1>' + default_sftp["remote_path"] + r'\g<2>',
                             new_snippet, re.M)

        return new_snippet

    def get_xml(self):

        user_home = os.curdir

        if 'HOME' in os.environ:
            user_home = os.environ['HOME']
        elif os.name == 'posix':
            user_home = os.path.expanduser("~")
        elif os.name == 'nt':
            if 'HOMEPATH' in os.environ and 'HOMEDRIVE' in os.environ:
                user_home = os.environ['HOMEDRIVE'] + os.environ['HOMEPATH']
        else:
            user_home = os.environ['HOMEPATH']

        # The default locations for FileZilla's XML database
        if os.name == 'nt':
            default_xml = user_home + os.sep + "AppData\\Roaming\\FileZilla\\sitemanager.xml"

            # Fix for Win XP
            if not os.path.exists(default_xml):
            	default_xml = user_home + os.sep + "Application Data\\FileZilla\\sitemanager.xml"

        elif os.name == 'posix':
            default_xml = user_home + os.sep + ".filezilla/sitemanager.xml"

        settings = sublime.load_settings("SublimeZilla.sublime-settings")
        path = settings.get("filezilla_db_path", default_xml)

        if not os.path.exists(path):
            path = settings.get("filezilla_db_path2", default_xml)

            if not os.path.exists(path):
                msg = "File sitemanager.xml not found. Is FileZilla installed? \n\n"
                msg += "If the sitemanager.xml file is located elsewhere please see https://github.com/ment4list/SublimeZilla#alternate-locations"
                sublime.error_message(msg)
                return None

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
        xmldoc = minidom.parse(self.get_xml())
        itemlist = xmldoc.getElementsByTagName('Server')
        server_array = []

        for server in itemlist:

            server_obj = {}

            Name = server.getElementsByTagName('Name')
            if Name[0].firstChild is not None:
                NameVal = Name[0].firstChild.nodeValue
                server_obj["name"] = str(NameVal)
            else:
                server_obj["name"] = ""

            Host = server.getElementsByTagName('Host')
            if Host[0].firstChild is not None:
                HostVal = Host[0].firstChild.nodeValue
                server_obj["host"] = str(HostVal)
            else:
                server_obj["host"] = ""

            Port = server.getElementsByTagName('Port')
            if Port[0].firstChild is not None:
                PortVal = Port[0].firstChild.nodeValue
                server_obj["port"] = str(PortVal)
            else:
                server_obj["port"] = ""

            User = server.getElementsByTagName('User')
            if User[0].firstChild is not None:
                UserVal = User[0].firstChild.nodeValue
                server_obj["user"] = str(UserVal)
            else:
                server_obj["user"] = ""

            Pass = server.getElementsByTagName('Pass')
            if len(Pass) > 0 and Pass[0].firstChild is not None:
                PassVal = Pass[0].firstChild.nodeValue

                # Try base64 decode...
                PassVal = str(PassVal)
                PassValTmp = ""

                try:
                    PassValTmp = base64.b64decode(PassVal).decode('utf-8')
                    PassValTmp = str(PassValTmp)
                except TypeError:
                    # Is probably not encoded, use what we had
                    PassValTmp = PassVal
                except binascii.Error:
                    # Is probably not encoded, use what we had
                    PassValTmp = PassVal

                server_obj["password"] = PassValTmp

            else:
                server_obj["password"] = ""

            LocalDir = server.getElementsByTagName('LocalDir')
            if LocalDir[0].firstChild is not None:
                LocalDirVal = LocalDir[0].firstChild.nodeValue
                server_obj["local_path"] = str(LocalDirVal)
            else:
                server_obj["local_path"] = ""

            RemoteDir = server.getElementsByTagName('RemoteDir')
            if RemoteDir[0].firstChild is not None:
                RemoteDirVal = RemoteDir[0].firstChild.nodeValue
                server_obj["remote_path"] = self.convertRemoteDir(str(RemoteDirVal))
            else:
                server_obj["remote_path"] = ""

            # Add this server to the array
            server_array.append(server_obj)

        return server_array

    # Converts FileZilla's weird export method for remote directories to actual directories
    def convertRemoteDir(self, filezilla_dir):

        # @Note botg's comment here: http://forum.filezilla-project.org/viewtopic.php?f=1&t=15923 might shed some light on why FileZilla exports the directories this way

        regex = "^((\d{1,2}\s){3})(.+)?$"
        modifiers = "gm"

        re_compile = re.compile(regex, re.M)
        results = re.split(regex, filezilla_dir)

        try:
            fz_remote_dir = results[3]
            # Replace all instances of \s\d{1,2}\s within capture group 3 with a "/" because it is seen as a directory by FileZilla
            slash_regex = "\s\d{1,2}\s"

            with_slashes = re.split(slash_regex, fz_remote_dir)

            return "/" + "/".join(with_slashes) + "/"

        except IndexError:
            return '/'

    def get_server(self, server_index):
        return self.servers[server_index]

    # getDirectories taken from Packages\SideBarEnhancements\sidebar\SideBarProject.py
    def getDirectories(self):
        return sublime.active_window().folders()
