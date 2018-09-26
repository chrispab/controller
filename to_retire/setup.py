#!/usr/bin/env python

"""
setup.py file for iotest
"""

from distutils.core import setup, Extension


iotest_module = Extension('_iotest',
                           sources=['iotest_wrap.c', 'iotest.c'], 
                           include_dirs= ['/home/ubuntu/Documents/projects/iotestprj','/home/ubuntu/c_environment/hardware/arduino/cores/arduino', '/home/ubuntu/c_environment/hardware/arduino/variants/sunxi'],
                           library_dirs=['/home/ubuntu/c_environment/', '/home/ubuntu/c_environment/hardware/arduino/cores/arduino/'],
                           libraries=['home/ubuntu/c_environment/libarduino.so','/home/ubuntu/c_environment/hardware/arduino/cores/arduino/platform.o']
                           )

setup (name = 'iotest',
       version = '0.1',
       author      = "CB",
       description = """iotest setup""",
       ext_modules = [iotest_module],
       py_modules = ["iotest"],
       )
