# standard imports
import argparse
import os
import shutil
import subprocess
import sys
from typing import Optional, Mapping

# lib imports
from dotenv import load_dotenv

# Load the environment variables from the Environment File
load_dotenv()

# args placeholder
args = None

# result placeholder
ERROR = False
FAILURES = []

temp_repo = os.path.join('homebrew-release-action', 'homebrew-test')


def _parse_args(args_list: list) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Homebrew formula audit, install, and test')
    parser.add_argument(
        '--formula_file',
        default=os.environ['INPUT_FORMULA_FILE'],
        help='Homebrew formula file to audit, install, and test',
        type=str,
    )
    return parser.parse_args(args_list)


def _run_subprocess(
        args_list: list,
        capture_output: bool = False,
        env: Optional[Mapping] = None,
) -> bool:
    global ERROR
    result = subprocess.run(
        args=args_list,
        capture_output=capture_output,
        env=env,
    )
    print('Captured stdout:\n\n', result.stdout.decode('utf-8') if result.stdout else '')

    try:
        result.check_returncode()
    except subprocess.CalledProcessError:
        ERROR = True
        print('Captured stderr:\n\n', result.stderr.decode('utf-8') if result.stderr else '')
        return False
    else:
        return True


def get_brew_repository() -> str:
    proc = subprocess.run(
        args=['brew', '--repository'],
        capture_output=True,
    )
    return proc.stdout.decode('utf-8').strip()


def process_input_formula(formula_file: str) -> str:
    # check if the formula file exists
    if not os.path.exists(formula_file):
        raise FileNotFoundError(f'::error:: Formula file {formula_file} does not exist')

    # check if the formula file is a file
    if not os.path.isfile(formula_file):
        raise FileNotFoundError(f'::error:: Formula file {formula_file} is not a file')

    # check if the formula file is a .rb file
    if not formula_file.endswith('.rb'):
        raise ValueError(f'::error:: Formula file {formula_file} is not a .rb file')

    # get filename
    formula_filename = os.path.basename(formula_file)
    print(f'formula_filename: {formula_filename}')

    # get the first letter of formula name
    first_letter = formula_filename[0].lower()
    print(f'first_letter: {first_letter}')

    # enable developer mode
    print('Enabling brew developer mode')
    _run_subprocess(
        args_list=[
            'brew',
            'developer',
            'on'
        ],
        capture_output=True
    )

    # run brew tap
    print(f'Running `brew tap-new {temp_repo} --no-git`')
    _run_subprocess(
        args_list=[
            'brew',
            'tap-new',
            temp_repo,
            '--no-git'
        ],
        capture_output=True
    )

    clone_repo = os.path.join(os.environ['GITHUB_ACTION_PATH'], 'build')
    print(f'clone_repo: {clone_repo}')

    # copy the formula file to the two directories
    tap_dirs = [
        os.path.join(clone_repo, 'Formula', first_letter),  # this is the repo we will push back to
        os.path.join(get_brew_repository(), 'Library', 'Taps', temp_repo, 'Formula', first_letter)  # tap directory
    ]
    for d in tap_dirs:
        print(f'Copying {formula_filename} to {d}')
        os.makedirs(d, exist_ok=True)
        shutil.copy2(formula_file, d)

        if not os.path.exists(os.path.join(d, formula_filename)):
            raise FileNotFoundError(f'::error:: Formula file {formula_filename} was not copied to {d}')
        print(f'Copied {formula_filename} to {d}')

    return formula_filename.split('.')[0]


def is_brew_installed() -> bool:
    print('Checking if Homebrew is installed')
    return _run_subprocess(
        args_list=[
            'brew',
            '--version'
        ]
    )


def audit_formula(formula: str) -> bool:
    print(f'Auditing formula {formula}')
    return _run_subprocess(
        args_list=[
            'brew',
            'audit',
            '--os=all',
            '--arch=all',
            '--strict',
            '--online',
            os.path.join(temp_repo, formula)
        ],
        capture_output=True
    )


def install_formula(formula: str) -> bool:
    print(f'Installing formula {formula}')
    env = dict(
        HOMEBREW_NO_INSTALLED_DEPENDENTS_CHECK='1'
    )

    # combine with os environment
    env.update(os.environ)

    return _run_subprocess(
        args_list=[
            'brew',
            'install',
            '--verbose',
            os.path.join(temp_repo, formula)
        ],
        capture_output=True,
        env=env,
    )


def test_formula(formula: str) -> bool:
    print(f'Testing formula {formula}')
    return _run_subprocess(
        args_list=[
            'brew',
            'test',
            os.path.join(temp_repo, formula)
        ],
        capture_output=True
    )


def main():
    if not is_brew_installed():
        raise SystemExit(1, 'Homebrew is not installed')

    formula = process_input_formula(args.formula_file)

    if not audit_formula(formula):
        print(f'::error:: Formula {formula} failed audit')
        FAILURES.append('audit')

    if not install_formula(formula):
        print(f'::error:: Formula {formula} failed install')
        FAILURES.append('install')

    if not test_formula(formula):
        print(f'::error:: Formula {formula} failed test')
        FAILURES.append('test')

    if ERROR:
        raise SystemExit(
            1,
            f'::error:: Formula did not pass checks: {FAILURES}. Please check the logs for more information.'
        )

    print(f'Formula {formula} audit, install, and test successful')


if __name__ == '__main__':
    args = _parse_args(args_list=sys.argv[1:])
    main()
