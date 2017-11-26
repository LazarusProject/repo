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
        self.main_url = 'https://rajzfilmek.online'
        self.site_name = 'Classic Cartoons'


    def categories(self):
        query = urlparse.urljoin(self.main_url, '/live-search.php?category=')
        r = client.request(query)
        result = result = r.split('</span>')
        for i in result:
            try:
                title = client.parseDOM(i, 'b')[0]
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
        query = urlparse.urljoin(self.main_url, url)
        r = client.request(query)
        result = r.split('<table ')
        result = [(re.search('\sid="(\d+)"', i).group(1), i) for i in result if 'select.php' in i]
        result = [(i[0], client.parseDOM(i[1], 'tr')) for i in result]
        
        try:
            plot = client.parseDOM(r, 'div', attrs={'class': 'description'})
            plot = client.parseDOM(plot, 'p')[0]
            plot = client.replaceHTMLCodes(plot)
            plot = plot.encode('utf-8')
        except:
            plot = ''
        
        try:
            img = client.parseDOM(r, 'img', ret='src')
            img = [i for i in img if '/posters/' in i][0]
            img = re.sub('jpg.+$', 'jpg', img)
            img = img.encode('utf-8')
        except:
            img = ''

        for item in result:
            season = item[0]
            for x in item[1]:
                try:
                    #x = x.replace('\n', '')
                    episode = client.parseDOM(x, 'td', attrs={'class': 'row_ep'})[0].replace('\n', '').strip()
                    episode = episode.encode('utf-8')
                    
                    title = client.parseDOM(x, 'td', attrs={'class': 'row_ti'})
                    title = [i.replace('\n', '') for i in title]
                    title = [i for i in title if not i.strip() == '']
                    title = '' if title == [] else title[0]
                    title = client.replaceHTMLCodes(title)
                    title = title.encode('utf-8')
                    
                    link = client.parseDOM(x.replace('\n', ''), 'a', ret='href')[0].encode('utf-8')

                    self.list.append({'title': '%sX%s  %s' % (season, episode, title), 'url': link, 'image': img})
                except:
                    pass

        for i in self.list: i.update({'action': 'resolve', 'source': source, 'page': '', 'plot': plot, 'isFolder': False, 'label': i['title']})

        return self.list


    def resolve(self, url):
        try:
            query = urlparse.urljoin(self.main_url, url)
            r = client.request(query)

            self.list += client.parseDOM(r, 'iframe', ret='src')
            if self.list == []:
                result = re.findall('["\'](http[^"\']+)', r)
                result = [i for i in result if 'googleusercontent.com' in i]
                if result:
                    r = client.request(result[0], output='geturl', redirect=False)
                    if 'googlevideo.com' in r: self.list.append(r)
            return self.list
        except: 
            return self.list
