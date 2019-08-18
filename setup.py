"""
Run this to install all libraries needed to run the application, and to create data files. You'll need access to
internet in order to run this file successfully.
"""

import os
import sys

assert sys.version_info >= (3, 4, 0), "Your python version {}.{}.{} is too old. Please use a newer version.".format(*sys.version_info)
"""
Python versions between 3.0 and 3.4 will probably work as well. However, pip isn't included until 3.4 in the default
python installation, and there are some API differences. 'pathlib' isn't included either. If you want to use another 
version, then you'll have to do the appropriate changes manually.
"""

# Project python packages.
from scripts import install
from scripts import generate


def main():
    # Install all necessary libraries before continuing.
    install.install_libraries_with_pip(install.REQUIRED_LIBRARIES)
    if sys.platform.startswith('darwin') and sys.version_info.minor >= 6:
        install.install_some_stupid_stuff_required_by_mac_for_python_version_3_6_and_above_to_certify_https_requests()

    # Generate the data files.
    root_directory = os.getcwd()
    generate.sql_create_file_and_data(root_directory)


if __name__ == '__main__':
    main()
