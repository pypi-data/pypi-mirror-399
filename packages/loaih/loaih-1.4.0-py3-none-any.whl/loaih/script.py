#!/usr/bin/env python
# encoding: utf-8
"""Helps with command line commands."""

import os
import shutil
import sys
import json
import click
import yaml
import loaih
import loaih.version
import loaih.build


@click.group()
@click.version_option(loaih.version.version)
def cli():
    """Helps with command line commands."""


@cli.command()
@click.option('-j', '--json', 'jsonout', default=False, is_flag=True, help="Output format in json.")
@click.option('--default-to-current', '-d', is_flag=True, default=False, help="If no versions are found, default to current one (for daily builds). Default: do not default to current.")
@click.argument('query')
def getversion(query, jsonout, default_to_current):
    """Get download information for named or numbered versions."""

    batchlist = []
    queries = []
    if ',' in query:
        queries.extend(query.split(','))
    else:
        queries.append(query)

    for singlequery in queries:
        elem = loaih.Solver.parse(singlequery, default_to_current)
        if elem.version not in { None, "" }:
            batchlist.append(elem)

    if len(batchlist) > 0:
        if jsonout:
            click.echo(json.dumps([x.to_dict() for x in batchlist ]))
        else:
            for value in batchlist:
                click.echo(value)


@cli.command()
@click.option('-a', '--arch', 'arch', default='x86_64',
    type=click.Choice(['x86', 'x86_64', 'all'], case_sensitive=False), help="Build the AppImage for a specific architecture. Default: x86_64")
@click.option('--check', '-c', is_flag=True, default=False, help="Checks in the repository path if the queried version is existent. Default: do not check")
@click.option('--checksums', '-e', is_flag=True, default=False, help="Create checksums for each created file (AppImage). Default: do not create checksums.")
@click.option('--keep-downloads', '-k', 'keep', is_flag=True, default=False, help="Keep the downloads folder after building the AppImage. Default: do not keep.")
@click.option('--languages', '-l', 'language', default='basic', type=str, help="Languages to be included. Options: basic, standard, full, a language string (e.g. 'it') or a list of languages comma separated (e.g.: 'en-US,en-GB,it'). Default: basic")
@click.option('--offline-help', '-o', 'offline', is_flag=True, default=False, help="Include the offline help pages for the chosen languages. Default: no offline help")
@click.option('--portable', '-p', 'portable', is_flag=True, default=False, help="Create a portable version of the AppImage or not. Default: no portable")
@click.option('--sign', '-s', is_flag=True, default=False, help="Sign the build with your default GPG key. Default: do not sign")
@click.option('--updatable', '-u', is_flag=True, default=False, help="Create an updatable AppImage (compatible with zsync2). Default: not updatable")
@click.option('--download-path', '-d', default='./downloads', type=str, help="Path to the download folder. Default: ./downloads")
@click.option('--repo-path', '-r', default='.', type=str, help="Path to the final storage of the AppImage. Default: current directory")
@click.option('--debug', 'debug', is_flag=True, default=False, help="Activate debug options.")
@click.argument('query')
def build(arch, language, offline, portable, updatable, download_path, repo_path, check, checksums, sign, keep, query, debug):
    """Builds an Appimage with the provided options."""

    # Multiple query support
    queries = []
    if ',' in query:
        queries.extend(query.split(','))
    else:
        queries.append(query)

    # Parsing options
    arches = []
    if arch.lower() == 'all':
        # We need to build it twice.
        arches = ['x86', 'x86_64']
    else:
        arches = [arch.lower()]

    # Other more global variables
    repopath = os.path.abspath(repo_path)
    if not os.path.exists(repopath):
        os.makedirs(repopath, exist_ok=True)
    downloadpath = os.path.abspath(download_path)
    if not os.path.exists(downloadpath):
        os.makedirs(downloadpath, exist_ok=True)

    for myquery in queries:
        for appbuild in loaih.build.Collection(myquery, arches):
            # Configuration phase
            appbuild.debug = debug
            appbuild.tidy_folder = False
            appbuild.language = language
            appbuild.offline_help = offline
            appbuild.portable = portable
            appbuild.updatable = updatable
            appbuild.storage_path = repopath
            appbuild.download_path = downloadpath
            appbuild.sign = sign

            # Running phase
            appbuild.calculate()

            if check:
                appbuild.check()

            appbuild.download(compact = True)
            appbuild.build()
            if checksums:
                appbuild.checksums()
            appbuild.publish()

            del appbuild

    if not keep:
        shutil.rmtree(downloadpath)


