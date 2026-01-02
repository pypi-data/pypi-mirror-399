#!/usr/bin/env python3
# encoding: utf-8
"""Classes and functions to build an AppImage."""

import os
import datetime
import glob
import subprocess
import shutil
import re
import shlex
import tempfile
import hashlib
import requests
import magic
import loaih


class Collection(list):
    """Aggregates metadata on a collection of builds."""

    def __init__(self, query, arch = ['x86', 'x86_64']):
        """Build a list of version to check/build for this round."""
        super().__init__()

        version = loaih.Solver.parse(query)

        # If a version is not buildable, discard it now!
        arch = [ x for x in arch if version.urls[x] != '-' ]
        self.extend([ Build(version, ar) for ar in arch ])

class BuildException(Exception): pass

class Build():
    """Builds a single version."""

    LANGSTD = [ 'ar', 'de', 'en-GB', 'es', 'fr', 'it', 'ja', 'ko', 'pt',
        'pt-BR', 'ru', 'zh-CN', 'zh-TW' ]
    LANGBASIC = [ 'en-GB' ]
    ARCHSTD = [ 'x86', 'x86_64' ]

    def __init__(self, version: loaih.Version, arch, debug=False):
        self.debug = debug
        self.version = version
        self.tidy_folder = True
        self.verbose = True
        self.check_dependencies = False
        self.arch = arch
        self.short_version = str.join('.', self.version.version.split('.')[0:2])
        self.branch_version = self.version.branch
        self.url = self.version.urls[arch]

        # Other default values - for structured builds
        # Most likely will be overridden by cli
        self.language = 'basic'
        self.offline_help = False
        self.portable = False
        self.updatable = True
        self.sign = True
        self.repo_type = 'local'
        self.remote_host = ''
        self.remote_path = ''
        self.storage_path = '/mnt/appimage'
        self.download_path = '/var/tmp/downloads'
        self.appnamedir = ''

        # Specific build version
        self.appname = self.version.appname()
        self.appversion = ''
        self.appimagedir = ''
        self.appimagefilename = ''
        self.zsyncfilename = ''

        # Other variables by build
        self.languagepart = '.' + self.language
        self.helppart = ''

        # Creating a tempfile
        self.builddir = tempfile.mkdtemp()
        self.tarballs = {}
        self.found = False
        self.built = False

        # Preparing the default for the relative path on the storage for
        # different versions.
        # The path will evaluated as part of the check() function, as it is
        # understood the storage_path can be changed before that phase.
        self.relative_path = []
        self.full_path = ''
        self.baseurl = ''


    def calculate(self):
        """Calculate exclusions and other variables."""

        if self.verbose:
            print("--- Preliminary Phase ---")

        if self.debug and isinstance(shutil.which('apt'), str):
            # APT is found in path. We assume we can find dependencies.
            self.check_dependencies = True


            if self.verbose:
                print("Updating system packages cache.")
            # Updating package cache
            subprocess.run(['sudo', 'apt', 'update'], check=True, stdout=subprocess.DEVNULL)
            if self.verbose:
                print("Ensuring apt-file is installed and updated.")
            # Updating apt-file cache
            subprocess.run(['sudo', 'apt', 'install', 'apt-file', '-y'], check=True, stdout=subprocess.DEVNULL)
            subprocess.run(['sudo', 'apt-file', 'update'], check=True, stdout=subprocess.DEVNULL)
        else:
            print("CAUTION: your system seems not to include a working version of apt.\nThis will cause the AppImage to leverage system libraries when run.")
            self.check_dependencies = False

        if self.verbose:
            print("--- Calculate Phase ---")

        # let's check here if we are on a remote repo or local.
        if self.storage_path.startswith("http"):
            # Final repository is remote
            self.repo_type = 'remote'
            if self.verbose:
                print("Repo is remote.")
        else:
            self.repo_type = 'local'
            if self.verbose:
                print("Repo is local.")

        # Calculating languagepart
        self.languagepart = "."
        if ',' in self.language:
            self.languagepart += self.language.replace(',', '-')
        else:
            self.languagepart += self.language

        # Calculating help part
        if self.offline_help:
            self.helppart = '.help'

        # Building the required names
        self.appimagefilename = self.__gen_appimagefilename__()
        self.zsyncfilename = self.appimagefilename + '.zsync'

        # Mandate to the private function to calculate the full_path available
        # for the storage and the checks.
        self.__calculate_full_path__()


    def check(self):
        """Checking if the requested AppImage has been already built."""

        if self.branch_version == 'daily':
            # Daily versions have to be downloaded and built each time; no
            # matter if another one is already present.
            return

        if self.verbose:
            print("--- Check Phase ---")

        if len(self.appimagefilename) == 0:
            self.calculate()

        if self.verbose:
            print(f"Searching for {self.appimagefilename}")

        # First, check if by metadata the repo is remote or not.
        if self.repo_type == 'remote':
            # Remote storage. I have to query a remote site to know if it
            # was already built.
            name = self.appimagefilename
            url = self.storage_path.rstrip('/') + self.full_path + '/'
            try:
                if len(loaih.match_xpath(url, f"//a[contains(@href,'{name}')]/@href")) > 0:
                    # Already built.
                    self.found = True

            except Exception:
                # The URL specified do not exist. So it is to build.
                self.found = False

        else:
            # Repo is local
            command = f"find {self.full_path} -name {self.appimagefilename}"
            res = subprocess.run(shlex.split(command),
                capture_output=True,
                env={ "LC_ALL": "C" },
                text=True, encoding='utf-8', check=True)

            if res.stdout and len(res.stdout.strip("\n")) > 0:
                # All good, the command was executed fine.
                self.found = True

        if self.found:
            if self.verbose:
                print(f"Found requested AppImage: {self.appimagefilename}.")


    def download(self, compact=False):
        """Downloads the contents of the URL as it was a folder."""

        if self.verbose:
            print("--- Download Phase ---")

        if self.found:
            return

        if self.verbose:
            print(f"Started downloads for {self.version.version}. Please wait.")

        # Checking if a valid path has been provided
        if self.url == '-':
            if self.verbose:
                print(f"Cannot build for arch {self.arch}. Continuing with other arches.")
            # Faking already built it so to skip other checks.
            self.found = True

        # Identifying downloads
        self.tarballs = [ x for x in loaih.match_xpath(self.url, "//td/a/text()") if x.endswith('tar.gz') and 'deb' in x and self.version.version in x ]

        self.download_tarballs = []

        # Issue #5: manage a limited number of downloads and not the full set.
        if compact:
            self.download_tarballs = self.__select_tarballs__()
        else:
            self.download_tarballs = self.tarballs

        # Create and change directory to the download location
        os.makedirs(self.download_path, exist_ok = True)
        os.chdir(self.download_path)
        for archive in self.download_tarballs:
            # If the archive is already there, do not do anything.
            if os.path.exists(archive):
                continue

            # Download the archive
            try:
                self.__download_archive_debug__(archive)
            except Exception as error:
                print(f"Failed to download {archive}: {error}.")

        if self.verbose:
            print(f"Finished downloads for {self.version.version}.")


    def build(self):
        """Building all the versions."""

        if self.found:
            return

        if self.verbose:
            print("--- Building Phase ---")

        # Preparation tasks
        self.appnamedir = os.path.join(self.builddir, self.appname)
        os.makedirs(self.appnamedir, exist_ok=True)
        # And then cd to the appname folder.
        os.chdir(self.appnamedir)
        # Download appimagetool from github
        appimagetoolurl = r"https://github.com/AppImage/AppImageKit/releases/"
        appimagetoolurl += f"download/continuous/appimagetool-{self.arch}.AppImage"
        self.__download__(appimagetoolurl, 'appimagetool')
        os.chmod('appimagetool', 0o755)

        # Build the requested version.
        self.__unpackbuild__()
        self.__prepare_contents__()
        if self.check_dependencies:
            if self.verbose:
                print("Searching for dependent libraries, it might take a while.")

            self.__missing_dependencies__()
        self.__finalize_build__()


    def checksums(self):
        """Create checksums of the built versions."""
        # Skip checksum if initally the build was already found in the storage directory

        if self.verbose:
            print("--- Checksum Phase ---")

        if self.found:
            return

        os.chdir(self.appnamedir)
        if self.built:
            for item in [ self.appimagefilename, self.zsyncfilename ]:
                itempath = os.path.join(self.appnamedir, item)
                if os.path.exists(itempath):
                    self.__create_checksum__(item)


    def publish(self):
        """Moves built versions to definitive storage."""

        if self.verbose:
            print("--- Publish Phase ---")

        if self.found:
            # All files are already present in the full_path
            return

        os.chdir(self.appnamedir)
        # Two cases here: local and remote storage_path.
        if self.repo_type == 'remote':
            # Remote first.
            # Build destination directory
            remotepath = self.remote_path.rstrip('/') + self.full_path
            try:
                if self.verbose:
                    subprocess.run(
                        r"rsync -rlIvz --munge-links *.AppImage* " +
                        f"{self.remote_host}:{remotepath}",
                        cwd=self.appnamedir, shell=True, check=True
                    )
                else:
                    subprocess.run(
                        r"rsync -rlIvz --munge-links *.AppImage* " +
                        f"{self.remote_host}:{remotepath}",
                        cwd=self.appnamedir, shell=True, check=True,
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                    )
            finally:
                pass

        else:
            # Local
            # Forcing creation of subfolders, in case there is a new build
            os.makedirs(self.full_path, exist_ok = True)
            for file in glob.glob("*.AppImage*"):
                subprocess.run(shlex.split(
                    f"cp -f {file} {self.full_path}"
                ), check=True)


    def generalize_and_link(self, chdir = 'default'):
        """Creates the needed generalized files if needed."""

        if self.verbose:
            print("--- Generalize and Link Phase ---")

        # If called with a pointed version, no generalize and link necessary.
        if not self.branch_version:
            return

        # If a prerelease or a daily version, either.
        if self.version.query in { 'daily', 'prerelease' }:
            return

        if chdir == 'default':
            chdir = self.full_path

        appimagefilename = r''
        zsyncfilename = r''

        # Creating versions for short version and query text
        versions = [ self.short_version, self.branch_version ]

        os.chdir(chdir)
        # if the appimage for the reported arch is not found, skip to next
        # arch
        if not os.path.exists(self.appimagefilename):
            return

        # Doing it both for short_name and for branchname
        for version in versions:
            appimagefilename = f"{self.appname}-{version}"
            appimagefilename += f"{self.languagepart}{self.helppart}"
            appimagefilename += f'-{self.arch}.AppImage'
            zsyncfilename = appimagefilename + '.zsync'

            # Create the symlink
            if self.verbose:
                print(f"Creating {appimagefilename} and checksums.")
            if os.path.exists(appimagefilename):
                os.unlink(appimagefilename)
            os.symlink(self.appimagefilename, appimagefilename)
            # Create the checksum for the AppImage
            self.__create_checksum__(appimagefilename)
            # Do not continue if no zsync file is provided.
            if not self.updatable:
                continue

            if self.verbose:
                print(f"Creating zsync file for version {version}.")
            if os.path.exists(zsyncfilename):
                os.unlink(zsyncfilename)
            shutil.copyfile(self.zsyncfilename, zsyncfilename)
            # Editing the zsyncfile
            subprocess.run(shlex.split(
                r"sed --in-place 's/^Filename:.*$/Filename: " +
                f"{appimagefilename}/' {zsyncfilename}"
            ), check=True)
            self.__create_checksum__(zsyncfilename)

    ### Private methods ###

    def __gen_appimagefilename__(self):
        """Generalize the construction of the name of the app."""
        self.appversion = self.version.version + self.languagepart + self.helppart
        return self.appname + f'-{self.appversion}-{self.arch}.AppImage'


    def __calculate_full_path__(self):
        """Calculate relative path of the build, based on internal other variables."""
        if len(self.relative_path) == 0:
            if self.tidy_folder:
                if self.branch_version == 'daily':
                    self.relative_path.append('daily')
                elif self.branch_version == 'prerelease':
                    self.relative_path.append('prerelease')

                # Not the same check, an additional one
                if self.portable:
                    self.relative_path.append('portable')

        # Fullpath might be intended two ways:
        if self.repo_type == 'remote':
            # Repository is remote
            # we build full_path as it is absolute to the root of the
            # storage_path.
            self.full_path = '/'
            if len(self.relative_path) >= 1:
                self.full_path += str.join('/', self.relative_path)
        else:
            # Repository is local
            # If it is remote or if it is local
            fullpath_arr = self.storage_path.split('/')
            # Joining relative path only if it is not null
            if len(self.relative_path) > 0:
                fullpath_arr.extend(self.relative_path)
            self.full_path = re.sub(r"/+", '/', str.join('/', fullpath_arr))

            if not os.path.exists(self.full_path):
                os.makedirs(self.full_path, exist_ok = True)

    def __create_checksum__(self, file):
        """Internal function to create checksum file."""

        retval = hashlib.md5()
        with open(file, 'rb') as rawfile:
            while True:
                buf = rawfile.read(2**20)
                if not buf:
                    break

                retval.update(buf)

        with open(f"{file}.md5", 'w', encoding='utf-8') as checkfile:
            checkfile.write(f"{retval.hexdigest()}  {os.path.basename(file)}")

    def __download_archive__(self, archive) -> str:
        return self.__download__(self.url, archive)

    def __download_archive_debug__(self, archive) -> str:
        """Analyses the downloaded archive to prevent issues with unpacking."""
        break_control = 0
        testedfilename = ""
        while break_control <= 5:
            timenow = datetime.datetime.now()
            testedfilename, resource = self.__download_debug__(self.url, archive)
            mime = magic.Magic(mime=True)
            mimetype = mime.from_file(testedfilename)
            if mimetype == 'application/gzip':
                return testedfilename

            # On the contrary, we will dump a logfile, remove the download and
            # redo the download.
            with open(os.path.join(self.download_path, 'downloadfailure.log'), 'a') as logfile:
                logfile.write(f"{timenow.isoformat()};{resource.url};{mimetype}\n")

            os.unlink(testedfilename)
            break_control += 1

        # If it arrives here, 5 attempts to download the archive have failed.
        raise BuildException(f"All downloads failed for {archive}. Exiting.")


    def __download__(self, url: str, filename: str):
        basename = filename
        if '/' in filename:
            basename = filename.split('/')[-1]

        full_url = url
        if url.endswith('/'):
            # URL has to be completed with basename of filename
            full_url = url + basename

        with requests.get(full_url, stream=True, timeout=10) as resource:
            resource.raise_for_status()
            with open(filename, 'wb') as file:
                for chunk in resource.iter_content(chunk_size=8192):
                    file.write(chunk)
        return filename

    def __download_debug__(self, url: str, filename: str) -> tuple[str, requests.Response]:
        basename = filename
        if '/' in filename:
            basename = filename.split('/')[-1]

        full_url = url
        if url.endswith('/'):
            # URL has to be completed with basename of filename
            full_url = url + basename

        with requests.get(full_url, stream=True, timeout=10) as resource:
            resource.raise_for_status()
            with open(filename, 'wb') as file:
                for chunk in resource.iter_content(chunk_size=8192):
                    file.write(chunk)
        return filename, resource

    def __select_tarballs__(self):
        retval = [ self.tarballs[0] ]

        # Let's process standard languages and append results to the
        # buildtarball
        if self.language == 'basic':
            if self.offline_help:
                retval.extend([ x for x in self.tarballs if 'pack_en-GB' in x ])
            else:
                retval.extend([ x for x in self.tarballs if 'langpack_en-GB' in x])
        elif self.language == 'standard':
            for lang in Build.LANGSTD:
                if self.offline_help:
                    retval.extend([ x for x in self.tarballs if 'pack_' + lang in x ])
                else:
                    retval.extend([ x for x in self.tarballs if 'langpack_' + lang in x ])
        elif self.language == 'full':
            if self.offline_help:
                # We need also all help. Let's replace buildtarball with the
                # whole bunch
                retval = self.tarballs
            else:
                retval.extend([ x for x in self.tarballs if 'langpack' in x ])
        else:
            # Looping for each language in self.language
            for lang in self.language.split(","):
                if self.offline_help:
                    retval.extend([ x for x in self.tarballs
                        if 'pack' + lang in x ])
                else:
                    retval.extend([ x for x in self.tarballs
                        if 'langpack' + lang in x ])

        return retval


    def __unpackbuild__(self):
        # We start by filtering out tarballs from the list
        buildtarballs = self.__select_tarballs__()

        os.chdir(self.appnamedir)

        # Unpacking the tarballs
        if self.verbose:
            print("---- Unpacking ----")

        for archive in buildtarballs:
            subprocess.run(shlex.split(
                f"tar xzf {self.download_path}/{archive}"), check=True)

    def __prepare_contents__(self):
        # create appimagedir
        if self.verbose:
            print("---- Preparing the build ----")
        self.appimagedir = os.path.join(self.appnamedir, self.appname + '.AppDir')
        os.makedirs(self.appimagedir, exist_ok = True)

        # At this point, let's decompress the deb packages
        if self.verbose:
            print("Unpacking main archives")

        subprocess.run(shlex.split(
            r"find .. -iname '*.deb' -exec dpkg -x {} . \;"
        ), cwd=self.appimagedir, check=True)

        if self.portable:
            subprocess.run(shlex.split(
                r"find . -type f -iname 'bootstraprc' " +
                r"-exec sed -i 's|^UserInstallation=.*|" +
                r"UserInstallation=\$SYSUSERCONFIG/libreoffice/%s|g' {} \+" % self.short_version
            ), cwd=self.appimagedir, check=True)

        # Changing desktop file
        if self.verbose:
            print("Preparing .desktop file.")

        subprocess.run(shlex.split(
            r"find . -iname startcenter.desktop -exec cp {} . \;"
        ), cwd=self.appimagedir, check=True)

        subprocess.run(shlex.split(
            f"sed --in-place \'s:^Name=.*$:Name={self.appname}:\' " +
            r"startcenter.desktop"
        ), cwd=self.appimagedir, check=False)

        if self.verbose:
            print("Preparing icon file.")
        subprocess.run(shlex.split(
            r"find . -name '*startcenter.png' -path '*hicolor*48x48*' " +
            r"-exec cp {} . \;"
        ), cwd=self.appimagedir, check=True)

        # Finding path to main executable
        cmd = subprocess.run(shlex.split(
            r"find -iname soffice.bin -print"
        ), cwd=self.appimagedir, check = True, capture_output=True)
        self.main_executable = os.path.abspath(os.path.join(
            self.appimagedir, 
            cmd.stdout.strip().decode('utf-8')))

        # Find the name of the binary called in the desktop file.
        binaryname = ''
        with open(
            os.path.join(self.appimagedir, 'startcenter.desktop'),
            'r', encoding="utf-8"
        ) as desktopfile:
            for line in desktopfile.readlines():
                if re.match(r'^Exec', line):
                    binaryname = line.split('=')[-1].split(' ')[0]
                    # Esci al primo match
                    break
    
        #binary_exec = subprocess.run(shlex.split(r"awk 'BEGIN { FS = \"=\" } /^Exec/ { print $2; exit }' startcenter.desktop | awk '{ print $1 }'"), cwd=self.appimagedir, text=True, encoding='utf-8')
        #binaryname = binary_exec.stdout.strip("\n")
    
        # Creating a soft link so the executable in the desktop file is present
        bindir=os.path.join(self.appimagedir, 'usr', 'bin')
        os.makedirs(bindir, exist_ok = True)
        subprocess.run(shlex.split(
            r"find ../../opt -iname soffice.bin -path '*program*' " +
            r"-exec ln -sf {} ./%s \;" % binaryname
        ), cwd=bindir, check=True)

    def __missing_dependencies__(self):
        """Finds and copy in the appimagedir any missing libraries."""
        # If the system permits it, we leverage lddcollect
        # to find the packages that contain .so dependencies in the main build.
        import lddcollect
        # We first process the ELF
        raw = lddcollect.process_elf(self.main_executable, verbose = False, dpkg = True)

        # If all works as expected, we obtain a tuple of:
        # (debian_packages, all_libraries, files_not_found)
        debian_packages = raw[0]
        not_found = raw[2]

        if len(debian_packages) != 0:
            # Creating temporary folders
            debs = [ x.split(':')[0] for x in debian_packages ]
            downloadpath = os.path.abspath(os.path.join(self.builddir, 'dependencies'))
            os.makedirs(downloadpath)
            

            if self.verbose:
                print("Downloading missing dependencies, please wait.")

            # Let's try to find and install also other libraries
            additional = list(dict.fromkeys([ Helpers.lib_to_deb(x) for x in not_found ]))
            debs.extend(additional)

            # It seems the download command does not download dependencies of
            # the packages.
            if self.verbose:
                print("Constructing the dependency tree.")

            for deb in debian_packages:
                debs.extend(Helpers.deb_dependencies(deb))

            # Re-cleaning up the dependency tree
            debs = list(dict.fromkeys(debs))

            # We download the missing dependencies leveraging apt
            subprocess.run(shlex.split(
                r"apt download " + " ".join(debs)
            ), cwd=downloadpath, check=True)

            # then we install them inside a temporary path
            temporary = os.path.abspath(os.path.join(downloadpath, 'temp'))
            os.makedirs(temporary)
            subprocess.run(shlex.split(
                r"find " + downloadpath + r" -iname \*.deb -exec dpkg -x {} " + temporary + r" \;"
            ), cwd=self.builddir, check=True)

            # We are finally copying the .so files in the same path as main_executable
            libdirs = [ 'lib/x86_64-linux-gnu', 'usr/lib/x86_64-linux-gnu' ]
            for libdir in libdirs:
                fulllibdir = os.path.abspath(os.path.join(temporary, libdir))
                subprocess.run(shlex.split(
                    f"cp -Ra {fulllibdir}/. {os.path.dirname(self.main_executable)}/"
                ), cwd=temporary, check=True)

            if self.debug:
                with open(os.path.abspath(os.path.join(self.storage_path, 'dependencies.lst')), 'w', encoding="utf-8") as deplist:
                    deplist.write("\n".join(debs))

    def __finalize_build__(self):
        if self.verbose:
            print("Finalizing build...")
        # Cleaning up AppDir
        cleanup_dirs = [ 'etc', 'lib', 'lib64', 'usr/lib', 'usr/local' ]
        for local in cleanup_dirs:
            shutil.rmtree(os.path.abspath(os.path.join(self.appimagedir, local)), ignore_errors=True)
    
        # Download AppRun from github
        apprunurl = r"https://github.com/AppImage/AppImageKit/releases/"
        apprunurl += f"download/continuous/AppRun-{self.arch}"
        dest = os.path.join(self.appimagedir, 'AppRun')
        self.__download__(apprunurl, dest)
        os.chmod(dest, 0o755)
    
        # Dealing with extra options
        buildopts = []
        if self.sign:
            buildopts.append('--sign')
    
        # adding zsync build if updatable
        if self.updatable:
            buildopts.append(f"-u 'zsync|{self.zsyncfilename}'")
    
        buildopts_str = str.join(' ', buildopts)
    
        # Build the number-specific build
        if self.verbose:
            print("---- Start building ----")
            subprocess.run(shlex.split(
                f"{self.appnamedir}/appimagetool {buildopts_str} -v " +
                f"{self.appimagedir}"
            ), env={ "VERSION": self.appversion }, check=True)
            print("---- End building ----")
        else:
            subprocess.run(shlex.split(
                f"{self.appnamedir}/appimagetool {buildopts_str} -v " +
                f"{self.appimagedir}"
            ), env={ "VERSION": self.appversion }, stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL, check=True)
    
        if self.verbose:
            print(f"Built AppImage version {self.appversion}")
    
        # Cleanup phase, before new run.
        for deb in glob.glob(self.appnamedir + '/*.deb'):
            os.remove(deb)
        subprocess.run(shlex.split(
            r"find . -mindepth 1 -maxdepth 1 -type d -exec rm -rf {} \+"
        ), check=True)
    
        self.built = True

    def __del__(self):
        """Destructor"""
        if not self.debug:
            # Cleaning up build directory
            shutil.rmtree(self.builddir)


class Helpers:

    @staticmethod
    def deb_dependencies(package_name):
        """Returns the array of the dependencies of that package."""

        # First pass: find dependency of that package in raw output
        pass1 = subprocess.Popen(shlex.split(
            f"apt-cache depends --recurse --no-recommends --no-suggests --no-conflicts --no-breaks --no-replaces --no-enhances --no-pre-depends {package_name}"
        ), stdout=subprocess.PIPE)

        # Second pass: only grep interesting lines.
        pass2 = subprocess.Popen(shlex.split(
            r"grep '^\w'"
        ), stdin=pass1.stdout, stdout=subprocess.PIPE, encoding='utf-8')
        stdout = pass2.communicate()[0]

        return stdout.strip().split("\n")

    @staticmethod
    def lib_to_deb(libraryname):
        """Uses system tools to identify the missing package."""

        libsearch = subprocess.run(shlex.split(
            f"sudo apt-file find -lx {libraryname}$"
        ), check=True, capture_output=True)
        candidate = [ x for x in libsearch.stdout.decode('utf-8').split('\n') if 'lib' in x ][0]
        return candidate
