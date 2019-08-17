import os
import sys
import subprocess
from pathlib import Path


LIBRARIES = [
    'flask    >= 1.1.0, < 2.0.0',
    'psycopg2 >= 2.8.0, < 3.0.0',
    'wtforms  >= 2.2.0, < 3.0.0',
    'passlib  >= 1.7.0, < 2.0.0',
]


def install_libraries_with_pip(libraries):
    for library in libraries:
        subprocess.call([sys.executable, '-m', 'pip', 'install', library])


def uninstall_libraries_with_pip(libraries):
    for library in libraries:
        subprocess.call([sys.executable, '-m', 'pip', 'uninstall', library])


# InstallCertificatesMinorVersion6.command is copied from the location:
# /Applications/Python 3.6/Install Certificates.command
def call_some_stupid_script_required_by_mac_for_python_version_3_6_and_above_to_certify_https_requests():
    minor  = sys.version_info.minor
    script = './InstallCertificatesMinorVersion{}.command'.format(minor)
    path_to_this_files_directory = Path(__file__).parent

    full_path_to_script = os.path.join(path_to_this_files_directory, script)

    print(full_path_to_script)

    subprocess.call(['chmod', '+x', full_path_to_script])
    subprocess.call([full_path_to_script], shell=True)

