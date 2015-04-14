#!/usr/bin/env python

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bottle
import sqlite3
import xml.etree.ElementTree as ET
import functools


def transactional(fn):
    @functools.wraps(fn)
    def inner(*args, **kwargs):
        conn = sqlite3.connect("kooditohtori.db")
        cursor = conn.cursor()
        kwargs.update(cursor=cursor)
        result = fn(*args, **kwargs)
        conn.commit()
        conn.close()
        return result
    return inner


@bottle.put("/reports/:project/:travis_build_number")
@transactional
def send_report(cursor, project, travis_build_number):
    root = ET.parse(bottle.request.body).getroot()
    
    cursor.execute(
        """ DELETE FROM bug_instance
            WHERE project = ?
            AND travis_build_number = ?""",
        (project, travis_build_number))
    
    for bug_instance in root.findall('BugInstance'):
        short_message = bug_instance.find('ShortMessage').text
        long_message = bug_instance.find('LongMessage').text
        cursor.execute(
            """INSERT INTO bug_instance (
                travis_build_number,
                project,
                short_message,
                long_message
            ) VALUES (?, ?, ?, ?)""",
            (travis_build_number,
                project,
                short_message,
                long_message))
    

@bottle.get("/bug_instances")
@transactional
def bug_instances(cursor):
    rows = cursor.execute(
        """SELECT
            travis_build_number,
            project,
            short_message,
            long_message
        FROM
            bug_instance
        ORDER BY
            travis_build_number DESC,
            project ASC,
            short_message ASC,
            long_message ASC""")
    
    return {
        "bug_instances": [
            {'travis_build_number': travis_build_number,
             'project': project,
             'short_message': short_message,
             'long_message': long_message}
            for (travis_build_number, project, short_message, long_message)
            in rows
        ]
    }


@bottle.get("/bug_report")
@transactional
def bug_report(cursor):
    rows = cursor.execute(
        """SELECT
            project,
            short_message,
            COUNT(*) as num_bugs
        FROM
            bug_instance
        WHERE
            travis_build_number =
                (SELECT MAX(travis_build_number) FROM bug_instance)
        GROUP BY
            project,
            short_message
        ORDER BY
            num_bugs DESC,
            short_message ASC,
            project ASC""")
    
    return {
        "bug_counts": [
            {'project': project,
             'short_message': short_message,
             'num_bugs': num_bugs}
            for (project, short_message, num_bugs)
            in rows
        ]
    }


@bottle.route("/static/<filename>")
def serve_static(filename):
    return bottle.static_file(filename, root="./static")
    

bottle.run(host='0.0.0.0', port=8080, debug=True)
