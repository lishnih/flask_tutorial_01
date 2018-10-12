#!/usr/bin/env python
# coding=utf-8
# Stan 2016-04-24

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import logging
logging.basicConfig(level=logging.DEBUG)

from flask_tutorial_01.main import app


if __name__ == '__main__':
    app.run(debug=True)
#   app.run(host='0.0.0.0', ssl_context='adhoc', debug=True)