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

from playmodel import *
from playmodel import _gentoo_distfiles_mirrors_table, _gentoo_mirror_pool_table
from playmodel import _gentoo_accept_keywords_table, _gentoo_keyword_pool_table
from playmodel import _gentoo_features_table, _gentoo_feature_pool_table
from playmodel import _gentoo_global_use_flags_table, _gentoo_use_flag_pool_table
from playmodel import _gentoo_sync_mirror_table, _gentoo_mirror_pool_table
from playmodel import _gentoo_system_profile_table, _gentoo_system_profile_pool_table
from playmodel import _gentoo_chost_table, _gentoo_chost_pool_table
from playmodel import _gentoo_call_flag_table, _gentoo_call_flag_pool_table
import datetime
import sqlalchemy
from sqlalchemy.sql import func, select, join, and_


_MAX_DISTFILES_MIRRORS = 30
_MAX_FEATURES = 30
_MAX_GLOBAL_USE_FLAGS = 100
_MAX_SYNC_MIRRORS = 30
_MAX_SYSTEM_PROFILE = 30
_MAX_CHOST = 30
_MAX_CALL_FLAGS = 30


class GentooReporter:
    def __init__(self, session):
        self.session = session
        self.gentoo_machines = 1
        self._data = {}

    def _relative(self, absolute, post_dot_digits=1):
        return round(absolute * 100.0 / self.gentoo_machines, post_dot_digits)

    def _analyze_archs(self):
        # TODO use different type of join?
        def make_row(absolute_stable, absolute_unstable, absolute_total, label=None):
            res = {
                'absolute_stable':absolute_stable,
                'absolute_unstable':absolute_unstable,
                'absolute_total':absolute_total,
                'relative_stable':self._relative(absolute_stable),
                'relative_unstable':self._relative(absolute_unstable),
                'relative_total':self._relative(absolute_total),
            }
            if label != None:
                res['label'] = label
            return res

        columns = [GentooKeywordString.name, func.count(GentooAcceptKeywordRel.machine_id), func.sum(GentooAcceptKeywordRel.stable)]
        pool_join = _gentoo_accept_keywords_table.join(_gentoo_keyword_pool_table)
        arch_join_condition = and_(GentooArchRel.keyword_id == GentooAcceptKeywordRel.keyword_id,\
                GentooArchRel.machine_id == GentooAcceptKeywordRel.machine_id)
        query = select(columns, from_obj=[pool_join]).where(arch_join_condition).\
                group_by(GentooArchRel.keyword_id).order_by(\
                func.count(GentooAcceptKeywordRel.machine_id).desc())
        total_stable = 0
        total_unstable = 0
        total_total = 0
        final_rows = []
        for i in query.execute().fetchall():
            label, total, stable = i
            stable = long(stable)
            unstable = total - stable
            if unstable < 0:
                unstable = 0

            total_stable = total_stable + stable
            total_unstable = total_unstable + unstable
            total_total = total_total + total

            final_rows.append(make_row(total_stable, total_unstable, total_total, label))

        res = {
            'listed':final_rows,
            'total':[make_row(total_stable, total_unstable, total_total)],
        }
        return res

    def _analyze_simple_stuff(self):
        def make_row(absolute, post_dot_digits, label=None):
            res = {
                'absolute':absolute,
                'relative':self._relative(absolute, post_dot_digits),
            }
            if label != None:
                res['label'] = label
            return res

        jobs = [
            {'_SECTION':'distfiles_mirrors',
                '_POOL_TABLE_OBJECT':_gentoo_mirror_pool_table,
                '_REL_TABLE_OBJECT':_gentoo_distfiles_mirrors_table,
                '_REL_CLASS_OBJECT':GentooDistfilesMirrorRel,
                '_POOL_CLASS_OBJECT':GentooMirrorString,
                '_DISPLAY_LIMIT':_MAX_DISTFILES_MIRRORS,
                '_FOREIGN_COLUMN_NAME':'mirror_id'},
            {'_SECTION':'features',
                '_POOL_TABLE_OBJECT':_gentoo_feature_pool_table,
                '_REL_TABLE_OBJECT':_gentoo_features_table,
                '_REL_CLASS_OBJECT':GentooFeatureRel,
                '_POOL_CLASS_OBJECT':GentooFeatureString,
                '_DISPLAY_LIMIT':_MAX_FEATURES,
                '_FOREIGN_COLUMN_NAME':'feature_id'},
            {'_SECTION':'global_use_flags',
                '_POOL_TABLE_OBJECT':_gentoo_use_flag_pool_table,
                '_REL_TABLE_OBJECT':_gentoo_global_use_flags_table,
                '_REL_CLASS_OBJECT':GentooGlobalUseFlagRel,
                '_POOL_CLASS_OBJECT':GentooUseFlagString,
                '_DISPLAY_LIMIT':_MAX_GLOBAL_USE_FLAGS,
                '_FOREIGN_COLUMN_NAME':'use_flag_id'},
            {'_SECTION':'sync_mirror',
                '_POOL_TABLE_OBJECT':_gentoo_mirror_pool_table,
                '_REL_TABLE_OBJECT':_gentoo_sync_mirror_table,
                '_REL_CLASS_OBJECT':GentooSyncMirrorRel,
                '_POOL_CLASS_OBJECT':GentooMirrorString,
                '_DISPLAY_LIMIT':_MAX_SYNC_MIRRORS,
                '_FOREIGN_COLUMN_NAME':'mirror_id'},
            {'_SECTION':'system_profile',
                '_POOL_TABLE_OBJECT':_gentoo_system_profile_pool_table,
                '_REL_TABLE_OBJECT':_gentoo_system_profile_table,
                '_REL_CLASS_OBJECT':GentooSystemProfileRel,
                '_POOL_CLASS_OBJECT':GentooSystemProfileString,
                '_DISPLAY_LIMIT':_MAX_SYSTEM_PROFILE,
                '_FOREIGN_COLUMN_NAME':'system_profile_id'},
            {'_SECTION':'chost',
                '_POOL_TABLE_OBJECT':_gentoo_chost_pool_table,
                '_REL_TABLE_OBJECT':_gentoo_chost_table,
                '_REL_CLASS_OBJECT':GentooChostRel,
                '_POOL_CLASS_OBJECT':GentooChostString,
                '_DISPLAY_LIMIT':_MAX_CHOST,
                '_FOREIGN_COLUMN_NAME':'chost_id'},
        ]

        res = {}
        for j in jobs:
            _SECTION = j['_SECTION']
            _POOL_TABLE_OBJECT = j['_POOL_TABLE_OBJECT']
            _REL_TABLE_OBJECT = j['_REL_TABLE_OBJECT']
            _REL_CLASS_OBJECT = j['_REL_CLASS_OBJECT']
            _POOL_CLASS_OBJECT = j['_POOL_CLASS_OBJECT']
            _DISPLAY_LIMIT = j['_DISPLAY_LIMIT']
            _FOREIGN_COLUMN_NAME = j['_FOREIGN_COLUMN_NAME']

            pool_join = _REL_TABLE_OBJECT.join(_POOL_TABLE_OBJECT)
            total_entry_count = self.session.query(_REL_CLASS_OBJECT).count()
            query = select([_POOL_CLASS_OBJECT.name, func.count(_REL_CLASS_OBJECT.machine_id)], \
                    from_obj=[pool_join]).group_by(getattr(_REL_CLASS_OBJECT, _FOREIGN_COLUMN_NAME)).order_by(\
                    func.count(_REL_CLASS_OBJECT.machine_id).desc(), _POOL_CLASS_OBJECT.name).limit(_DISPLAY_LIMIT)
            if _DISPLAY_LIMIT >= 50:
                post_dot_digits = 2
            else:
                post_dot_digits = 1

            final_rows = []
            others = total_entry_count
            for i in query.execute().fetchall():
                label, absolute = i
                others = others - absolute
                final_rows.append(make_row(absolute, post_dot_digits, label))
            if others < 0:
                others = 0

            res[_SECTION] = {
                'listed':final_rows,
                'others':[make_row(others, post_dot_digits)],
                'total':[make_row(total_entry_count, post_dot_digits)],
            }
        return res

    def _analyzes_compile_flags(self):
        def make_row(absolute, post_dot_digits, label=None):
            res = {
                'absolute':absolute,
                'relative':self._relative(absolute, post_dot_digits),
            }
            if label != None:
                res['label'] = label
            return res

        res = {}
        for call_flag_class in ('CFLAGS', 'CXXFLAGS', 'LDFLAGS', 'MAKEOPTS'):
            try:
                call_flag_class_object = self.session.query(GentooCallFlagClassString).filter_by(name=call_flag_class).one()
            except sqlalchemy.orm.exc.NoResultFound:
                # TODO
                raise
            call_flag_class_id = call_flag_class_object.id

            pool_join = _gentoo_call_flag_table.join(_gentoo_call_flag_pool_table)
            total_entry_count = self.session.query(GentooCallFlagRel).filter_by(call_flag_class_id=call_flag_class_id).count()
            query = select([GentooCallFlagString.name, func.count(GentooCallFlagRel.machine_id)], \
                    from_obj=[pool_join]).where(GentooCallFlagRel.call_flag_class_id == call_flag_class_id).\
                    group_by(GentooCallFlagRel.call_flag_id).order_by(\
                    func.count(GentooCallFlagRel.machine_id).desc(), GentooCallFlagString.name).limit(_MAX_CALL_FLAGS)
            if _MAX_CALL_FLAGS >= 50:
                post_dot_digits = 2
            else:
                post_dot_digits = 1

            final_rows = []
            others = total_entry_count
            for i in query.execute().fetchall():
                label, absolute = i
                others = others - absolute
                final_rows.append(make_row(absolute, post_dot_digits, label))
            if others < 0:
                others = 0

            res[call_flag_class] = {
                'listed':final_rows,
                'others':[make_row(others, post_dot_digits)],
                'total':[make_row(total_entry_count, post_dot_digits)],
            }
        return res

    # TODO testing
    def _explain_time_delta(self, d):
        def numerus(number):
            if number == 1:
                return ''
            else:
                return 's'

        def format_seconds(s):
            return '%d second%s' % (seconds, numerus(seconds))

        words = []
        if d.days > 0:
            words.append('%d day%s' % (d.days, numerus(d.days)))
        seconds = d.seconds
        hours = seconds / 3600
        seconds = seconds - 3600 * hours
        minutes = seconds / 60
        seconds = seconds - 60 * minutes
        if hours > 0:
            words.append('%d hour%s' % (hours, numerus(hours)))
        if minutes > 0:
            words.append('%d minute%s' % (minutes, numerus(minutes)))

        if words:
            words.append(format_seconds(seconds))
            return ', '.join(words[:-1]) + ' and ' + words[-1]
        else:
            if seconds == 0:
                return 'less than 1 second'
            else:
                return format_seconds(seconds)

    def gather(self):
        report_begun = datetime.datetime.utcnow()
        self.gentoo_machines = self.session.query(GentooArchRel).count()
        simple_stuff = self._analyze_simple_stuff()
        archs = self._analyze_archs()
        compile_flags = self._analyzes_compile_flags()
        report_finished = datetime.datetime.utcnow()
        generation_duration = self._explain_time_delta(\
                report_finished - report_begun)
        data = {
            'generation_time':datetime.datetime.strftime(\
                    report_finished, "%Y-%m-%d %H:%S UTC"),
            'generation_duration':generation_duration,
            'archs':archs,
            'compile_flags':compile_flags,
        }
        for k, v in simple_stuff.items():
            if k in data:
                raise Exception('Fatal key collision')
            data[k] = v
        self._data = data

    def data(self):
        return self._data


def gentoo_data_tree(session):
    gentoo_reporter = GentooReporter(session)
    gentoo_reporter.gather()
    return gentoo_reporter.data()
