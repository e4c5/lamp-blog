A django blog that stores data in the google-cloud-datastore and runs
on google-appengine.

Warning hasn't been updated since 2015 and still uses django 1.5 but 
that will be fixed shortly.

Powers http://raditha.com/


Upgrading to Django 1.11
--
The upgrade process has kicked off at last. Apparently if you specify the django
version as 1.11 app engine still tries to run some old 1.4 code (management.setup_environ
the solution is to install django as a vendor library. The official app engine document
suggests

   pip install -t lib Django
   

If you want to test locally on ubuntu based installation, the above may not give the
excepted result because in ubuntu `--user` is a default option for pip The following error
may result if you are not in a virtual environment. 

>   DistutilsOptionError: can't combine user with prefix, exec_prefix/home, or install_(plat)base

The solution then is to try the following command or activate a virtualenv:

   pip install -t --system lib Django