@cli.command()
@click.option("--verbose", '-v', is_flag=True, default=False, help="Show building phases.", show_default=True)
@click.argument("yamlfile")
def batch(yamlfile, verbose):
    """Builds a collection of AppImages based on YAML file."""
    # Defaults for a batch building is definitely more different than a
    # manual one. To reflect this behaviour, I decided to split the commands
    # between batch (bulk creation) and build (manual building).

    # Check if yamlfile exists.
    if not os.path.exists(os.path.abspath(yamlfile)):
        click.echo(f"YAML file {yamlfile} does not exists or is unreadable.")
        sys.exit(1)

    # This is a buildfile. So we have to load the file and pass the build
    # options ourselves.
    config = {}
    with open(os.path.abspath(yamlfile), 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)

    # Globals for yamlfile
    gvars = {}
    gvars['download_path'] = "/var/tmp/downloads"
    if 'download' in config['data'] and config['data']['download']:
        gvars['download_path'] = config['data']['download']

    gvars['force'] = False
    if 'force' in config['data'] and config['data']['force']:
        gvars['force'] = config['data']['force']

    gvars['storage_path'] = "/srv/http/appimage"
    if 'repo' in config['data'] and config['data']['repo']:
        gvars['storage_path'] = config['data']['repo']

    gvars['remoterepo'] = False
    gvars['remote_host'] = ''
    gvars['remote_path'] = "/srv/http/appimage"
    if 'http' in gvars['storage_path']:
        gvars['remoterepo'] = True
        gvars['remote_host'] = "ciccio.libreitalia.org"
        if 'remote_host' in config['data'] and config['data']['remote_host']:
            gvars['remote_host'] = config['data']['remote_host']

        if 'remote_path' in config['data'] and config['data']['remote_path']:
            gvars['remote_path'] = config['data']['remote_path']

    gvars['sign'] = False
    if 'sign' in config['data'] and config['data']['sign']:
        gvars['sign'] = True

    # With the config file, we ignore all the command line options and set
    # generic default.
    for cbuild in config['builds']:
        # Loop a run for each build.
        collection = loaih.build.Collection(cbuild['query'])

        for obj in collection:
            # Configuration phase
            obj.verbose = verbose
            obj.language = 'basic'
            if 'language' in cbuild and cbuild['language']:
                obj.language = cbuild['language']
            obj.offline_help = False
            if 'offline_help' in cbuild and cbuild['offline_help']:
                obj.offline_help = cbuild['offline_help']
            obj.portable = False
            if 'portable' in cbuild and cbuild['portable']:
                obj.portable = cbuild['portable']
            obj.updatable = True
            obj.storage_path = gvars['storage_path']
            obj.download_path = gvars['download_path']
            obj.remoterepo = gvars['remoterepo']
            obj.remote_host = gvars['remote_host']
            obj.remote_path = gvars['remote_path']
            obj.sign = gvars['sign']

            # Build phase
            obj.calculate()
            if not gvars['force']:
                obj.check()
            obj.download()
            obj.build()
            obj.checksums()
            if obj.remoterepo and obj.appnamedir:
                obj.generalize_and_link(obj.appnamedir)
            obj.publish()
            if not obj.remoterepo:
                obj.generalize_and_link()
            del obj

    # In case prerelease or daily branches are used, cleanup the download
    # folder after finishing the complete run (to make sure the next run
    # will redownload all the needed files and is indeed fresh).
    # we will swipe all the builds inside a collection to understand the files
    # to delete.
    for cbuild in config['builds']:
        # Loop a run for each build.
        for build in loaih.build.Collection(cbuild['query']):

            if build.version.branch in {'prerelease', 'daily'}:
                build.version.cleanup_downloads(gvars['download_path'], verbose)
