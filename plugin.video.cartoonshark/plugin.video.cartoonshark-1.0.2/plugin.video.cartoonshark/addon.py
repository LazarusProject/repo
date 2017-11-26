# -*- coding: utf-8 -*-

'''
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


import urlparse,sys
from resources.lib.indexers.navigator import navigator


REMOTE_DBG = False


# append pydev remote debugger
if REMOTE_DBG:
    # Make pydev debugger works for auto reload.
    # Note pydevd module need to be copied in XBMC\system\python\Lib\pysrc
    try:
        sys.path.append("C:\\Users\\User\\.p2\\pool\\plugins\\org.python.pydev_4.4.0.201510052309\\pysrc")
        import pydevd # with the addon script.module.pydevd, only use `import pydevd`
    # stdoutToServer and stderrToServer redirect stdout and stderr to eclipse console
        pydevd.settrace('localhost', stdoutToServer=True, stderrToServer=True)
    except ImportError:
        sys.stderr.write("Error: " +
            "You must add org.python.pydev.debug.pysrc to your PYTHONPATH.")
        sys.exit(1)


params = dict(urlparse.parse_qsl(sys.argv[2].replace('?','')))

url = params.get('url')

action = params.get('action')

source = params.get('source')

title = params.get('title')

image = params.get('image')

search_text = params.get('search_text')

page = params.get('page')
if page == None or len(page)<1:
    page ='1'


if action == None:
    navigator().root()

elif action == 'folders':
    navigator().folders(source)

elif action == 'videos':
    navigator().videos(source, url, page)

elif action == 'resolve':
    navigator().getVideo(url, image, title, source)

elif action == 'search':
    navigator().search()

elif action == 'search_result':
    navigator().search_thread(search_text)
