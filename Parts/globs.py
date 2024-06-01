# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2023 ParaPy Holding B.V.
#
# You may use the contents of this file in your application code.
#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY
# KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A PARTICULAR
# PURPOSE.

import os
import sys


def main_dir():
    """Return top-level directory of parapy source code.

    :rtype: str
    """
    encoding = sys.getfilesystemencoding()
    if hasattr(sys, "frozen"):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(__file__)


CUR_DIR = main_dir()
AIRFOIL_DATA = os.path.join(CUR_DIR, "airfoil.dat")

if __name__ == '__main__':
    print(CUR_DIR)
    print(AIRFOIL_DATA)
