#!/usr/bin/python
import sys, getopt, os, subprocess, re, time, datetime


##############################
# Configurations
##############################
# Servers' info
SERVERS = {
    # Local server
    "local" : {
        "IP" : "localhost",             # The IP address of the server.
        "DOMAIN" : "localhost",         # Server's domain name.
        "KEYPAIR" : "",                 # The keypair file used to connect to the server.
        "DEFAULT_USER" : "vagrant",     # The default user and user group of the server.
        "HTTP_PORT" : 80,               # The HTTP port on the server.
        "HTTPS_PORT" : 443,             # The HTTPS port on the server.
        "HTTP_FORWARDED_PORT" : 8080,   # The HTTP forwarded port
        "HTTPS_FORWARDED_PORT" : 4443,  # The HTTPS forwarded port
        "BRANCH" : "master",            # Vagrant server doesn't require git
    },

    "dev" : {
        "IP" : "54.94.211.154",         # The IP address of the server.
        "DOMAIN" : "vron.intertech.com.br", # Server's domain name.
        "KEYPAIR" : "vronaws.pem",      # The keypair file used to connect to the server.
        "DEFAULT_USER" : "ubuntu",      # The default user and user group of the server.
        "HTTP_PORT" : 80,               # The HTTP port on the server.
        "HTTPS_PORT" : 443,             # The HTTPS port on the server.
        "HTTP_FORWARDED_PORT" : 80,     # The HTTP forwarded port
        "HTTPS_FORWARDED_PORT" : 443,   # The HTTPS forwarded port
        "BRANCH" : "master",            # Vagrant server doesn't require git
    },

    "prod" : {
        "IP" : "ip-here",               # The IP address of the server.
        "DOMAIN" : "vron.com.au",       # Server's domain name.
        "KEYPAIR" : "key-here.pem",     # The keypair file used to connect to the server.
        "DEFAULT_USER" : "ubuntu",      # The default user and user group of the server.
        "HTTP_PORT" : 80,               # The HTTP port on the server.
        "HTTPS_PORT" : 443,             # The HTTPS port on the server.
        "HTTP_FORWARDED_PORT" : 80,     # The HTTP forwarded port
        "HTTPS_FORWARDED_PORT" : 443,   # The HTTPS forwarded port
        "BRANCH" : "master",            # Vagrant server doesn't require git
    },

    "wiki" : {
        "IP" : "ip-here",               # The IP address of the server.
        "DOMAIN" : "vron.com.au",       # Server's domain name.
        "KEYPAIR" : "key-here.pem",     # The keypair file used to connect to the server.
        "DEFAULT_USER" : "ubuntu",      # The default user and user group of the server.
        "HTTP_PORT" : 80,               # The HTTP port on the server.
        "HTTPS_PORT" : 443,             # The HTTPS port on the server.
        "HTTP_FORWARDED_PORT" : 80,     # The HTTP forwarded port
        "HTTPS_FORWARDED_PORT" : 443,   # The HTTPS forwarded port
        "BRANCH" : "",                  # Vagrant/Wiki server doesn't require git
    },
}

# Global settings
GIT_REPO = "https://github.com/humbertomn/vron.git"     # Git repository
DEPLOYMENT_ROOT = ""                                    # Root folder for deploying web projects (Leave empty for a single project)
VIRTUALENV_ROOT = ""                                    # Root folder for virtualenvs  (Leave empty for a single project)
PROJECT_ALIAS = "vron"                                  # Current project alias
APP_NAME = "vron"                                       # Current project main application

# Packages to be installed for django applications
DJANGO_PACKAGES = [
    "python3-dev", "git", "apache2", "libapache2-mod-wsgi-py3",
    "libmysqlclient-dev", "mysql-client", "gettext", "libjpeg-dev", "rabbitmq-server",
    "supervisor", "python3-lxml",
]

# Packages to be installed for wiki application
WIKI_PACKAGES = [
    "apache2", "libapache2-mod-php5", "php5-mysql",
    "libmysqlclient-dev", "mysql-client"
]

# Virtualenv packages
VIRTUALENV_PACKAGES = [
    "django==1.7.5",
    "https://dev.mysql.com/get/Downloads/Connector-Python/mysql-connector-python-1.2.3.tar.gz",
    "python-social-auth==0.2.9",
    "pillow==2.8.1",
    "django-stdimage==1.2.2",
    "pytz==2015.4",
    "defusedxml==0.4.1",
    "progressbar==2.2",
    "python3-openid==3.0.5",
    "requests==2.7.0",
    "sqlparse==0.1.14",
    "celery==3.1.18",
    "django-celery==3.1.16"
]








#############################################
# PRE-CALCULATED CONFIGURATIONS (NOT RECOMMENDED TO MODIFY)
#############################################

