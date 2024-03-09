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
  - name: Publish Homebrew Formula
    uses: LizardByte/homebrew-release-action@master
    with:
      formula_file: "${{ github.workspace }}/hello_world.rb"
      git_email: ${{ secrets.GIT_EMAIL }}
      git_username: ${{ secrets.GIT_USERNAME }}
      org_homebrew_repo: repo_owner/repo_name
      token: ${{ secrets.PAT }}
```

It's possible to overwrite the defaults by providing additional inputs:

```yaml
steps:
  - name: Publish Homebrew Formula
    uses: LizardByte/homebrew-release-action@master
    with:
      contribute_to_homebrew_core: true
      formula_file: "${{ github.workspace }}/hello_world.rb"
      git_email: ${{ secrets.GIT_EMAIL }}
      git_username: ${{ secrets.GIT_USERNAME }}
      homebrew_core_fork_repo: repo_owner/homebrew-core
      org_homebrew_repo: repo_owner/repo_name
      org_homebrew_repo_branch: master
      token: ${{ secrets.PAT }}
      upstream_homebrew_core_repo: Homebrew/homebrew-core
```
