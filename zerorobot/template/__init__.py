"""
This package contains all the logic regarding templates.

This is mostly the only package AYS developer should work with when implementing services

It contains 2 sub-module:
- base:
 This is where the TemplateBase class is defined. This is the class every every service should inherits from.
- decorator:
 A bunch of decorator tha can be used to wrap service actions to enabled new behaviors. E.g: retry policy, timeouts,...
"""
