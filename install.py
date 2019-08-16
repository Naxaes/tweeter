import subprocess

LIBRARIES = [
    'flask>=1.1.0,<2.0.0',
    'psycopg2>=2.8.0,<3.0.0',
    'wtforms>=2.2.0,<3.0.0',
    'passlib>1.7.0,<2.0.0'
]


def install_libraries_with_pip(libraries):
    try:
        # For UNIX devices.
        for library in libraries:
            subprocess.call('python -m pip install {}'.format(library))
    except FileNotFoundError:
        # For Windows devices.
        for library in libraries:
            subprocess.call('py -m pip install {}'.format(library))


def uninstall_libraries_with_pip(libraries):
    try:
        # For UNIX devices.
        for library in libraries:
            subprocess.call('python -m pip uninstall {}'.format(library))
    except FileNotFoundError:
        # For Windows devices.
        for library in libraries:
            subprocess.call('py -m pip uninstall {}'.format(library))


if __name__ == '__main__':
    install_libraries_with_pip(LIBRARIES)
