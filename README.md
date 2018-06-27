# pygls - Python Generic Language Server

(Pronounced like "spy glass".)

A generic implementation of the [Language Server Protocol][1] for use as a foundation for writing non-Python language servers (e.g. XML).

[1]: https://microsoft.github.io/language-server-protocol/

## Setup

Since there are no `requirements.txt`, installation is done from the project's root with following command:
`python setup.py install`

If you are using virtual environment (VE), then follow next steps:

1. Open terminal, create and activate VE ([see how](https://docs.python.org/3/tutorial/venv.html))
2. In the same terminal, navigate to project root directory and run `python setup.py install` command (be sure that VE is activated)
3. In project's root in `.vscode/settings.json` set `python.pythonPath` to point to your VE's python executable

### Run tests

1. `pip install -r requirements_dev.txt`
2. Open terminal, navigate to tests directory and run `pytest` command
