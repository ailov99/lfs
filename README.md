Release version: 1.2
Hosted on: https://lfs.pythonanywhere.com/lfs

## Synopsis

####Development of:  
1. Innovative online distance-learning practice  
2. Effective online platform to host programme contents  
3. Framework for the creation of easily accessible digital contents (e.g. teacher resources, student activities)  
4. Interactive media (e.g. online feedback and discussion space)  

## Motivation

Training teachers around Scotland to teach about sustainability.  
Support learning for sustainability in Scottish schools.  
Allows teachers through online distance-learning.  
Make learning an enjoyable interactive experience via an innovative online platform.  

## Requirements
Before installation you must have the following installed:

Python 2.7+  
Django 1.7  
Pip  

## Installation
The following steps shows how to install and run our project:

$ cd lfs_project  
$ pip install -r requirements.txt  
$ python manage.py makemigrations  
$ python manage.py migrate  
$ python db_seed.py  

Launch locally

$ python manage.py runserver

## API Reference

Django==1.7  
django-model-utils==2.4  
django-bootstrap-form==3.2  
django-hitcount==1.2.1  
django-passwords==0.3.7  
django-annoying==0.9.0  
django-form-utils==1.0.3  
django-formset-js==0.5.0  
django-jquery-js==2.1.4  
pytz==2016.1  
pybbm==0.17.3  
Unidecode==0.4.19  
bbcode==1.0.22  
coverage==4.0.3  
pbr==1.8.1  
Pillow==3.0.0  
six==1.10.0  
stevedore==1.10.0  

## Tests

How to run tests:
$ python manage.py test  
  OR  
$ ./cover.sh  
This generates a HTML coverage report in htmlcov  


## License

The MIT License (MIT)
Copyright (c) 2016 Gregor Thomson, Aurimas Saulys, Duncan Milne, Reni Mihaylova, Aleksandar Ilov and Remigijus Bartasius

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