# Pre-calculate the available servers regex pattern
AVAILABLE_SERVERS_PATTERN = '(' + '|'.join( sorted( SERVERS.keys() ) ) + ')'

# Project root and virtualenv
PROJECT_ROOT = DEPLOYMENT_ROOT + '/' + PROJECT_ALIAS
PROJECT_VIRTUALENV = VIRTUALENV_ROOT + '/' + PROJECT_ALIAS + "venv"
DATABASE_BACKUP_FOLDER = '/database_backup'

# Aliases for django, wiki and wsgi
DJANGO_ALIAS = "django"
WIKI_ALIAS = "wiki"
WSGI_ALIAS = "wsgi"

# Apache's default user
APACHE_DEFAULT_USER = "www-data"

# User group for the project
DEFAULT_USER_GROUP = PROJECT_ALIAS + "-dev"

# Root path for django and wiki
DJANGO_ROOT = PROJECT_ROOT + '/' + DJANGO_ALIAS
WIKI_ROOT = PROJECT_ROOT + '/' + WIKI_ALIAS

# Apache configurations folder
APACHE_SITES_ENABLED_PATH = "/etc/apache2/sites-enabled"    # Sites enabled folder on Apache
APACHE_MODS_ENABLED_PATH = "/etc/apache2/mods-enabled"      # Mods enabled folder on Apache
APACHE_MODS_AVAILABLE_PATH = "/etc/apache2/mods-available"      # Mods available folder on Apache

# Spacing for help messages.
N_DEFAULT_HELP_SPACING = 15



WSGI_CONF = """
<IfModule mod_wsgi.c>
    WSGIPythonPath {django_root}:/{virtualenv}/lib/python3.4:/{virtualenv}/lib/python3.4/site-packages
</IfModule>
""".format( django_root = DJANGO_ROOT, virtualenv = PROJECT_VIRTUALENV )

# Requires formatting on the fly. Params:
# http_port, wiki_alias, domain, wiki_root.
WIKI_CONF = """
    <VirtualHost *:{http_port}>
        ServerName {wiki_alias}.{domain}
        DocumentRoot {wiki_root}
        <Directory {wiki_root}>
            Require all granted
        </Directory>
    </VirtualHost>
"""

# Requires formatting on the fly. Params:
# http_port, https_port, www_domain, pt_domain, django_root, app_name, https_forwarded_port
DJANGO_CONF = """
    <VirtualHost *:{http_port}>
        ServerName {www_domain}
        DocumentRoot {django_root}

        SSLEngine on
        SSLProtocol All -SSLv2 -SSLv3
        SSLCertificateFile /etc/apache2/ssl/vron.crt
        SSLCertificateKeyFile /etc/apache2/ssl/vron.key
        SSLCertificateChainFile /etc/apache2/ssl/vron.ca

        WSGIScriptAlias / {django_root}/{app_name}/wsgi.py

        Alias /favicon.ico {django_root}/static/favicon.ico
        Alias /static/ {django_root}/static/
        Alias /upload/ {django_root}/upload/

        <Directory {django_root}/{app_name}/>
                <Files wsgi.py>
                    Require all granted
                </Files>
        </Directory>

        <Directory {django_root}/static/>
            Require all granted
        </Directory>

        <Directory {django_root}/upload/>
            Require all granted
        </Directory>

    </VirtualHost>
"""


CELERY_CONF = """
    ; ==================================
    ;  celery worker supervisor example
    ; ==================================

    [program:celery]
    ; Set full path to celery program if using virtualenv
    command=/vronvenv/bin/celery worker -A vron -B --loglevel=INFO

    user=nobody
    directory=/vron/django
    numprocs=1
    stdout_logfile=/var/log/celery/worker.log
    stderr_logfile=/var/log/celery/worker.log
    autostart=true
    autorestart=true
    startsecs=10

    ; Need to wait for currently executing tasks to finish at shutdown.
    ; Increase this if you have very long running tasks.
    stopwaitsecs = 600

    ; When resorting to send SIGKILL to the program to terminate it
    ; send SIGKILL to its whole process group instead,
    ; taking care of its children as well.
    killasgroup=true

    ; if rabbitmq is supervised, set its priority higher
    ; so it starts first
    priority=998
"""


