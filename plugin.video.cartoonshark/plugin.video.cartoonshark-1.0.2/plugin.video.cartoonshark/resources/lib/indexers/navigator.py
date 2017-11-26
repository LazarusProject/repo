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


import os,sys,urlparse,urllib,xbmc,time,re

from resources.lib.modules import control
from resources.lib.modules import cleantitle
from resources.lib.modules import workers

try: import urlresolver
except: pass


sysaddon = sys.argv[0] ; syshandle = int(sys.argv[1])

artPath = control.artPath(); addonFanart = control.addonFanart()

from resources.lib.sources import sources as sources
sourceDict = sources()

class navigator:
    def __init__(self):
        self.results = []


    def root(self):
        self.addDirectoryItem(u'Keres\u00E9s', 'search', os.path.join(artPath, 'search.png'))
        
        for i in sourceDict:
            try:
                self.addDirectoryItem(i[1].site_name.encode('utf-8'), 'folders&source=%s' % i[0], os.path.join(artPath, i[0] + '.png'))
            except:
                pass

        self.endDirectory()


    def folders(self, source):
        source = [i for i in sourceDict if i[0] == source][0]
        list = source[1].categories()
        for i in list:
            self.addDirectoryItem(i['title'], '%s&source=%s&url=%s' % (i['action'], source[0], urllib.quote_plus(i['url'])), i['image'])

        self.endDirectory()
    

    def videos(self, source, url, page, search=False):
        if search == True:
            list = self.results
            if list == []: return
            for i in list: i.update({'label': '[COLOR FF008000][I]%s [/I][/COLOR] | %s' % (i['source'].upper(), i['title'])})
        else:
            source = [i for i in sourceDict if i[0] == source][0]
            list = source[1].videos(url, page, source[0])
        for i in list:
            try:
                isPlayable = queue = True if not i['isFolder'] == True else False
                label = i['label'] if 'label' in i else i['title']
                self.addDirectoryItem(label, '%s&title=%s&url=%s&image=%s&source=%s&page=%s' % (i['action'], urllib.quote_plus(i['title']), urllib.quote_plus(i['url']), i['image'], i['source'], i['page']), i['image'], queue=queue, isAction=True, isFolder=i['isFolder'], isPlayable = isPlayable, plot = i['plot'])
            except:
                pass

        self.endDirectory(content='movies')


    def getVideo(self, url, icon, title, source):
        try:
            source = [i for i in sourceDict if i[0] == source][0]
            u = source[1].resolve(url)

            if u == None or u == []: raise Exception()

            if type(u) == str:
                pass

            else:
                u = [re.sub('^//', 'http://', i) for i in u]
                u = [re.sub('http.+?\?http', 'http', i) for i in u]
                u = [i.replace('videakid.hu', 'videa.hu') for i in u]
                u = [i.replace('flvplayer.swf', 'player') for i in u]
                u = [re.sub('/preview$', '', i) for i in u]
                u = [i.encode('utf-8') for i in u]
                
                for item in u:
                    try:
                        hmf = urlresolver.HostedMediaFile(url=item, include_disabled=True, include_universal=False)
                        if hmf.valid_url() == True: u = hmf.resolve(); break
                    except:
                        pass
    
                if u == False or u == None: raise Exception()

            item = control.item(path=u)
            item.setArt({'icon': icon, 'thumb': icon})
            item.setInfo(type='Video', infoLabels = {'Title': title})

            control.resolve(int(sys.argv[1]), True, item)
        except:
            control.idle()
            control.infoDialog(u'Lej\u00E1tsz\u00E1s sikertelen')
            return


    def search(self):
        try:
            control.idle()

            t = u'Keres\u00E9s'
            k = control.keyboard('', t) ; k.doModal()
            q = k.getText() if k.isConfirmed() else None

            if (q == None or q == ''): return

            url = urllib.quote_plus(q)
            url = '%s?action=search_result&search_text=%s' % (sys.argv[0], urllib.quote_plus(url))
            control.execute('Container.Update(%s)' % url)
        except:
            return


    def search_thread(self, search_text):
        threads = []

        title = self.getTitle(urllib.unquote_plus(search_text))
        for i in sourceDict: threads.append(workers.Thread(self.getSearchResult, title, i[0], i[1]))
        
        [i.start() for i in threads]
        
        for i in range(0, (30 * 2) + 60):
            try:
                if xbmc.abortRequested == True: return sys.exit()

                is_alive = [x.is_alive() for x in threads]
                if all(x == False for x in is_alive): break

                time.sleep(0.5)
            except:
                pass

        self.videos('', '', '', search=True)


    def getSearchResult(self, title, source, call):
        try:
            results = []
            results = call.videos(title, '', source, search=True)
            self.results.extend(results)
        except:
            pass


    def getTitle(self, title):
        title = cleantitle.normalize(title)
        return title


    def addDirectoryItem(self, name, query, icon, queue=False, isAction=True, isFolder=True, isPlayable=False, plot = ''):
        try: name = control.lang(name).encode('utf-8')
        except: pass
        url = '%s?action=%s' % (sysaddon, query) if isAction == True else query
        cm = []
        if queue == True: cm.append((u'Lej\u00E1tsz\u00E1si sorba tesz', 'RunPlugin(%s?action=queueItem)' % sysaddon))
        item = control.item(label=name)
        item.addContextMenuItems(cm)
        item.setArt({'icon': icon, 'thumb': icon, 'poster': icon})
        if not isPlayable == False: item.setProperty("IsPlayable", "true"); item.setInfo( type="Video", infoLabels= {'Title': name, 'Plot': plot, 'Genre': 'Mese'} )
        if not addonFanart == None: item.setProperty('Fanart_Image', addonFanart)
        control.addItem(handle=syshandle, url=url, listitem=item, isFolder=isFolder)


    def endDirectory(self, content='addons'):
        control.content(syshandle, content)
        control.directory(syshandle, cacheToDisc=True)
