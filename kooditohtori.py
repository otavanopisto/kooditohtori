#!/usr/bin/env python3

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bottle
import sqlite3
import xml.etree.ElementTree as ET

@bottle.put("/sendreport")
def send_report():
    conn = sqlite3.connect("kooditohtori.db")
    c = conn.cursor()
    root = ET.parse(bottle.request.body).getroot()
    
    timestamp = root.attrib['timestamp']
    project = root.find('Project').attrib['projectName']
    
    for bug_instance in root.findall('BugInstance'):
        short_message = bug_instance.find('ShortMessage').text
        long_message = bug_instance.find('LongMessage').text
        c.execute("""INSERT INTO bug_instance (
                        timestamp,
                        project,
                        short_message,
                        long_message
                    ) VALUES (?, ?, ?, ?)""",
                    (timestamp,
                    project,
                    short_message,
                    long_message))
        
    conn.commit()
    conn.close()
    
@bottle.get("/bug_instances")
def bug_instances():
    conn = sqlite3.connect("kooditohtori.db")
    c = conn.cursor()
    
    rows = c.execute(
    """SELECT
            timestamp,
            project,
            short_message,
            long_message
        FROM
            bug_instance
        ORDER BY
            timestamp DESC,
            project DESC,
            short_message DESC,
            long_message DESC""")
    
    result = {
        "bug_instances": [
            {'timestamp': timestamp,
             'project': project,
             'short_message': short_message,
             'long_message': long_message}
            for (timestamp, project, short_message, long_message)
            in rows
        ]
    }
        
    conn.commit()
    conn.close()
    
    return result

@bottle.route("/static/<filename>")
def serve_static(filename):
    return bottle.static_file(filename, root="./static")
    
bottle.run(host='localhost', port=6060, debug=True)