########################################################################
# PUBLIC METHODS
# If you want to add a new method, please follow the pattern existant
# in other methods (Regex to check usage at beginning, method help if
# usage wont match, etc).
########################################################################
def config( args ):
    """
        Usage: python helper.py config <feature> on <server> (with database)
        Installs the desired app on the remote.
        :args: A string indicating the server to run the update.
    """

    # The usage regex.
    usage_pattern = "^(site|wiki) on {0}( with database)?$".format( AVAILABLE_SERVERS_PATTERN )
    cmd_str = " ".join( args )

    # Checks if the user typed the command correctly
    if not re.match( usage_pattern, cmd_str ):
        print
        print( "usage: python {0} {1} {2}".format( __file__, config.__name__, usage_pattern ) )
        print
        print( "Params explanation:")
        print( "    {0}{1}".format( "(site|wiki)".ljust( N_DEFAULT_HELP_SPACING ), "The application to install." ) )
        print( "    {0}{1}".format( "(local|dev|prod)".ljust( N_DEFAULT_HELP_SPACING ), "The server to configure." ) )
        print( "    {0}{1}".format( "[with database]".ljust( N_DEFAULT_HELP_SPACING ), "(Optional) Indicates to install a local database on the server." ) )
    else:

        # The commands to be executed in the server
        remote_commands = []

        # The command to generate the conf file for the specified app (site or wiki).
        conf_file_generator_cmd = ""

        # Extracts params from command line
        app = args[0] # App
        server = args[2] # Server

        # The number of the ports to display on the .conf files
        http_workaround_port = ""
        https_workaround_port = ""
        wiki_workaround_port = ""

        # Connecting to the server
        if server == "local":
            commands = [ "vagrant ssh" ]
        else:
            commands = [ "ssh", "-i", SERVERS[ server ][ "KEYPAIR" ], "{0}@{1}".format( SERVERS[ server ][ "DEFAULT_USER" ], SERVERS[ server ][ "IP" ] ) ]

        # Creates the user group and adds server's and apache's user to it.
        remote_commands.append( "echo \" \"" )
        remote_commands.append( "echo \"##############################\"" )
        remote_commands.append( "echo \"# CONFIG. GROUP PERMISSIONS  #\"" )
        remote_commands.append( "echo \"##############################\"" )
        remote_commands.append( "echo \" \"" )
        remote_commands.extend( [
            "sudo groupadd {0}".format( DEFAULT_USER_GROUP ),
            "sudo usermod -a -G {0} {1}".format( DEFAULT_USER_GROUP, SERVERS[ server ][ "DEFAULT_USER"] ),
            "sudo usermod -a -G {0} {1}".format( DEFAULT_USER_GROUP, APACHE_DEFAULT_USER ),
        ] )
        remote_commands.append( "echo \"   ...DONE!\"" )

        # Updates apt-get
        remote_commands.append( "echo \" \"" )
        remote_commands.append( "echo \"#########################\"" )
        remote_commands.append( "echo \"# UPDATING APT-GET      #\"" )
        remote_commands.append( "echo \"#########################\"" )
        remote_commands.append( "echo \" \"" )
        remote_commands.append( "sudo apt-get update" )
        remote_commands.append( "echo \"   ...DONE!\"" )

        # Install packages
        remote_commands.append( "echo \" \"" )
        remote_commands.append( "echo \"##################################\"" )
        remote_commands.append( "echo \"# INSTALLING REQUIRED PACKAGES   #\"" )
        remote_commands.append( "echo \"##################################\"" )
        remote_commands.append( "echo \" \"" )

        INSTALL_PACKAGES = DJANGO_PACKAGES if app == "site" else WIKI_PACKAGES
        for package in INSTALL_PACKAGES:
            remote_commands.append( "sudo apt-get install {0} --yes".format( package ) )
        remote_commands.append( "echo \"   ...DONE!\"" )


        # Checks for the WITH param to know if
        # there is more features to install, like database.
        if "with" in args:

            # LOCAL DATABASE required?
            if "database" in args:
                # Asks for root password
                root_password = input( "Please type the root's password for MySQL: " )
                root_password_confirm = input( "Please confirm the root's password for MySQL: " )

                # If they are different, return.
                if root_password != root_password_confirm:
                    print( "Error: Passwords do not match." )
                    return

                # Add commands to install the mysql-server
                remote_commands.append( "echo \" \"" )
                remote_commands.append( "echo \"############################\"" )
                remote_commands.append( "echo \"# INSTALLING MYSQL-SERVER  #\"" )
                remote_commands.append( "echo \"############################\"" )
                remote_commands.append( "echo \" \"" )
                remote_commands.extend( [
                    "echo mysql-server mysql-server/root_password password {0} | sudo debconf-set-selections".format( root_password ),
                    "echo mysql-server mysql-server/root_password_again password {0} | sudo debconf-set-selections".format( root_password ),
                    "sudo apt-get -y install mysql-server",
                ] )
                remote_commands.append( "echo \"   ...DONE!\"" )


        # Creating the project's root folder
        remote_commands.append( "echo \" \"" )
        remote_commands.append( "echo \"########################\"" )
        remote_commands.append( "echo \"# CREATING ROOT FOLDER #\"" )
        remote_commands.append( "echo \"########################\"" )
        remote_commands.append( "echo \" \"" )
        remote_commands.extend([
            "sudo mkdir -p {0}".format( PROJECT_ROOT ),
            "sudo chown {0}:{1} {2}".format( SERVERS[ server ][ "DEFAULT_USER" ], DEFAULT_USER_GROUP, PROJECT_ROOT ),
            "sudo chgrp -R {0} {1}".format( DEFAULT_USER_GROUP, PROJECT_ROOT ),
        ])
        remote_commands.append( "echo \"   ...DONE!\"" )


        ######################################
        # Configuring Wiki on remote.
        ######################################
        if "wiki" in args:
            remote_commands.append( "echo \" \"" )
            remote_commands.append( "echo \"#########################\"" )
            remote_commands.append( "echo \"# DOWNLOADING MEDIAWIKI #\"" )
            remote_commands.append( "echo \"#########################\"" )
            remote_commands.append( "echo \" \"" )
            remote_commands.extend([
                "cd {0}".format( PROJECT_ROOT ),
                "wget http://releases.wikimedia.org/mediawiki/1.23/mediawiki-1.23.2.tar.gz",
                "tar -zxf mediawiki-1.23.2.tar.gz",
                "rm mediawiki-1.23.2.tar.gz",
                "mv mediawiki-1.23.2 {0}".format( WIKI_ROOT ),
                "sudo chown -R {0}:{1} {2}".format( SERVERS[ server ][ "DEFAULT_USER" ], DEFAULT_USER_GROUP, WIKI_ROOT ),
                "sudo chgrp -R {0} {1}".format( DEFAULT_USER_GROUP, WIKI_ROOT ),
            ])
            remote_commands.append( "echo \"   ...DONE!\"" )

            # Formats the conf file for the given server
            wiki_conf = WIKI_CONF.format(
                http_port = SERVERS[ server ][ "HTTP_PORT" ],
                wiki_alias = WIKI_ALIAS,
                domain = SERVERS[ server ][ "DOMAIN" ],
                wiki_root = WIKI_ROOT
            )

            remote_commands.append( "echo \" \"" )
            remote_commands.append( "echo \"#############################\"" )
            remote_commands.append( "echo \"# GENERATING WIKI.CONF FILE #\"" )
            remote_commands.append( "echo \"#############################\"" )
            remote_commands.append( "echo \" \"" )
            # Creates the conf file containing the virtualhosts for the wiki on apache sites-enabled folder.
            remote_commands.extend([
                "sudo touch {0}/{1}.conf".format( APACHE_SITES_ENABLED_PATH, WIKI_ALIAS ),
                "sudo chmod 777 {0}/{1}.conf".format( APACHE_SITES_ENABLED_PATH, WIKI_ALIAS ),
                "echo \"{0}\" > {1}/{2}.conf".format( wiki_conf, APACHE_SITES_ENABLED_PATH, WIKI_ALIAS ),
                "sudo chmod 644 {0}/{1}.conf".format( APACHE_SITES_ENABLED_PATH, WIKI_ALIAS ),
            ])
            remote_commands.append( "echo \"   ...DONE!\"" )


        ################################
        # Configuring Django on remote.
        ################################
        elif "site" in args:
            remote_commands.append( "echo \" \"" )
            remote_commands.append( "echo \"#################################\"" )
            remote_commands.append( "echo \"# CREATING DIRECTORY STRUCTURE  #\"" )
            remote_commands.append( "echo \"#################################\"" )
            remote_commands.append( "echo \" \"" )
            # Creating folder structure
            remote_commands.extend([
                "sudo mkdir -p {0}".format( PROJECT_VIRTUALENV ),
                "sudo chown {0}:{1} {2}".format( SERVERS[ server ][ "DEFAULT_USER" ], DEFAULT_USER_GROUP, PROJECT_VIRTUALENV ),
                "sudo chgrp -R {0} {1}".format( DEFAULT_USER_GROUP, PROJECT_VIRTUALENV ),
            ])
            remote_commands.append( "echo \"   ...DONE!\"" )


            remote_commands.append( "echo \" \"" )
            remote_commands.append( "echo \"##################################\"" )
            remote_commands.append( "echo \"# INSTALLING PIP AND VIRTUALENV  #\"" )
            remote_commands.append( "echo \"##################################\"" )
            remote_commands.append( "echo \" \"" )
            # Installing pip using python3 and virtualenv
            remote_commands.extend([
                "cd {0}".format( PROJECT_VIRTUALENV ),
                "wget https://bootstrap.pypa.io/get-pip.py",
                "sudo python3 get-pip.py",
                "sudo pip install virtualenv",
                "sudo rm get-pip.py",
            ])
            remote_commands.append( "echo \"   ...DONE!\"" )

            # Downloading git code.
            if server != "local":
                remote_commands.append( "echo \" \"" )
                remote_commands.append( "echo \"#########################\"" )
                remote_commands.append( "echo \"# DOWNLOADING CODE      #\"" )
                remote_commands.append( "echo \"#########################\"" )
                remote_commands.append( "echo \" \"" )
                remote_commands.extend([
                    "cd {0}".format( PROJECT_ROOT ),
                    "git clone {0} temp".format( GIT_REPO ),
                    "shopt -s dotglob",
                    "mv temp/* {0}".format( PROJECT_ROOT ),
                    "git checkout {0}".format( SERVERS[ server ][ "BRANCH" ] ),
                    "rm -R temp",
                    "rm -R infra",
                ])
                remote_commands.append( "echo \"   ...DONE!\"" )

            remote_commands.append( "echo \" \"" )
            remote_commands.append( "echo \"###########################\"" )
            remote_commands.append( "echo \"# CONFIGURING VIRTUALENV  #\"" )
            remote_commands.append( "echo \"###########################\"" )
            remote_commands.append( "echo \" \"" )
            # Installing and configuring virtualenv
            remote_commands.extend([
                "virtualenv {0}".format( PROJECT_VIRTUALENV ),
                "source {0}/bin/activate".format( PROJECT_VIRTUALENV ),
                "sudo chmod 777 {0}".format( PROJECT_VIRTUALENV ),
            ])
            for package in VIRTUALENV_PACKAGES:
                remote_commands.append( "pip install {0}".format( package ) )
            remote_commands.extend([
                "deactivate",
                "sudo chmod 755 {0}".format( PROJECT_VIRTUALENV ),
            ])
            remote_commands.append( "echo \"   ...DONE!\"" )

            remote_commands.append( "echo \" \"" )
            remote_commands.append( "echo \"#########################\"" )
            remote_commands.append( "echo \"# GENERATING CONF FILES #\"" )
            remote_commands.append( "echo \"#########################\"" )
            remote_commands.append( "echo \" \"" )

            # Generates wsgi.conf
            remote_commands.extend([
                "sudo touch {0}/{1}.conf".format( APACHE_MODS_ENABLED_PATH, WSGI_ALIAS ),
                "sudo chmod 777 {0}/{1}.conf".format( APACHE_MODS_ENABLED_PATH, WSGI_ALIAS ),
                "echo \"{0}\" > {1}/{2}.conf".format( WSGI_CONF, APACHE_MODS_ENABLED_PATH, WSGI_ALIAS ),
                "sudo chmod 644 {0}/{1}.conf".format( APACHE_MODS_ENABLED_PATH, WSGI_ALIAS ),
            ])

            # Formats the conf file for the given server
            django_conf = DJANGO_CONF.format(
                http_port = SERVERS[ server ][ "HTTP_PORT" ],
                https_port = SERVERS[ server ][ "HTTPS_PORT" ],
                https_forwarded_port = SERVERS[ server ][ "HTTPS_FORWARDED_PORT" ],
                www_domain = "www.{0}".format( SERVERS[ server ][ "DOMAIN" ] ) if server == "prod" else SERVERS[ server ][ "DOMAIN" ],
                pt_domain = "pt.{0}".format( SERVERS[ server ][ "DOMAIN" ] ) if server == "prod" else SERVERS[ server ][ "DOMAIN" ],
                django_root = DJANGO_ROOT,
                app_name = APP_NAME,
            )

            # Generates django.conf
            remote_commands.extend([
                "sudo touch {0}/{1}.conf".format( APACHE_SITES_ENABLED_PATH, DJANGO_ALIAS ),
                "sudo chmod 777 {0}/{1}.conf".format( APACHE_SITES_ENABLED_PATH, DJANGO_ALIAS ),
                "echo \"{0}\" > {1}/{2}.conf".format( django_conf, APACHE_SITES_ENABLED_PATH, DJANGO_ALIAS ),
                "sudo chmod 644 {0}/{1}.conf".format( APACHE_SITES_ENABLED_PATH, DJANGO_ALIAS ),
            ])

            # Generates celery.conf
            remote_commands.extend([
                "sudo mkdir /var/log/celery",
                "sudo touch /var/log/celery/worker.log",
                "sudo touch /etc/supervisor/conf.d/celery.conf",
                "sudo chmod 777 /etc/supervisor/conf.d/celery.conf",
                "echo \"{0}\" > /etc/supervisor/conf.d/celery.conf".format( CELERY_CONF ),
                "sudo chmod 644 /etc/supervisor/conf.d/celery.conf",
                "sudo service supervisor restart"
            ])
            remote_commands.append( "echo \"   ...DONE!\"" )


            remote_commands.append( "echo \" \"" )
            remote_commands.append( "echo \"#################################\"" )
            remote_commands.append( "echo \"# ENABLING SSL and WSGI_EXPRESS #\"" )
            remote_commands.append( "echo \"#################################\"" )
            remote_commands.append( "echo \" \"" )
            # Enabling SSL on apache
            remote_commands.append( "sudo a2enmod ssl" )


        # Enabling mode rewrite on apache
        remote_commands.append( "echo \"Enabling mode rewrite\"" )
        remote_commands.append( "sudo a2enmod rewrite" )

        # Clears apache's default conf.
        remote_commands.append( "echo \"Removing apache's default conf file\"" )
        remote_commands.append( "sudo rm {0}/000-default.conf".format( APACHE_SITES_ENABLED_PATH ) )

        # Reinforce the owner and group of all project's folders
        remote_commands.append( "echo \"Reinforcing owner and group over all project's folders\"" )
        remote_commands.extend([
            "sudo chown -R {0}:{1} {2}".format( SERVERS[ server ][ "DEFAULT_USER" ], DEFAULT_USER_GROUP, PROJECT_ROOT ),
            "sudo chgrp -R {0} {1}".format( DEFAULT_USER_GROUP, PROJECT_ROOT ),
        ])

        # Restarting apache
        remote_commands.append( "sudo service apache2 restart" )

        call_by_cloning_script( server, remote_commands )

        # Print ending hints
        print()
        print()
        print( "###############################################")
        print( "# Installation DONE. But you should configure #")
        print( "# some DATABASE settings manually. Please     #")
        print( "# refer our Wiki to get extra help.           #")
        print( "###############################################")
        print()
        print( "1. Connect to the server." )
        print( "     python helper.py connect <server>" )
        print( "2. Access mysql as root (you will be prompted to insert your root's password)." )
        print( "     mysql -u root -p" )
        print( "3. Create the database." )
        print( "     create database <database>;" )
        print( "4. Create the user for this database." )
        print( "     create user <username>@localhost identified by <password>;" )
        print( "5. Grant all privilegies to the user on the database. " )
        print( "     grant all on <database>.* to <username>@localhost;" )
        if app == "site":
            print( "6. Exit MySQL and SSH and run \"update\" to populate the database." )
            print( "     python helper.py update <server>" )
        elif app == "wiki":
            print( "6. Access http://{0}:{1}/mw-config/index.php to configure the wiki.".format( SERVERS[ server ][ "IP" ], SERVERS[ server ][ "HTTP_PORT" ] ) )



