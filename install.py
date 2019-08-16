import subprocess

LIBRARIES = [
    'flask',
    'psycopg2',
    'wtforms',
    'passlib'
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
    uninstall_libraries_with_pip(LIBRARIES)
