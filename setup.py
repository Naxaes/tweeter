"""
Run this to install all libraries needed to run the application, and to create data files. You'll need access to
internet in order to run this file successfully.
"""

import os
import sys

assert sys.version_info >= (3, 6, 0), "Your python version {}.{}.{} is too old. Please use a newer version.".format(*sys.version_info)
"""
Python versions between 3.0 and 3.6 will probably work as well. However, pip isn't included until 3.4 in the default
python installation, and there are some API differences. If you want to use another version, then you'll have to do the 
appropriate changes manually. 
"""

# Project python packages.
from scripts import install
from scripts import generate

prompt = '''\
Do you want to:
   1. Install dependencies.
   2. Generate database data and forms.
   3. Both.
'''


def main():

    answer = input(prompt)
    while answer not in ('1', '2', '3'):
        answer = input("Please type 1, 2 or 3. ")

    if answer == '1':
        do_installation = True
        do_generation   = False
    elif answer == '2':
        do_installation = False
        do_generation   = True
    elif answer == '3':
        do_installation = True
        do_generation   = True
    else:
        raise ValueError(f"Invalid input '{answer}'!")


    # Install all necessary libraries before continuing.
    if do_installation:
        print('Installing...')
        install.install_libraries_with_pip(install.REQUIRED_LIBRARIES)
        if sys.platform.startswith('darwin') and sys.version_info.minor >= 6:
            install.install_some_stupid_stuff_required_by_mac_for_python_version_3_6_and_above_to_certify_https_requests()
        print('Installation completed!')

    # Generate the data files.
    if do_generation:
        print('Generating...')
        root_directory = os.getcwd()
        generate.sql_create_file_and_data(root_directory)

        # Generate forms based on database file
        target_directory = os.path.join(os.getcwd(), 'app')
        generate.forms_file(target_directory)
        print('Generation completed!')


if __name__ == '__main__':
    main()