def connect( args ):
    """
        Connects to the specified server via ssh.
        :args: A string indicating the server to connect to.
    """

    # The usage regex.
    usage_pattern = "{0}".format( AVAILABLE_SERVERS_PATTERN )
    cmd_str = " ".join( args )

    # Checks if the user typed the command correctly
    if not re.match( usage_pattern, cmd_str ):
        print
        print( "usage: python {0} {1} {2}".format( __file__, connect.__name__, usage_pattern ) )
        print
        print( "Params explanation:")
        print( "    {0}{1}".format( "local".ljust( N_DEFAULT_HELP_SPACING ), "Connects to your local vagrant instance." ) )
        print( "    {0}{1}".format( "dev".ljust( N_DEFAULT_HELP_SPACING ), "Connects to your development instance." ) )
        print( "    {0}{1}".format( "prod".ljust( N_DEFAULT_HELP_SPACING ), "Connects to production instance." ) )
    else:
        # Gets the server name
        server = args[0]

        # Connects to the server.
        if server == "local":
            return cmd( "vagrant ssh" )
        else:
            return cmd( "ssh -i {0} {1}@{2}".format( SERVERS[ server ][ "KEYPAIR" ], SERVERS[ server ][ "DEFAULT_USER" ], SERVERS[ server ][ "IP" ] ) )


