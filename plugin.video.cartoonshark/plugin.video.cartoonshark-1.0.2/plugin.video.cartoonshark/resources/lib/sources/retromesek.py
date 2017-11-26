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


import re,urlparse,urllib

from resources.lib.modules import client

class source:
    def __init__(self):
        self.list = []
        self.main_url = 'http://www.retromesek.hu'
        self.site_name = u'Retr\u00F3 mes\u00E9k'


    def categories(self):
        r = client.request(self.main_url)
        result = client.parseDOM(r, 'div', attrs={'class': 'categories'})
        result = client.parseDOM(result, 'td')
        for i in result:
            try:
                title = client.parseDOM(i, 'img', ret='alt')[0]
                title = client.replaceHTMLCodes(title)
                title = title.encode('utf-8')
                
                img = client.parseDOM(i, 'img', ret='src')[0].encode('utf-8')
                img = urlparse.urljoin(self.main_url, img)
                
                url = client.parseDOM(i, 'a', ret='href')[0].encode('utf-8')

                self.list.append({'title': title, 'url': url, 'image': img})
            except:
                pass
        for i in self.list: i.update({'action': 'videos'})

        return self.list


    def videos(self, url, page, source):
        query = urlparse.urljoin(self.main_url, url + '/%s' % page)
        r = client.request(query)
        result = client.parseDOM(r, 'div', attrs={'id': 'main'})
        result = client.parseDOM(result, 'td')
        for i in result:
            try:
                title = client.parseDOM(i, 'br')[0]
                title = client.replaceHTMLCodes(title)
                title = title.encode('utf-8')

                link = client.parseDOM(i, 'a', ret='href')[0].encode('utf-8')

                img = client.parseDOM(i, 'img', ret='src')[0].encode('utf-8')

                self.list.append({'title': title, 'url': link, 'image': img})
            except:
                pass
            for i in self.list: i.update({'action': 'resolve', 'source': source, 'page': '', 'plot': '', 'isFolder': False, 'label': i['title']})

        try:
            if re.sub('^/', '', urllib.unquote_plus(url)) + '/%s\'' % str(int(page) + 1) in r:
                self.list.append({'title': '[COLOR green]Következő oldal >>[/COLOR]', 'url': url, 'image': '', 'action': 'videos', 'source': source, 'page': str(int(page) + 1), 'isFolder': True, 'plot': ''})
        except:
            pass
        
        return self.list


    def resolve(self, url):
        try:
            query = urlparse.urljoin(self.main_url, url)
            r = client.request(query)
            self.list += client.parseDOM(r, 'iframe', ret='src')
            self.list += client.parseDOM(r, 'embed', ret='src')
            return self.list
        except: 
            return self.list
