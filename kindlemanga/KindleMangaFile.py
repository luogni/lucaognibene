__author__="Jeff Byrom"
__date__ ="$Jan 22, 2010 2:27:29 PM$"

import os
import time

def WriteMangaFiles():
    folder = os.path.split(os.getcwd())[1]
    date = time.gmtime()
    print folder

    placeFilename = folder + '.manga_save'
    mangaFilename = folder + '.manga'

    placeFile = open(placeFilename, 'wb')
    placeFile.write(time.strftime('#%a %b %d %H:%M:%S GMT %Y', date) + '\n')
    placeFile.write('LAST=/mnt/us/pictures/' + folder + '/0000.gif' + '\n')
    placeFile.close()
    print placeFilename

    mangaFile = open(mangaFilename, 'wb')
    mangaFile.write('\0')
    mangaFile.close()
    print mangaFilename