def restart( args ):
    """
        Restarts the required services running on the server.
        :args: A string indicating the server to restart.
    """

    # The usage regex.
    usage_pattern = "{0}".format( AVAILABLE_SERVERS_PATTERN )
    cmd_str = " ".join( args )

    # Checks if the user typed the command correctly
    if not re.match( usage_pattern, cmd_str ):
        print
        print( "usage: python {0} {1} {2}".format( __file__, restart.__name__, usage_pattern ) )
        print
        print( "Params explanation:")
        print( "    {0}{1}".format( "local".ljust( N_DEFAULT_HELP_SPACING ), "Restarts the services on the local instance (vagrant)." ) )
        print( "    {0}{1}".format( "dev".ljust( N_DEFAULT_HELP_SPACING ), "Restarts the services on the development instance." ) )
        print( "    {0}{1}".format( "prod".ljust( N_DEFAULT_HELP_SPACING ), "Restarts the services on the production instance." ) )
    else:
        # Gets the server name
        server = args[0]
        services = [ "mysql", "supervisor", "apache2" ]

        cmd_str = ""
        for service in services:
            cmd_str += "sudo service {0} restart; ".format( service )

        if server == "local":
            cmd( "vagrant ssh -c '{0}'".format( cmd_str ) )
        else:
            # Generates the ssh command for the given server
            ssh_command = "ssh -i {0} {1}@{2} -t".format(
                SERVERS[ server ][ "KEYPAIR" ],
                SERVERS[ server ][ "DEFAULT_USER" ],
                SERVERS[ server ][ "IP" ]
            )
            cmd( "{0} '{1}'".format( ssh_command, cmd_str ) )


