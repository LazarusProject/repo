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
        self.main_url = 'http://mese.tv'
        self.site_name = 'Mese.tv'


    def categories(self):
        r = client.request(self.main_url)
        result = client.parseDOM(r, 'ul', attrs={'class': 'index_items'})
        result = client.parseDOM(result, 'li')
        for i in result:
            try:
                title = client.parseDOM(i, 'img', ret='title')[0]
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


    def videos(self, url, page, source, search=False):
        if search == False:
            query = urlparse.urljoin(self.main_url, url)
        else:
            query = urlparse.urljoin(self.main_url, '/?search=%s' % urllib.quote_plus(url))
        r = client.request(query)
        if not search == False and u'Nem tal\u00E1lhat\u00F3k eredm\u00E9nyek'.encode('utf-8') in r:
            raise Exception()
        var_t = re.search('var t\s*=\s*([^;]+)', r).group(1)
        var_t = eval(var_t)
        result = client.parseDOM(r, 'div', attrs={'class': 'items'})
        result = client.parseDOM(result, 'div', attrs={'class': 'item'})
        for i in result:
            try:
                title = client.parseDOM(i, 'div', attrs={'class': 'text'})
                title = client.parseDOM(title, 'h2')[0]
                title = client.replaceHTMLCodes(title)
                title = title.encode('utf-8')
                
                link = client.parseDOM(i, 'a', ret='href')[0].encode('utf-8')
                
                plot = client.parseDOM(i, 'div', attrs={'class': 'description'})[0]
                try: plot = client.replaceHTMLCodes(plot)
                except: pass
                try: plot = plot.encode('utf-8')
                except: pass
                
                img = [i[4] for i in var_t if link==i[3].replace('\\','')][0].replace('\\', '')
                #img = client.parseDOM(i, 'img', ret='src')[0].encode('utf-8')

                self.list.append({'title': title, 'url': img, 'image': img, 'plot': plot})
            except:
                pass
            for i in self.list: i.update({'action': 'resolve', 'source': source, 'page': '', 'isFolder': False, 'label': i['title']})

        return self.list


    def resolve(self, url):
        try:
            id = re.search('/vi/([^/]+)', url).group(1)
            self.list.append('https://www.youtube.com/watch?v=%s' % id)
            return self.list
        except: 
            return self.list
