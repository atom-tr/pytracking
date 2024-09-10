.. pytracking documentation master file, created by
   sphinx-quickstart on Mon Sep  9 15:34:05 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to pytracking's documentation!
======================================

This library provides a set of functions that provide open and click tracking
when sending emails. This is particularly useful if you rely on an Email
Service Provider (ESP) which does not provide open and click tracking.

The library only provides building blocks and does not handle the actual
sending of email or the serving of tracking pixel and links, but it comes
pretty close to this.

.. image:: https://github.com/powergo/pytracking/actions/workflows/test.yml/badge.svg
    :target: https://github.com/powergo/pytracking/actions/workflows/test.yml

.. image:: https://img.shields.io/pypi/v/pytracking.svg
   :target: https://pypi.python.org/pypi/pytracking

.. image:: https://img.shields.io/pypi/l/pytracking.svg

.. image:: https://img.shields.io/pypi/pyversions/pytracking.svg


Further reading
~~~~~~~~~~~~~~~

.. toctree::
   :maxdepth: 1
   :caption: Package documentation:

   usage/installation
   usage/api
   usage/quickstart
   usage/configuration
   usage/advanced
   changelog
   authors

.. toctree::
   :maxdepth: 1
   :caption: Examples documentation:

   ex/django

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