def update( args ):
    """
        Updates the code of the instance with git HEAD modifications.
        :args: A string indicating the server to run the update.
    """
    # The usage regex.
    usage_pattern = "{0}".format( AVAILABLE_SERVERS_PATTERN )
    cmd_str = " ".join( args )

    # Checks if the user typed the command correctly
    if not re.match( usage_pattern, cmd_str ):
        print
        print( "usage: python {0} {1} {2}".format( __file__, update.__name__, usage_pattern ) )
        print
        print( "Params explanation:")
        print( "    {0}{1}".format( "local".ljust( N_DEFAULT_HELP_SPACING ), "Updates your local instance." ) )
        print( "    {0}{1}".format( "dev".ljust( N_DEFAULT_HELP_SPACING ), "Updates your development instance." ) )
        print( "    {0}{1}".format( "prod".ljust( N_DEFAULT_HELP_SPACING ), "Updates your production instance." ) )
    else:
        # Configuring the params and the commands to call.
        server = args[0]

        remote_commands = []
        # Connects to the server.
        if server == "local":
            remote_commands = [
                "source {0}/bin/activate".format( PROJECT_VIRTUALENV ),
                "python {0}/manage.py migrate".format( DJANGO_ROOT ),
                "deactivate",
                "sudo service apache2 restart",
            ]

        else:
            # Configuring the remote commands.
            remote_commands = [
                "cd {0}".format( PROJECT_ROOT ),
                "git checkout {0}".format( SERVERS[ server ][ "BRANCH" ] ),
                "git pull origin {0}".format( SERVERS[ server ][ "BRANCH" ] ),
                "rm -R infra",
                "source {0}/bin/activate".format( PROJECT_VIRTUALENV ),
                "python {0}/manage.py migrate".format( DJANGO_ROOT ),
                "deactivate",
                "sudo service apache2 restart",
            ]

        return call_by_cloning_script( server, remote_commands )


