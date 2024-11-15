# standard imports
import os
import subprocess
import sys
from typing import Optional

# lib imports
import pytest

# local imports
from action import main


def get_current_branch(cwd: Optional[str] = None) -> str:
    if cwd:
        os.chdir(cwd)  # hack for unit testing on windows
    if not cwd:
        github_ref = os.getenv('GITHUB_REF')
        if github_ref:
            # Running in a GitHub Actions runner.
            # The branch name is the last part of GITHUB_REF.
            return github_ref.split('/')[-1]

    # Fallback method when not running in a GitHub Actions runner
    proc = subprocess.run(
        ['git', 'branch', '--show-current'],
        cwd=cwd,
        capture_output=True,
    )
    return proc.stdout.decode().strip()


def test_parse_args():
    args = main._parse_args(['--formula_file', 'foo'])
    assert args.formula_file == 'foo'


def test_run_subprocess(capsys):
    result = main._run_subprocess(
        args_list=[sys.executable, '-c', 'print("foo")'],
    )

    assert result, "Process returned non zero exit code"

    captured = capsys.readouterr()
    assert 'foo' in captured.out
    assert captured.err == ''


def test_run_subprocess_fail(capsys):
    result = main._run_subprocess(
        args_list=[sys.executable, '-c', 'raise SystemExit(1)'],
    )

    assert not result, "Process returned zero exit code"
    assert main.ERROR


@pytest.mark.parametrize('outputs', [
    ('test_1', 'foo'),
    ('test_2', 'bar'),
])
def test_set_github_action_output(github_output_file, outputs):
    main.set_github_action_output(output_name=outputs[0], output_value=outputs[1])

    with open(github_output_file, 'r') as f:
        output = f.read()

    assert output.endswith(f"{outputs[0]}<<EOF\n{outputs[1]}\nEOF\n")


def test_get_brew_repository(operating_system):
    assert main.get_brew_repository()


def test_prepare_homebrew_core_fork(homebrew_core_fork_repo):
    main.prepare_homebrew_core_fork(
        branch_suffix='homebrew-release-action-tests',
        path=homebrew_core_fork_repo
    )

    # assert that the current branch is the branch we created
    branch = get_current_branch(cwd=homebrew_core_fork_repo)
    assert branch.endswith('homebrew-release-action-tests')


def test_proces_input_formula():
    with pytest.raises(FileNotFoundError):
        main.process_input_formula(formula_file='foo')

    with pytest.raises(FileNotFoundError):
        main.process_input_formula(formula_file=os.path.join(os.getcwd(), 'build'))

    with pytest.raises(ValueError):
        main.process_input_formula(formula_file=os.path.join(os.getcwd(), 'README.md'))

    formula = main.process_input_formula(formula_file=os.path.join(os.getcwd(), 'tests', 'Formula', 'hello_world.rb'))
    assert formula == 'hello_world'

    dirs = [
        os.path.join(os.environ['GITHUB_WORKSPACE'], 'homebrew-release-action', 'org_homebrew_repo'),
        os.path.join(os.environ['GITHUB_WORKSPACE'], 'homebrew-release-action', 'homebrew_core_fork_repo'),
    ]

    for d in dirs:
        assert os.path.isfile(os.path.join(d, 'Formula', 'h', 'hello_world.rb'))


def test_is_brew_installed(operating_system):
    assert main.is_brew_installed()


def test_brew_upgrade():
    assert main.brew_upgrade()


def test_audit_formula():
    assert main.audit_formula(formula='hello_world')


def test_brew_install_formula():
    assert main.install_formula(formula='hello_world')


def test_test_formula():
    assert main.test_formula(formula='hello_world')


def test_main(brew_untap, homebrew_core_fork_repo, input_validate):
    main.args = main._parse_args(args_list=[])
    main.main()
    assert not main.ERROR
    assert not main.FAILURES
