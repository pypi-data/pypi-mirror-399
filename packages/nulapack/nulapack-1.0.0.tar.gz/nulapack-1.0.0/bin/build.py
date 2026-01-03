#!/usr/bin/env python3

import argparse
import logging
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path


logger = logging.getLogger(name=__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", "%d-%m-%Y %H:%M:%S")

file_handler = logging.FileHandler("build.log", "w")
file_handler.setLevel(logging.DEBUG)

file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.addFilter(lambda record: record.levelno != logging.ERROR)
stdout_handler.setFormatter(formatter)
logger.addHandler(stdout_handler)

stderr_handler = logging.StreamHandler(sys.stderr)
stderr_handler.setLevel(logging.ERROR)
stderr_handler.setFormatter(formatter)
logger.addHandler(stderr_handler)


def run_command(command, cwd=None):
    if cwd is None:
        logger.warning("No working directory specified. Using current directory.")
        cwd = Path.cwd()
    else:
        cwd = Path(cwd)

    log_file_path = cwd / "build.log"

    logger.info(f"Executing command: '{command}' in '{cwd}'")

    with subprocess.Popen(
        shlex.split(command),
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=0,
        env=dict(**os.environ, PYTHONUNBUFFERED="1"),
        text=True,
    ) as proc:
        with open(log_file_path, "a") as _log_file:
            for line in proc.stdout:
                # _log_file.write(line)
                logger.debug(line.rstrip())

        rv = proc.wait()

    if rv != 0:
        logger.error(f"Command exited with status {rv}")
        sys.exit(rv)

    logger.info("Command executed successfully.")


def build(build_tests=False):
    cmake_cmd = "cmake -S . -B build"
    version = (
        subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"], capture_output=True, text=True
        ).stdout.strip()
        or None
    )
    if not version:
        raise RuntimeError("Could not determine version from git tags.")

    cmake_cmd += f" -DNULAPACK_VERSION={version[1:]}"

    if sys.platform == "win32":
        cmake_cmd += "  -G 'MinGW Makefiles'"

    if build_tests:
        cmake_cmd += " -DBUILD_TEST=ON"
    else:
        cmake_cmd += " -DBUILD_TEST=OFF"

    run_command(cmake_cmd)
    run_command("make", cwd="build")


def install():
    run_command("pip install . -v --log build.log")


def wheel():
    run_command("pip wheel . -v -w dist --log build.log")


def doxygen():
    run_command("doxygen Doxyfile")


def develop(build_tests=True, with_py=True):
    build(build_tests=build_tests)
    if with_py:
        run_command("pip install .[dev] -v --log build.log")


def test(build_tests=False, with_py=False):
    develop(build_tests, with_py)

    for file in Path(__file__).parent.glob("test_*"):
        if file.is_file() and os.access(file, os.X_OK):
            logger.info(f"Running {file.name} ...")
            run_command(f"bin/{file.name}")
    run_command("pytest -s -v")


def clean():
    logger.debug("Starting cleanup ...")

    run_command("pip uninstall nulapack -y")

    for entry in Path("").iterdir():
        if entry.name in ["dist", "build", "lib", ".pytest_cache", ".ruff_cache"]:
            logger.info(f"Removing '{entry}'")
            shutil.rmtree(entry)
        if entry.name == "bin" and entry.is_dir():
            for bin_entry in entry.iterdir():
                if bin_entry.is_file() and bin_entry.name.startswith("test_"):
                    logger.info(f"Removing '{bin_entry}'")
                    bin_entry.unlink()
        if entry.name.startswith(".mesonpy"):
            logger.info(f"Removing '{entry}'")
            shutil.rmtree(entry)
        if entry.name.endswith("egg-info"):
            logger.info(f"Removing '{entry}'")
            shutil.rmtree(entry)
        if entry.suffix == ".log":
            logger.info(f"Removing '{entry}'")
            entry.unlink()

    logger.info("Finished cleanup.")


def main():
    parser = argparse.ArgumentParser(description="NULAPACK Build Script")
    parser.add_argument(
        "mode",
        help="""Build mode:
        'build' -- Build library
        'install' -- Install python interface
        'wheel' -- Build python interface wheel
        'doxygen' -- generates documentation
        'test' -- Test library
        'develop' -- Build with tests and install editable python interface
        'clean' -- Remove build artifacts""",
        type=str,
        choices=["build", "install", "wheel", "doxygen", "develop", "test", "clean"],
    )
    parser.add_argument(
        "--build-tests",
        action="store_true",
        help="Enable building and running tests",
    )
    parser.add_argument(
        "--with-py",
        action="store_true",
        help="Build/install the Python interface",
    )

    args = parser.parse_args()

    if not any(vars(args).values()):
        parser.print_help()
        sys.exit(0)

    if args.mode == "build":
        build(build_tests=args.build_tests)
    if args.mode == "install":
        install()
    if args.mode == "wheel":
        wheel()
    if args.mode == "doxygen":
        doxygen()
    if args.mode == "develop":
        develop(args.build_tests, args.with_py)
    if args.mode == "test":
        test(args.build_tests, args.with_py)
    if args.mode == "clean":
        clean()


if __name__ == "__main__":
    main()