###########################################################
# Utility function to extract the filename from a string.
###########################################################
def path_leaf( path ):
    import ntpath
    head, tail = ntpath.split( path )
    return tail or ntpath.basename( head )
###########################################################


def copy( args ):
    """
    Copy a file or a folder from/to the remote server.
    :args: A set of arguments including the server to run the command, the file and
    recursive option.
    """
    # The usage regex.
    usage_pattern = "[^ ]+( -[rR])? (from|to) {0} (to|into) [^ ]+".format( AVAILABLE_SERVERS_PATTERN )
    cmd_str = " ".join( args )

    # Check if the minimal number of arguments was passed.
    if not re.match( usage_pattern, cmd_str ):
        print
        print( "usage: python {0} {1} <file> [-r] from <server> to <local_path>".format( __file__, copy.__name__ ) )
        print( "usage: python {0} {1} <file> [-r] to <server> into <remote_path>".format( __file__, copy.__name__ ) )
        print
        print( "Params explanation:")
        print( "    {0}{1}".format( "file".ljust( N_DEFAULT_HELP_SPACING ), "The file or folder to be copied." ) )
        print( "    {0}{1}".format( "-r".ljust( N_DEFAULT_HELP_SPACING ), "(Optional) param indicating to download the <file> path recursively." ) )
        print( "    {0}{1}".format( "dev".ljust( N_DEFAULT_HELP_SPACING ), "Copy files from/to the development server." ) )
        print( "    {0}{1}".format( "prod".ljust( N_DEFAULT_HELP_SPACING ), "Copy files from/to the production server." ) )
        print( "    {0}{1}".format( "local_path".ljust( N_DEFAULT_HELP_SPACING ), "The directory on your local machine to put the file." ) )
        print( "    {0}{1}".format( "remote_path".ljust( N_DEFAULT_HELP_SPACING ), "The directory on your remote to put the file." ) )
    else:
        # Extracts the recursive param
        recursive = ( "-r" in args or "-R" in args )
        if recursive:
            del args[1]

        # Extracts the other params (Note: The recursive arg was removed if it was passed).
        src = args[0]
        from_to = args[1]
        server = args[2]
        dest = args[4]

        ################################
        # Copying from server to local.
        ################################
        if from_to == "from":
            # The scp command with params set.
            commands = [ "scp", "-r", "-i", SERVERS[ server ][ "KEYPAIR" ], "{0}@{1}:{2}".format( SERVERS[ server ][ "DEFAULT_USER" ], SERVERS[ server ][ "IP" ], src ), dest ]
            if not recursive:
                commands.remove( "-r" )

            return cmd( commands )

        ################################
        # Copying from local to server.
        ################################
        else:
            if recursive:   # Recursive? (src and dest are folders)
                commands = [ "scp", "-r", "-i", SERVERS[ server ][ "KEYPAIR" ], src, "{0}@{1}:{2}".format( SERVERS[ server ][ "DEFAULT_USER" ], SERVERS[ server ][ "IP" ], dest ) ]
            else:
                # Extracts the filename from source
                filename = path_leaf( src )
                if not dest.endswith( os.pathsep ):
                    filename = '/' + filename

                commands = [ "scp", "-i", SERVERS[ server ][ "KEYPAIR" ], src,  "{0}@{1}:{2}{3}".format( SERVERS[ server ][ "DEFAULT_USER" ], SERVERS[ server ][ "IP" ], dest, filename ) ]
            return cmd( commands )










