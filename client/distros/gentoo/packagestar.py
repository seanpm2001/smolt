# smolt - Fedora hardware profiler
#
# Copyright (C) 2009 Sebastian Pipping <sebastian@pipping.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301, USA.

from collections import defaultdict
import os
import portage
from overlays import Overlays

class _PackageStar:
    def __init__(self):
        pass

    def _init(self, section, privacy_filter):
        self._section = section
        self._privacy_filter = privacy_filter
        self._collect()

    def _locations(self):
        return [os.path.join(
            portage.settings["PORTAGE_CONFIGROOT"],
            portage.USER_CONFIG_PATH.lstrip(os.path.sep))]

    def _collect(self):
        self._cp_to_atoms = defaultdict(list)
        self._total_count = 0
        self._secret_count = 0
        for location in self._locations():
            for x in portage.grabfile_package(
                    os.path.join(location, self._section), recursive = 1):
                self._total_count = self._total_count + 1
                cp = portage.dep_getkey(x)
                if self._privacy_filter and Overlays().is_secret_package(cp):
                    self._secret_count = self._secret_count + 1
                    continue
                merge_with = set([x])
                if cp in self._cp_to_atoms:
                    self._cp_to_atoms[cp] = self._cp_to_atoms[cp].union(merge_with)
                else:
                    self._cp_to_atoms[cp] = merge_with

    def total_count(self):
        return self._total_count

    def secret_count(self):
        return self._secret_count

    def known_count(self):
        return self.total_count() - self.secret_count()

    def hits(self, cpv):
        cp = portage.dep_getkey(cpv)
        if cp not in self._cp_to_atoms:
            return False
        test_atom = '=' + cpv
        for a in self._cp_to_atoms[cp]:
            if portage.dep.get_operator(a) == None:
                return True
            elif not not portage.dep.match_from_list(test_atom, [a]):
                return True
        return False

    def dump(self):
        print '%s:' % (self._section)
        for k, v in self._cp_to_atoms.items():
            print '  %s: %s' % (k, v)
        print
        print '  Total: ' + str(self.total_count())
        print '    Known: ' + str(self.known_count())
        print '    Secret: ' + str(self.secret_count())
        print


class _PackageMask(_PackageStar):
    def __init__(self):
        self._init('package.mask', privacy_filter=True)


class _PackageUnmask(_PackageStar):
    def __init__(self):
        self._init('package.unmask', privacy_filter=True)


class _ProfilePackageMask(_PackageStar):
    def __init__(self):
        self._init('package.mask', privacy_filter=False)

    def _locations(self):
        main_tree_profiles = [os.path.join(portage.settings["PORTDIR"],
            "profiles")] + portage.settings.profiles # TODO break potential
        overlay_profiles = [os.path.join(e, "profiles") for e in \
            portage.settings["PORTDIR_OVERLAY"].split()]
        return[e for e in main_tree_profiles + overlay_profiles if \
            os.path.isdir(e)]


_package_unmask_instance = None
def PackageUnmask():
    """
    Simple singleton wrapper around _PackageUnmask class
    """
    global _package_unmask_instance
    if _package_unmask_instance == None:
        _package_unmask_instance = _PackageUnmask()
    return _package_unmask_instance


_package_mask_instance = None
def PackageMask():
    """
    Simple singleton wrapper around _PackageMask class
    """
    global _package_mask_instance
    if _package_mask_instance == None:
        _package_mask_instance = _PackageMask()
    return _package_mask_instance


_profile_package_mask_instance = None
def ProfilePackageMask():
    """
    Simple singleton wrapper around _ProfilePackageMask class
    """
    global _profile_package_mask_instance
    if _profile_package_mask_instance == None:
        _profile_package_mask_instance = _ProfilePackageMask()
    return _profile_package_mask_instance


if __name__ == '__main__':
    package_mask = PackageMask()
    package_mask.dump()
    package_unmask = PackageUnmask()
    package_unmask.dump()
    profile_package_mask = ProfilePackageMask()
    profile_package_mask.dump()
