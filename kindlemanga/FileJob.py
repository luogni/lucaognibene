__author__="Jeff Byrom"
__date__ ="$Apr 2, 2010 8:54:00 AM$"

import os
import re
#from decimal import *

class FileJob:

    filename = ''
    seriesName = ''
    volume = ''
    ch = ''
    myRE = re.compile('\d+')

    def __init__(self, filename):
        self.filename = filename
        names = os.path.split(filename)
        self.seriesName = names[0][names[0].rindex('/') + 1:len(names[0])]
        
        vIndex = 0
        chIndex = 0

        # print names[1]
        try:
            extIndex = names[1].rindex ('.')
            try:
                tempVolStr = names[1][:extIndex].lower()
                #print tempVolStr
                while (True):
                    try:
                        #vIndex = names[1].lower().rindex('v')
                        vIndex = tempVolStr.rindex('v')

                        volSection = tempVolStr[vIndex:]
                        #print 'vIndex:', vIndex
                        #print 'tempVolStr: ', tempVolStr
                        volSearch = self.myRE.search(volSection)
                        #print 'volSearch: ', volSearch
                        #print volSearch.start(), volSearch.end()
                        #if ()
                        if (volSearch != None):
                            #print volSearch.start(), volSearch.end()
                            self.volume = str(int(volSection[volSearch.start():volSearch.end()]))
                            break
                        elif (tempVolStr != None):
                            #print 'tempVolStr != None'
                            tempVolStr = tempVolStr[:vIndex - 1]
                        else:
                            self.volume = ''
                            break
                        #print 'Volume: ', self.volume
                    except ValueError:
                        #print 'ValueError'
                        self.volume = ''
                        break
            except ValueError:
                self.volume = ''

            try:
                chIndex = names[1].lower().rindex('c')
                #print chIndex
                if (chIndex > vIndex and chIndex < extIndex):
                    chSection = names[1][chIndex:extIndex]
                    #print chSection
                    chSearch = self.myRE.search(chSection)
                    #print 'chSearch = ', chSearch
                    if (chSearch != None):
                        self.ch = str(int(chSection[chSearch.start():chSearch.end()]))
                #self.volume += '.' + ch
                #print 'Chapter: ', self.ch
            except ValueError:
                self.ch = ''

            try:
                seriesIndex = 0
                if (self.volume != ''):
                    endIndex = vIndex
                elif (self.ch != ''):
                    endIndex = chIndex
                else:
                    endIndex = extIndex

                if (endIndex > 0):
                    if (names[1][endIndex - 1] == '-' or names[1][endIndex - 1] == '_'):
                        endIndex -= 1
                    seriesSection = names[1][seriesIndex:endIndex].strip()
                    #print seriesSection
                    self.seriesName = seriesSection

            except ValueError:
                self.seriesName = names[0][names[0].rindex('/') + 1:len(names[0])]

        except ValueError:
            self.volume = ''
            self.ch = ''

        print "SERIES NAME", self.seriesName
        #ska - support 1234134-seriesName as mangatraders
        if self.seriesName.find ('-') > 0:
            aa = self.seriesName.split ('-')
            try:
                a = int (aa[0])
                self.seriesName = aa[1]
            except:
                pass

    def setSeriesName(self, seriesName):
        self.seriesName = seriesName

    def setVolume(self, volume):
        self.volume = str(int(volume))

    def setChapter(self, chapter):
        self.ch = str(int(chapter))


    def getFilename(self):
        return self.filename

    def getSeriesName(self):
        return self.seriesName

    def getVolume(self):
        return self.volume

    def getChapter(self):
        return self.ch
