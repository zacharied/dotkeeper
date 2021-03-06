#!/usr/bin/env python3

import os, sys
from pathlib import Path
import argparse

def find_links_to_dotkeep(dotkeep):
    links = []

    # Walk through home directory recursively.
    for root, dirs, files in os.walk(args.search_root):
        for filename in dirs + files:
            # Check if the link points to within the dotkeep.
            fullpath = f'{root}/{filename}'
            if os.path.islink(fullpath) and \
                    os.path.realpath(fullpath).startswith(dotkeep) and \
                    not fullpath.startswith(dotkeep) and \
                    not fullpath.startswith(str(Path.home()) + '/.dotkeep-link'):
                if args.separator in fullpath:
                    print(f'File "{fullpath}" has the separator in its path and will be skipped', file=sys.stderr)
                    continue
                localpath = os.path.realpath(fullpath).split(dotkeep + "/")[1]
                if not localpath:
                    # Sanity check.
                    raise IOError('dotkeep-local path was empty')
                links.append((localpath, fullpath))

    return list(map(lambda paths: (paths[0].replace(str(Path.home()), '~'), paths[1].replace(str(Path.home()), '~')), links))

def do_save_links(dotkeep, silent=False):
    # Make sure we can write to the record file.
    if args.links_file.exists():
        if not os.access(args.links_file, os.W_OK):
            raise IOError(f'unable to write to links file "{args.links_file}"')

    with args.links_file.open('w+') as links_file:
        for realpath, linkpath in find_links_to_dotkeep(dotkeep):
            if not silent:
                print(f'{linkpath} -> {realpath}')
            links_file.write(f'{realpath}{args.separator}{linkpath}\n')

def do_restore_links(dotkeep, silent=False):
    links = []
    
    if not args.links_file.exists() or not os.access(args.links_file, os.R_OK):
        raise IOError(f'unable to read from links file "{args.links_file}"')

    with args.links_file.open('r') as links_file:
        for line in links_file.readlines():
            splitted = line.strip().split(args.separator)
            if len(splitted) != 2:
                raise IOError(f'invalid separator pattern: {line}')
            
            links.append((splitted[0].replace('~', str(Path.home())), splitted[1].replace('~', str(Path.home()))))

    for localpath, linkpath in links:
        realpath = f'{dotkeep}/{localpath}'

        if not silent:
            print(f'Restoring {linkpath} -> {realpath}')

        if os.path.exists(linkpath):
            if silent:
                raise IOError('a link already exists')

            if os.path.islink(linkpath) and os.path.realpath(linkpath) == realpath:
                print('  Link already exists')
                continue
            
            print(f'A link already exists at "{linkpath}". Overwrite it? [y/n] ', end='')
            choice = input().lower()

            if choice == 'y':
                os.remove(linkpath)
            else:
                continue

        os.symlink(realpath, linkpath)

def load_args(arglist, action_required=False):
    global args
    parser = argparse.ArgumentParser(prog='dotkeeper', description='Save and restore linked dotfiles')
    if action_required:
        parser.add_argument('action', choices=['save', 'restore'])
    parser.add_argument('--separator', '-s', type=str, default='\t')
    parser.add_argument('--links-file', '-f', type=Path, default='links')
    parser.add_argument('--search-root', '-r', type=Path, default=Path.home())
    args = parser.parse_args(arglist)

def main():
    # Find the real path of the dotkeep.
    dotkeep_link = f'{Path.home()}/.dotkeep-link'

    if not os.path.islink(dotkeep_link) or not os.path.isdir(os.path.realpath(dotkeep_link)):
        print(f'"{dotkeep_link}" must be a symbolic link pointing to a directory.', file=sys.stderr)
        sys.exit(1)

    dotkeep = os.path.realpath(dotkeep_link)
    print(f'Dotkeep found at "{dotkeep}".')

    if args.action == 'save':
        do_save_links(dotkeep)
    elif args.action == 'restore':
        do_restore_links(dotkeep)

global args

if __name__ == '__main__':
    load_args(sys.argv[1:], action_required=True)
    main()
