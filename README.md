# vron
A little connector between 2 APIs: Viator &amp; RON.

## Technologies and Tools Used

### Back-End
- Python >= 3.4
- Django >= 1.7
- MySQL >= 5.4

### Front-End
- HTML
- CSS
- Javascript

### IDE of preference
- PyCharm
- Sublime

### Server Side
- Ubuntu 14.0.4
- Vagrant
- Virtual Box
- GIT
- Celery

### APIs
- [RON Api](http://wiki.respax.com.au/respax/ron_api)
- [Viator API](http://supplierapitestharness.viatorinc.com/documentation.php)


## Installing required software

1. Install Vagrant (Go to: http://www.vagrantup.com/downloads.html)
2. Install Virtual Box (Go to: https://www.virtualbox.org/wiki/Downloads)
3. Install GIT, including command line options. (Go to: http://git-scm.com/downloads)
4. Install Python 3.4 (Go to: https://www.python.org/)


## Cloning the code

1. Clone the GIT Repository using the following command:
    `git clone https://github.com/humbertomn/vron.git ~/vron`

    PS: If you want to install anywhere on your system, change the path: "~/vron"

2. To start up your virtual environment, run the following command:
    ```
    cd ~/vron/infra
    vagrant up
    ```
    Vagrant is configured to use the ports 2222, 8080, 8181 and 4443, so make sure they are free to be used.

3. Run the following command to configure your environment (Make sure you still in the 'infra' folder).
    `python helper.py config site on local with database`

    The helper.py script will install all needed packages on your local enviroment, such as apache, git and also a local mysql database. It will ask to you the root's password for the database (Choose one that is good to you. We will use "88uhGLua19UOSAmav" for examplification).

    PS: It's ok to see an error message from apache (it would not be able to restart properly because it doesn't found the SSL files, It's ok, keep following the steps).


## Installing the database
1. Connect to the virtual machine via SSH:
    `python helper.py connect local` or `vagrant ssh`

2. Access your mysql and create a database called 'vron'
    `mysql -u root -p`
    When asked for the password, type in: 88uhGLua19UOSAmav

3. Create the database 'vron' and the user 'vron':
    ```
    create database vron;
    create user vron@localhost identified by '99pUq3PAwFjnBsdZe3';
    grant all on vron.* to vron@localhost;
    exit;
    ```

4. Activate your python virtualenv and run a 'migrate' inside your django application:
    ```
    source /vronvenv/bin/activate
    python /vron/django/manage.py migrate
    ```

5. Create a superuser to be able to access the admin area
    ```
    source /vronvenv/bin/activate
    python /vron/django/manage.py createsuperuser
    ```


## Testing
To make sure it works open up [http://localhost:8080/]
