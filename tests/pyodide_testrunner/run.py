import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from multiprocessing import Process, Queue

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support import expected_conditions as EC


# Path to the root of the repo.
REPO = pathlib.Path(__file__).parent.parent.parent
BROWSERS = {
    "chrome": (webdriver.Chrome, webdriver.ChromeOptions),
    "firefox": (webdriver.Firefox, webdriver.FirefoxOptions),
}


def build_wheel() -> str:
    """Build a wheel package of ``pygls`` and its testsuite.

    In order to test pygls under pyodide, we need to load the code for both pygls and its
    testsuite. This is done by building a wheel.

    To avoid messing with the repo this is all done under a temp directory.
    """

    with tempfile.TemporaryDirectory() as tmpdir:
        # Copy all required files.
        dest = pathlib.Path(tmpdir)

        # So that we don't have to fuss with packaging, copy the test suite into `pygls`
        # as a sub module.
        directories = [("pygls", "pygls"), ("tests", "pygls/tests")]

        for src, target in directories:
            shutil.copytree(REPO / src, dest / target)

        files = ["pyproject.toml", "poetry.lock", "README.md", "ThirdPartyNotices.txt"]

        for src in files:
            shutil.copy(REPO / src, dest)

        # Convert the lock file to requirements.txt.
        # Ensures reproducible behavour for testing.
        subprocess.run(
            [
                "poetry",
                "export",
                "-f",
                "requirements.txt",
                "--output",
                "requirements.txt",
            ],
            cwd=dest,
        )
        subprocess.run(
            ["poetry", "run", "pip", "install", "-r", "requirements.txt"], cwd=dest
        )
        # Build the wheel
        subprocess.run(["poetry", "build", "--format", "wheel"], cwd=dest)
        whl = list((dest / "dist").glob("*.whl"))[0]
        shutil.copy(whl, REPO / "tests/pyodide_testrunner")

        return whl.name


def spawn_http_server(q: Queue, directory: str):
    """A http server is needed to serve the files to the browser."""

    handler_class = partial(SimpleHTTPRequestHandler, directory=directory)
    server = ThreadingHTTPServer(("localhost", 0), handler_class)
    q.put(server.server_port)

    server.serve_forever()


def main():
    exit_code = 1
    whl = build_wheel()

    q = Queue()
    server_process = Process(
        target=spawn_http_server,
        args=(q, REPO / "tests/pyodide_testrunner"),
        daemon=True,
    )
    server_process.start()
    port = q.get()

    print("Running tests...")
    try:
        driver_cls, options_cls = BROWSERS[os.environ.get("BROWSER", "chrome")]

        options = options_cls()
        if "CI" in os.environ:
            options.binary_location = "/usr/bin/google-chrome"
            options.add_argument("--headless")

        driver = driver_cls(options=options)
        driver.get(f"http://localhost:{port}?whl={whl}")

        wait = WebDriverWait(driver, 120)
        try:
            button = wait.until(EC.element_to_be_clickable((By.ID, "exit-code")))
            exit_code = int(button.text)
        except WebDriverException as e:
            print(f"Error while running test: {e!r}")
            exit_code = 1

        console = driver.find_element(By.ID, "console")
        print(console.text)
    finally:
        if hasattr(server_process, "kill"):
            server_process.kill()
        else:
            server_process.terminate()

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
