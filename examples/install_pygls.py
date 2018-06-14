'''
Script is used to install the pygls with command `PYTHON_PATH setup.py install`
PYTHON_PATH = .vscode/settings.json -> "python.pythonPath"
'''
import json
from os.path import dirname, join
import subprocess


this_folder = dirname(__file__)
root_folder = join(this_folder, '../')


def get_settings():
    settings_path = join(root_folder, '.vscode/settings.json')
    try:
        with open(settings_path, 'r') as f:
            return json.load(f)
    except:
        msg = ("Please create file .vscode/settings.json and "
               "add python.pythonPath configuration.")
        print(msg)


def get_section(settings, section):
    try:
        return settings[section]
    except:
        print("Missing {} in configuration".format(section))


def install_pygls(python_path):
    cmd = ' '.join([python_path, "setup.py", "install"])
    print("Installing pygls with command: {}".format(cmd))
    try:
        p = subprocess.Popen(cmd,
                             cwd=root_folder,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        for line in p.stdout.readlines():
            print(line.decode('utf-8'))
    except Exception as e:
        print(e)


settings = get_settings()
python_path = get_section(settings, 'python.pythonPath')
install_pygls(python_path)
