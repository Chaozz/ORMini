ORMini
======

[![Build Status](https://travis-ci.org/Chaozz/ORMini.svg?branch=master)](https://travis-ci.org/Chaozz/ORMini)
[![codecov](https://codecov.io/gh/Chaozz/ORMini/branch/master/graph/badge.svg)](https://codecov.io/gh/Chaozz/ORMini)

CS542 Group Project

Overview
-------

A simple Python ORM framework.


Install Requirements
----------------

- Install Python 2

- Open a terminal, go to the project folder, and run this command to install all project dependencies:

      $ pip install -r requirements.txt

Structure
-----------

```
+-- ormini/
|   +-- __init__.py
|   +-- db.py
|   +-- fields.py
|   +-- models.py
|   +-- utils.py
+-- tests/
+-- config.py
+-- runtests.py
```

#### Main folders explanation

__ormini/__ folder

This folder contains the source code.

- __db.py__
Code for db connections.

- __fields.py__
Code for data fields.

- __model.py__
Code for data Models and CRUD methods.

__tests/__ folder

This folder contains the code for unit tests

__config.py__
The general settings for the framework.

__runtests.py__

Run this file to do the unit tests and code linting.


**The Project is still in progress. All the best and enjoy coding.**



