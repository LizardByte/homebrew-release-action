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
        cwd: Optional[str] = None,
        env: Optional[Mapping] = None,
) -> bool:
    global ERROR
    result = subprocess.run(
        args=args_list,
        capture_output=capture_output,
        cwd=cwd,
        env=env,
    )
    print('Captured stdout:\n\n')
    print(result.stdout.decode('utf-8') if result.stdout else '')

    try:
        result.check_returncode()
    except subprocess.CalledProcessError:
        ERROR = True
        print('Captured stderr:\n\n')
        print(result.stderr.decode('utf-8') if result.stderr else '')
        return False
    else:
        return True


def set_github_action_output(output_name: str, output_value: str):
    """
    Set the output value by writing to the outputs in the Environment File, mimicking the behavior defined <here
    https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions#setting-an-output-parameter>__.

    Parameters
    ----------
    output_name : str
        Name of the output.
    output_value : str
        Value of the output.
    """
    with open(os.path.abspath(os.environ["GITHUB_OUTPUT"]), "a") as f:
        f.write(f'{output_name}<<EOF\n')
        f.write(output_value)
        f.write('\nEOF\n')


def branch_exists(branch: str) -> bool:
    try:
        subprocess.check_output(['git', 'show-ref', '--verify', '--quiet', f'refs/heads/{branch}'])
        return True
    except subprocess.CalledProcessError:
        return False


def get_brew_repository() -> str:
    proc = subprocess.run(
        args=['brew', '--repository'],
        capture_output=True,
    )
    return proc.stdout.decode('utf-8').strip()


def prepare_homebrew_core_fork(
        branch_suffix: str,
        path: str,
) -> None:
    print('Preparing Homebrew/homebrew-core fork')

    # checkout a new branch
    branch_name = f'homebrew-release-action/{branch_suffix}'
    if not branch_exists(branch_name):  # create a new branch if it does not exist
        print(f'Creating new branch {branch_name}')
        _run_subprocess(
            args_list=['git', 'checkout', '-b', branch_name],
            capture_output=True,
            cwd=path,
        )
    else:  # checkout the existing branch
        print(f'Checking out existing branch {branch_name}')
        _run_subprocess(
            args_list=['git', 'checkout', branch_name],
            capture_output=True,
            cwd=path,
        )

    # add the upstream remote
    print('Adding upstream remote')
    _run_subprocess(
        args_list=[
            'git',
            'remote',
            'add',
            'upstream',
            f'https://github.com/{os.environ["INPUT_UPSTREAM_HOMEBREW_CORE_REPO"]}'
        ],
        capture_output=True,
        cwd=path,
    )

    # fetch the upstream remote
    print('Fetching upstream remote')
    _run_subprocess(
        args_list=['git', 'fetch', 'upstream'],
        capture_output=True,
        cwd=path,
    )

    # hard reset
    print('Hard resetting to upstream/master')
    _run_subprocess(
        args_list=['git', 'reset', '--hard', 'upstream/master'],
        capture_output=True,
        cwd=path,
    )

    set_github_action_output(
        output_name='homebrew_core_branch',
        output_value=branch_name
    )


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

    formula = formula_filename.split('.')[0]

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

    org_homebrew_repo = os.path.join(os.environ['GITHUB_ACTION_PATH'], 'org_homebrew_repo')
    homebrew_core_fork_repo = os.path.join(os.environ['GITHUB_ACTION_PATH'], 'homebrew_core_fork_repo')
    print(f'org_homebrew_repo: {org_homebrew_repo}')
    print(f'homebrew_core_fork_repo: {homebrew_core_fork_repo}')

    if os.getenv('INPUT_CONTRIBUTE_TO_HOMEBREW_CORE').lower() == 'true':
        prepare_homebrew_core_fork(branch_suffix=formula, path=homebrew_core_fork_repo)

    # copy the formula file to the two directories
    tap_dirs = [
        os.path.join(org_homebrew_repo, 'Formula', first_letter),  # we will commit back to this
        os.path.join(homebrew_core_fork_repo, 'Formula', first_letter),  # we will commit back to this
        os.path.join(get_brew_repository(), 'Library', 'Taps', temp_repo, 'Formula', first_letter)  # tap directory
    ]
    for d in tap_dirs:
        print(f'Copying {formula_filename} to {d}')
        os.makedirs(d, exist_ok=True)
        shutil.copy2(formula_file, d)

        if not os.path.exists(os.path.join(d, formula_filename)):
            raise FileNotFoundError(f'::error:: Formula file {formula_filename} was not copied to {d}')
        print(f'Copied {formula_filename} to {d}')

    return formula


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
