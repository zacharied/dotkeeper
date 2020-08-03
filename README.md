# dotkeeper

![Python application](https://github.com/zacharied/dotkeeper/workflows/Python%20application/badge.svg)

This is a script designed for those who like to keep all their dotfiles nested in one directory and create symlinks to
them around the filesystem.

## Usage

You must have a symlink at `~/.dotkeep-link` that points to a directory. This directory will be seen as the "dotkeep" in
which all your dotfiles live.

Run `dotkeeper save` to find all symlinks pointing towards your dotkeep and write them to a file.

Run `dotkeeper restore` to read from such a file and regenerate the symlinks stored within.

## Requirements

Python 3 is required.
