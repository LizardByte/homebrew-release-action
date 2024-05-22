# homebrew-release-action
[![GitHub Workflow Status (CI)](https://img.shields.io/github/actions/workflow/status/lizardbyte/homebrew-release-action/ci.yml.svg?branch=master&label=CI%20build&logo=github&style=for-the-badge)](https://github.com/LizardByte/homebrew-release-action/actions/workflows/ci.yml?query=branch%3Amaster)
[![Codecov](https://img.shields.io/codecov/c/gh/LizardByte/homebrew-release-action.svg?token=d0EjUVzuPN&style=for-the-badge&logo=codecov&label=codecov)](https://app.codecov.io/gh/LizardByte/homebrew-release-action)

A reusable action to audit, install, test, and publish homebrew formulas to a tap.
This action is tailored to the @LizardByte organization, but can be used by anyone if they follow the same conventions.

## Basic Usage

See [action.yml](action.yml)

The intent here is that the formulas are supplied by the upstream repository, instead of the tap repository.
This works better for projects where the build process changes often, and formulas are more difficult to update.

As part of an automated release workflow, this action can be used to audit, install, test and publish the supplied
formulas to the tap repository.

Additionally, this action can be used to contribute the formula to an upstream homebrew-core repository, by
creating a pull request to the upstream repository. This feature is disabled by default. To use it you must
fork [Homebrew/homebrew-core](https://github.com/Homebrew/homebrew-core) and provide the `homebrew_core_fork_repo`.
You must also enable the `contribute_to_homebrew_core` input. Finally, you can modify the `upstream_homebrew_core_repo`
to point to a different repository if you are not using the official Homebrew/homebrew-core repository.

```yaml
steps:
  - name: Validate and Publish Homebrew Formula
    uses: LizardByte/homebrew-release-action@master
    with:
      formula_file: "${{ github.workspace }}/hello_world.rb"
      git_email: ${{ secrets.GIT_EMAIL }}
      git_username: ${{ secrets.GIT_USERNAME }}
      org_homebrew_repo: repo_owner/repo_name
```

It's possible to overwrite the defaults by providing additional inputs:

```yaml
steps:
  - name: Validate and Publish Homebrew Formula
    uses: LizardByte/homebrew-release-action@master
    with:
      contribute_to_homebrew_core: true
      formula_file: "${{ github.workspace }}/hello_world.rb"
      git_email: ${{ secrets.GIT_EMAIL }}
      git_username: ${{ secrets.GIT_USERNAME }}
      homebrew_core_fork_repo: repo_owner/homebrew-core
      org_homebrew_repo: repo_owner/repo_name
      org_homebrew_repo_branch: master
      publish: true  # you probably want to use some conditional logic here
      token: ${{ secrets.PAT }}  # required to publish
      upstream_homebrew_core_repo: Homebrew/homebrew-core
      validate: false  # skip the audit and install steps
```

> **Warning**:
> This action is only compatible with Linux and macOS runners, and will intentionally fail on Windows runners.

> **Note**:
> If you have a formula that is sensitive to the runner's OS version, you may wish to use a matrix strategy to run the
> action. In this case you probably only want to run the publish on one of them. Below is an example.

```yaml
jobs:
  publish:
    strategy:
    fail-fast: false  # false to test all, true to fail entire job if any fail
    matrix:
      include:
        # https://docs.github.com/en/actions/using-github-hosted-runners/about-github-hosted-runners/about-github-hosted-runners#standard-github-hosted-runners-for-public-repositories
        # while GitHub has larger macOS runners, they are not available for our repos :(
        - os: macos-12
          publish: true
        - os: macos-13
        - os: macos-14
        - os: ubuntu-20.04
        - os: ubuntu-22.04
  name: Homebrew (${{ matrix.os }})
  runs-on: ${{ matrix.os }}
  steps:
    - name: Checkout
      uses: actions/checkout@v4

    - name: Generate Formula
      shell: bash
      run: |
        # whatever you need to do to generate the formula

    - name: Validate and Publish Homebrew Formula
      uses: LizardByte/homebrew-release-action@master
      with:
        formula_file: "${{ github.workspace }}/build/hello_world.rb"
        git_email: ${{ secrets.GIT_EMAIL }}
        git_username: ${{ secrets.GIT_USERNAME }}
        org_homebrew_repo: repo_owner/repo_name
        org_homebrew_repo_branch: main
        publish: ${{ matrix.publish }}
        token: ${{ secrets.PAT }}
```