########################################################################
# INTERNAL METHODS
# Please do not modify the code above if you don't know what you're doing.
# This script was made to you just modify the configurations bellow.
########################################################################
def init():
    """
        Parse the command line params and calls the desired method.
        If the method is not encountered displays the help.
    """
    if len( sys.argv ) > 1:
        # Tries to get the method to be called.
        method = globals().get( sys.argv[1] )
        # Gets the params
        params = sys.argv[2:]

        # If method exists
        if method:
            method( params )
        # Else Displays help
        else:
            h()
    # Displays help
    else:
        h()



def h():
    """
        Displays info about the helper's methods.
    """

    # A big list of dictionaries mapping available methods names
    # and its respectives descriptions
    METHODS_HELP = [
        {
            "name": config.__name__,
            "description": "Configures a site or wiki on the remote server."
        },

        {
            "name": connect.__name__,
            "description": "Connects via ssh to the remote server."
        },
        {
            "name": update.__name__,
            "description": "Updates the remote server."
        },
        {
            "name": copy.__name__,
            "description": "Copy files from/to remote server."
        },
        {
            "name": restart.__name__,
            "description": "Restarts the services running on the server."
        },
    ]
    print
    print( "USAGE: python {0} <command> <params>".format( __file__ ) )
    print
    print( "Available commands:" )

    for help in METHODS_HELP:
        print( "    {0}{1}".format( help[ "name" ].ljust( N_DEFAULT_HELP_SPACING ), help[ "description" ] ) )



def cmd( commands ):
    """
        Internal function. Used to call command line methods and pass input to it.
    """

    # Converts commands to string
    if type( commands ) is list:
        commands = " ".join( commands )

    # Calls the command
    shell = subprocess.call( commands, shell = True )



def call_by_cloning_script( server, commands ):

    # Generates the script file.
    script_filename = "cs-{0}.sh".format( time.time() )
    with open( script_filename, "wb" ) as script:
        script.write( bytes( "\n".join( commands ).replace( "\r", '' ), "UTF-8" ) )


    # Sending and executing the script
    if server == "local":
        cmd( "vagrant ssh -c 'bash /vagrant/{0};'".format( script_filename ) )
    else:
        home_folder = "/home/" + SERVERS[ server ][ "DEFAULT_USER" ]
        copy( [ script_filename, "to", server, "into", home_folder ] )

        # Generates the ssh command for the given server
        ssh_command = "ssh -i {0} {1}@{2} -t".format(
            SERVERS[ server ][ "KEYPAIR" ],
            SERVERS[ server ][ "DEFAULT_USER" ],
            SERVERS[ server ][ "IP" ]
        )

        # The full path to the script on the remote server
        script_remote_path = home_folder + '/' + script_filename

        # Call the script and removes it
        callcmd = "{0} 'bash {1}; sudo rm {1};'".format( ssh_command, script_remote_path )
        cmd( callcmd )

    # Removes the generated file
    cmd( "rm {0}".format( script_filename ) )

# Calls the initial method and exit.
init()
exit()