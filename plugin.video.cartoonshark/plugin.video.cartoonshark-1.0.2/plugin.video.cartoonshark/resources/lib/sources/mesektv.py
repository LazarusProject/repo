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
        self.main_url = 'http://www.mesek.tv'
        self.site_name = 'Mesek.tv'


    def categories(self):
        r = client.request(self.main_url)
        try: r = r.decode('iso-8859-1').encode('utf-8')
        except: pass
        result = client.parseDOM(r, 'ul', attrs={'id': 'menu-fo-menu'})
        result = client.parseDOM(result, 'li', attrs={'id': 'menu-item-\d+'})
        result2 = client.parseDOM(result, 'li', attrs={'id': 'menu-item-\d+'})
        if result2: [result.append(i) for i in result2]
        result = [i for i in result if not 'sub-menu' in i and i.strip() != '']
        for i in result:
            try:
                title = client.parseDOM(i, 'a')[0]
                try: title = title.encode('iso-8859-1')
                except: pass
                title = re.sub('<.*>', '', title).strip()
                title = client.replaceHTMLCodes(title)
                
                url = client.parseDOM(i, 'a', ret='href')[0].encode('utf-8')

                self.list.append({'title': title, 'url': url, 'image': '0'})
            except:
                pass
        for i in self.list: i.update({'action': 'videos'})

        return self.list


    def videos(self, url, page, source, search=False):
        if search == False:
            query = urlparse.urljoin(self.main_url, url + '/page/%s' % page)
        else:
            query = urlparse.urljoin(self.main_url, '/?s=%s' % urllib.quote_plus(url))
        r = client.request(query)
        try: r = r.decode('iso-8859-1').encode('utf-8')
        except: pass
        result = client.parseDOM(r, 'div', attrs={'id': 'content'})
        if search == False:
            result = client.parseDOM(result, 'div', attrs={'class': 'cat_view'})
        else:
            result = client.parseDOM(result, 'div', attrs={'class': 'single_game'})
        #result = client.parseDOM(result, 'div', attrs={'class': 'cat_view'})
        for i in result:
            try:
                title = client.parseDOM(i, 'a', ret='title')[0]
                try: title = title = title.encode('iso-8859-1').decode('utf-8')
                except: pass
                try: title = client.replaceHTMLCodes(title)
                except: pass
                title = title.encode('utf-8')
                try:
                    plot = client.parseDOM(i, 'div')
                    plot = re.search('/h4>\s*([^<]+)', plot[0]).group(1)
                    try: plot = client.replaceHTMLCodes(plot)
                    except: pass
                    try: plot = plot.encode('iso-8859-1')
                    except: pass
                except:
                    plot = ''

                link = client.parseDOM(i, 'a', ret='href')[0].encode('utf-8')
    
                img = client.parseDOM(i, 'img', ret='src')[0].encode('utf-8')
                try: img = re.sub('-\d+x\d+\.', '.', img)
                except: pass
    
                self.list.append({'title': title, 'url': link, 'image': img, 'plot': plot})
            except:
                pass
            for i in self.list: i.update({'action': 'resolve', 'source': source, 'page': '', 'isFolder': False, 'label': i['title']})

        try:
            next = client.parseDOM(r, 'a', attrs={'class': 'nextpostslink'})
            if next:
                self.list.append({'title': '[COLOR green]Következő oldal >>[/COLOR]', 'url': url, 'image': '', 'action': 'videos', 'source': source, 'page': str(int(page) + 1), 'isFolder': True, 'plot': ''})
        except:
            pass

        return self.list


    def resolve(self, url):
        try:
            query = urlparse.urljoin(self.main_url, url)
            r = client.request(query)
            result = client.parseDOM(r, 'div', attrs={'id': 'play_game'})
            
            self.list += client.parseDOM(result, 'iframe', ret='src')
            self.list += client.parseDOM(result, 'embed', ret='src')
            self.list += client.parseDOM(result, 'a', ret='href')
            return self.list
        except: 
            return self.list
