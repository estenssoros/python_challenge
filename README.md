# Python Challenge

To begin:
- make sure you have libmysqlclient-dev installed

```
$ sudo apt-get -y install libmysqlclient-dev gcc
```
- edit values in mysql_cnf.sh

```
export MYSQL_USERNAME='root'
export MYSQL_HOST='localhost'
```

- also update mysql connection options in myapp/myapp/settings.py

```
78 DATABASES = {
79     'default': {
80         'ENGINE': 'django.db.backends.mysql',
81         'NAME': 'swimlane',
82         'USER': 'root',
83         'PASSWORD': '',
84         'HOST': '',
85         'PORT': '3306',
86     }
87 }
```

- run this script:

```
$ ./start_interview.sh
```
  - installs modules in requirements packaged and launches django app
