#!/usr/bin/env python
# encoding: utf-8
"""machinery for compiling new versions of appimages."""

import datetime
import json
import re
import requests
import subprocess
import shlex
from lxml import html

# Constants
DOWNLOADPAGE = "https://www.libreoffice.org/download/download/"
ARCHIVE = "https://downloadarchive.documentfoundation.org/libreoffice/old/"
RELEASE = "https://download.documentfoundation.org/libreoffice/stable/"
DAILY = "https://dev-builds.libreoffice.org/daily/master/"
PRERELEASE = "https://dev-builds.libreoffice.org/pre-releases/deb/x86_64/"

SELECTORS = {
    'still': {
        'URL': DOWNLOADPAGE,
        'xpath': '(//span[@class="dl_version_number"])[last()]/text()'
    },
    'fresh': {
        'URL': DOWNLOADPAGE,
        'xpath': '(//span[@class="dl_version_number"])[1]/text()'
    },
    'prerelease': {
        'URL': DOWNLOADPAGE,
        'xpath': '//p[@class="lead_libre"][last()]/following-sibling::ul[last()]/li/a/text()'
    },
    'daily': {
        'URL': DAILY,
        'xpath': '//td/a'
    }
}


# Generic functions
def match_xpath(url: str, xpath: str):
    """Uses a couple of extensions to get results over webpage."""
    resource = requests.get(url, timeout=10)
    parsed = html.fromstring(resource.content)
    return parsed.xpath(xpath)


