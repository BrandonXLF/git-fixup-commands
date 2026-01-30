# Git Fixup Commands

> pip install git-fixup-commands

A suite of Git commands to easily edit any previous Git commit via `git commit --fixup` and `git rebase --autosquash`. Works with any commit in the commit tree, including the root commit and merge commits.

## Commands

* `git fixup COMMIT_REF` - Fixup the given commit with the currently staged changes (stage using `git add`). Unstaged changes are temporarily stashed.
* `git amend COMMIT_REF` - Amend the given commit (like `git commit --amend`) with the currently staged changes (stage using `git add`). Unstaged changes are temporarily stashed.
* `git reword COMMIT_REF` - Reword / edit the commit message of the given commit.

## Examples

* `git fixup HEAD~2` - Apply staged changes the commit before the previous commit.
* `git reword 3e58f12` - Edit the commit message of the commit with hash `3e58f12`.

## Options

All the commands above support the following options:

* `-p`, `--pause` - Pause the rebase after the commit is updated. Allows for editing the newly modified commit using `git commit --amend`. Resume with `git rebase --continue`. Not compatible with `--interactive` as the sequence editor is overridden.

All flags from `git rebase` are supported. Note that `--autosquash`, `--autostash`, and `--rebase-merges` are already set. For example, the following may be useful:

* `-i`, `--interactive` - Enable the interactive rebase editor, which allows interactive editing of commits between the modified commit and HEAD.

## Installation

The suite of commands can be installed to your system path (via the Python script folder) using `pip install git-fixup-commands`.

## Limitations

* Merge commits are recreated, meaning changes may need to be made again if git does not have a recorded resolution to reuse.

## How It Works

The provided commands are mainly a wrapper around two Git commands, `git commit --fixup` and `git rebase --autosquash`. The first command creates a special fixup commit which is then processed by the second command and squashed into the indicated commit.

## Repository

### Running

The project can be installed to your system using `python3 -m pip install -e .`. Commands can also be run using `python3 main.py COMMAND`.

### Testing

A suite of scenario-based tests, which run the commands in real Git repositories, is provided in the `test` folder. These tests can be run with `python3 test/test.py`.