# Classes
class Version():
    """Represent the skeleton of each queried version."""

    def __init__(self):
        self.query = ''
        self.branch = ''
        self.version = ''
        self.urls = {
            'x86': '-',
            'x86_64': '-'
        }

    def appname(self):
        """Determines the app name based on the query branch determined."""
        datematch = re.match(r'[0-9]{8}', self.query)
        retval = 'LibreOffice'
        if self.query in {'prerelease', 'daily', 'current', 'yesterday'} or datematch:
            retval = 'LibreOfficeDev'

        return retval

    def cleanup_downloads(self, path, verbose=False) -> None:
        """Cleanups the downloads folder to assure new versions are built."""
        search_name = self.appname() + '_' + self.version
        cmd = f"find {path} -iname {search_name}\\*.tar.gz -delete"
        if verbose:
            subprocess.run(shlex.split(cmd), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.run(shlex.split(cmd))

    def to_dict(self):
        """Returns a dictionary of versions."""
        return {
            'query': self.query,
            'version': self.version,
            'basedirurl': self.urls
        }

    def to_json(self):
        """Returns a json representation of the version."""
        return json.dumps(self.to_dict())

    def __str__(self):
        return f"""query: {self.query}
version: {self.version}
x86: {self.urls['x86']}
x86_64: {self.urls['x86_64']}"""

class QueryError(Exception):
    """Standard exception for errors regarding queries."""


class Solver():
    """Generic solver to call others."""

    def __init__(self, text: str, default_to_current = False):
        self.text = text
        self.branch = text
        self.version = None
        self.default_to_current = default_to_current
        self.baseurl = ARCHIVE

    def solve(self):
        """Splits the query text possibilities, calling all the rest of the solvers."""

        solver = self
        if self.text in { 'current', 'yesterday', 'daily' }:
            solver = DailySolver(self.text, self.default_to_current)
        elif self.text in { 'still', 'fresh', 'prerelease' }:
            solver = NamedSolver(self.text)
        elif '.' in self.text:
            solver = NumberedSolver(self.text)
        else:
            try:
                int(self.text)
                solver = DailySolver(self.text, self.default_to_current)
            except ValueError:
                raise QueryError("The queried version does not exist.")

        self.version = solver.solve()
        self.baseurl = solver.baseurl
        return self.version

    def to_version(self):
        retval = Version()
        retval.query = self.text
        retval.branch = self.branch
        retval.version = self.version
        if retval.branch != 'daily' and retval.branch != 'prerelease':
            retval.urls['x86_64'] = self.baseurl + 'x86_64/'

            try:
                x86ver = match_xpath(self.baseurl + 'x86/', '//td/a/text()')
            except Exception:
                return retval

            if len(x86ver) > 1:
                retval.urls['x86'] = self.baseurl + 'x86/'
        else:
            retval.urls['x86_64'] = self.baseurl
        return retval

    @staticmethod
    def parse(text: str, default_to_current = False):
        """Calling the same as solver class."""
        retval = Solver(text, default_to_current)
        retval.solve()
        return retval.to_version()

class DailySolver(Solver):
    """Specific solver to daily queries."""

    def __init__(self, text: str, default_to_current = False):
        super().__init__(text, default_to_current)
        self.branch = 'daily'
        self.baseurl = DAILY

    def solve(self):
        """Get daily urls based on query."""
        x = "//td/a[starts-with(text(),'Linux-rpm_deb-x86') and contains(text(),'TDF/')]/text()"
        tinderbox_segment = match_xpath(self.baseurl, x)[-1]
        self.baseurl = self.baseurl + tinderbox_segment

        # Reiterate now to search for the dated version
        xpath_query = "//td/a/text()"
        daily_set = match_xpath(self.baseurl, xpath_query)

        matching = ''
        today = datetime.datetime.today()
        try:
            int(self.text)
            matching = datetime.datetime.strptime(self.text, "%Y%m%d").strftime('%Y-%m-%d')
        except ValueError:
            # All textual version
            if self.text in { 'current', 'daily' }:
                matching = 'current'
            elif self.text == 'yesterday':
                matching = (today + datetime.timedelta(days=-1)).strftime("%Y-%m-%d")

        results = sorted([ x for x in daily_set if matching in x ])
        if len(results) == 0:
            # No daily versions found.
            if self.default_to_current:
                solver = DailySolver('current')
                self.version = solver.version
                self.baseurl = solver.baseurl
        else:
            self.baseurl = self.baseurl + results[-1]

        # baseurl for x86 is not available for sure on daily builds.

        xpath_string = "//td/a[contains(text(), '_deb.tar.gz')]/text()"
        links = match_xpath(self.baseurl, xpath_string)
        if len(links) > 0:
            link = str(links[-1])
            self.version = link.rsplit('/', maxsplit=1)[-1].split('_')[1]

        return self.version


class NamedSolver(Solver):
    """Solves the query knowing that the input is a named query."""

    def __init__(self, text: str):
        super().__init__(text)
        self.branch = text
        self.baseurl = SELECTORS[self.text]['URL']
        self.generalver = ''

    def solve(self):
        """Get versions from query."""
        xpath_query = SELECTORS[self.text]['xpath']
        results = sorted(match_xpath(self.baseurl, xpath_query))

        if len(results) > 0:
            self.generalver = str(results[-1])

            result: str = self.generalver
            xpath_string = f"//td/a[starts-with(text(),'{result}')]/text()"
            archived_versions = sorted(match_xpath(ARCHIVE, xpath_string))

            if len(archived_versions) == 0:
                return self.version

            # Return just the last versions
            fullversion: str = str(archived_versions[-1])
            self.baseurl = ARCHIVE + fullversion + 'deb/'
            self.version = fullversion.rstrip('/')
            if self.branch == 'prerelease':
                self.baseurl = PRERELEASE

        return self.version


class NumberedSolver(Solver):
    """Specific solver for numbered versions."""

    def __init__(self, text: str):
        super().__init__(text)
        self.branch = '.'.join(text.split('.')[0-2])

    def solve(self):
        xpath_string = f"//td/a[starts-with(text(),'{self.text}')]/text()"
        versions = sorted(match_xpath(self.baseurl, xpath_string))
        if len(versions) == 0:
            # It is possible that in the ARCHIVE there's no such version (might be a prerelease)
            return self.version

        version = str(versions[-1])
        self.baseurl = self.baseurl + version + 'deb/'
        self.version = version.rstrip('/')

        return self.version
