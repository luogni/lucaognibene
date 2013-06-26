__author__="Jeff Byrom"
__date__ ="$Jan 20, 2010 12:54:44 PM$"

import os
import sys
import wx
import Archive
import FileJob
import ProcessImages
import KindleMangaFile
import KindleMangaLayout
import ConfigParser

class MainFrame(KindleMangaLayout.KindleMangaFrame):

    fileList = []
    outDir = ''
    win = 'win'
    linux = 'linux'

    def __init__(self, parent):
        KindleMangaLayout.KindleMangaFrame.__init__(self, parent)
        #sys.stdout = self.m_textCtrl_console
        #sys.stderr = self.m_textCtrl_console

        self.loadPrefs()

        self.m_textCtrl_outDir.SetValue(self.outDir)
        self.m_listCtrl1.InsertColumn(0, 'Filename')
        self.m_listCtrl1.InsertColumn(1, 'Series')
        self.m_listCtrl1.InsertColumn(2, 'Volume')
        self.m_listCtrl1.InsertColumn(3, 'Chapter')
        self.resizeCols()
        #self.m_listCtrl1.SetColumnWidth(0, wx.LIST_AUTOSIZE)

    def OnClose(self, event):
        self.savePrefs()
        self.Destroy()

    def OnOpen(self, event):
        self.dirname = ''
        dlg = wx.FileDialog(self, "Choose file(s) to add to list", self.dirname, '', 'Rar, zip files (*.rar;*.cbr;*.zip;*.cbz)|*.rar;*.cbr;*.zip;*.cbz', wx.FLP_CHANGE_DIR|wx.FLP_FILE_MUST_EXIST|wx.FLP_OPEN|wx.FD_MULTIPLE)
        if dlg.ShowModal() == wx.ID_OK:
            #print os.getcwd()
            self.filenames = dlg.GetFilenames()
            self.dirname = dlg.GetDirectory() + '/'
            #print self.dirname
            #print self.filenames
            for index, filename in enumerate(self.filenames):
                tempFilename = self.dirname + filename
                if tempFilename.find('\\\\') > 0:
                    tempFilename = tempFilename.replace('\\\\','\\')
                #self.filenames[index] = tempFilename
                self.filenames[index] = filename
                # filename, data, size, datetime, dir=None
                self.fileList.append(FileJob.FileJob(tempFilename))
                listIndex = self.m_listCtrl1.InsertStringItem(100, self.fileList[-1].getFilename())
                self.m_listCtrl1.SetStringItem(listIndex, 1, self.fileList[-1].getSeriesName())
                self.m_listCtrl1.SetStringItem(listIndex, 2, self.fileList[-1].getVolume())
                self.m_listCtrl1.SetStringItem(listIndex, 3, self.fileList[-1].getChapter())
                print 'Added ' + filename
            #print self.filenames
        dlg.Destroy()
        self.resizeCols()
        if (len(self.getSelections()) == 0):
            if (self.m_listCtrl1.GetItemCount() != 0):
                self.m_listCtrl1.Select(0)
                self.OnSelectJob(event)
        #return [self.dirname, self.filenames]

    def OnRemove(self, event):
        selections = self.getSelections()
        selections.reverse()
        for index in selections:
            print 'Removed ' + os.path.split(self.fileList[index].getFilename())[1]
            del self.fileList[index]
            self.m_listCtrl1.DeleteItem(index)
        self.resizeCols()

    def OnProcess(self, event):
        self.ProcessAll(self.fileList, self.m_textCtrl_outDir.GetValue())

    def OnTextSeries(self, event):
        #print "OnTextSeries"
        selected = self.getSelections()
        #print selected
        if len(selected) == 1:
            index = selected[0]
            #index = selected
            self.fileList[index].setSeriesName(self.m_textCtrl_series.GetValue())
            self.m_listCtrl1.SetStringItem(index, 1, self.fileList[index].getSeriesName())
            #print self.fileList[index].getSeriesName()
        else:
            for index in selected:
                #print index, self.fileList[index].getSeriesName()
                if (index < len(self.fileList)):
                    self.fileList[index].setSeriesName(self.m_textCtrl_series.GetValue())
                    self.m_listCtrl1.SetStringItem(index, 1, self.fileList[index].getSeriesName())
        self.resizeCols()

    
    def OnTextVolume(self, event):
        selected = self.getSelections()
        if (len(selected) == 1):
            if len(selected) == 1:
                index = selected[0]
                if (self.m_textCtrl_volume.GetValue().isdigit()):
                    #if (c for c in self.m_textCtrl_volume.GetValue() if c in '0123456789.'):
                    self.fileList[index].setVolume(self.m_textCtrl_volume.GetValue())
                    self.m_listCtrl1.SetStringItem(index, 2, str(self.fileList[index].getVolume()))

    def OnTextChapter(self, event):
        selected = self.getSelections()
        if (len(selected) == 1):
            if len(selected) == 1:
                index = selected[0]
                if (self.m_textCtrl_ch.GetValue().isdigit()):
                    #if (c for c in self.m_textCtrl_volume.GetValue() if c in '0123456789.'):
                    self.fileList[index].setChapter(self.m_textCtrl_ch.GetValue())
                    self.m_listCtrl1.SetStringItem(index, 3, str(self.fileList[index].getChapter()))

    def OnOutDir(self, event):
        self.outDir = self.m_textCtrl_outDir.GetValue()

    def OnOutDirButton(self, event):
        self.dirname = ''
        if self.m_textCtrl_outDir.GetValue() != '':
            self.dirname = self.m_textCtrl_outDir.GetValue()
        else:
            self.dirname = os.getcwd()

        #print "Opening dir: " + self.dirname
        dlg = wx.DirDialog(self, "Choose directory to create output files", self.dirname)
        if dlg.ShowModal() == wx.ID_OK:
            #print os.getcwd()
            self.dirname = dlg.GetPath()
            #print self.dirname
            self.m_textCtrl_outDir.SetValue(self.dirname)
        dlg.Destroy()

    def OnSelectJob(self, event):
        selected = self.getSelections()

        #if (self.m_listCtrl1.GetSelectedItemCount() == 1):
        if (len(selected) == 1):
            #selected = self.m_listCtrl1.GetNextItem(-1, state = wxLIST_STATE_SELECTED)
            #selected = self.m_listCtrl1.GetFirstSelected()
            index = selected[0]
            
            #if (selected > -1):
            if (index > -1):
                seriesName = self.m_listCtrl1.GetItem(index, 1)
                volume = self.m_listCtrl1.GetItem(index, 2)
                ch = self.m_listCtrl1.GetItem(index, 3)
                #print seriesName.GetText()
                #print self.m_listCtrl1.GetItemText(item)
                #print value
                self.m_textCtrl_series.SetValue(seriesName.GetText())
                self.m_textCtrl_volume.SetValue(volume.GetText())
                self.m_textCtrl_ch.SetValue(ch.GetText())
        #elif (self.m_listCtrl1.GetSelectedItemCount() > 1):
        elif (len(selected) > 1):
            #selected = self.m_listCtrl1.GetNextItem(-1, state = wx.LIST_STATE_SELECTED)
            #while (selected >= 0):
            for index in selected:
                #print selected

                if (len(self.fileList) > index):
                    sameSeriesName = True
                    firstSeriesName = self.fileList[index].getSeriesName()
                    #for index in selected:
                    #    # set the list ctrl to same selection:
                    #    self.m_listCtrl1.SetItemState(index, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)
                    #for index in selected:
                    if (firstSeriesName != self.fileList[index].getSeriesName()):
                        sameSeriesName = False
                        break
                    if (sameSeriesName):
                        self.m_staticText_archiveName.SetLabel('')
                        self.m_textCtrl_series.SetValue(firstSeriesName)
                        self.m_textCtrl_volume.SetValue('')
                        self.m_textCtrl_ch.SetValue('')

                #selected = self.m_listCtrl1.GetNextItem(selected, state = wx.LIST_STATE_SELECTED)
                #selected = self.m_listCtrl1.GetNextItem(selected, state = wx.LIST_STATE_SELECTED)
                #print selected
            #print 'multiple selected'


    def ProcessAll(self, fileJobList, outDir):
        unknownVol = 0;
        for index, job in enumerate(fileJobList):
            filename = job.getFilename()
            #print 'filename: ' + filename

            filepath = os.path.split(filename)
            #print 'filepath: ' + str(filepath)
            volume = job.getVolume()
            ch = job.getChapter()
            if (job.getSeriesName() != ''):
                seriesName = job.getSeriesName()
            else:
                seriesName = 'Unknown'
                unknownVol += 1
                volume = unknownVol
            if (outDir != ''):
                #if (not os.path.isdir(outDir)):
                #    self.dialog_dir_not_found.show()
                tempDirName = outDir

            tempDir = tempDirName + '/' # + seriesName
            print tempDir
            os.chdir(tempDir)
            #print os.getcwd()
            #if job.getSeriesName().len > 0:
            #
            #imageDir = os.path.splitext(filepath[1])[0]
            #tempImageDir = raw_input('set imageDir: [' + imageDir + ']: ')
            tempImageDir = seriesName.replace(' ', '_')
            if (len(volume) > 0):
                tempImageDir += '-vol.' + ('%03d' % int(volume))
            if (len(ch) > 0):
                tempImageDir += '-ch.' + ('%03d' % int(ch))
                
            if (len(tempImageDir) != 0):
                imageDir = tempImageDir

            # height of kindle display - 40 pixel status bar:
            #targetHeight = 760
            #maxWidth = 600
            #better to use it rotated and scroll.. or i won't see anything!
            targetHeight = 1200
            maxWidth = 800

            # check if tmp directory exists, creat if it does not:
            if (not os.path.isdir(imageDir)):
                os.mkdir(imageDir)

            os.chdir(imageDir)
            print

            archive = Archive.Archive()
            archive.ArchiveFile(filename)

            entries = archive.ReadFiles()
            entries.sort()

            archive.Close()

            ProcessImages.ProcessAndSave(entries, targetHeight, maxWidth)
            KindleMangaFile.WriteMangaFiles()
            os.chdir('..')
            progress = int((float(index + 1) / float(len(fileJobList))) * 100)
            #print index, len(fileJobList)
            #print progress
            self.m_gauge_progress.SetValue(progress)
        print 'done'

    def printBox(self, text):
        self.m_textCtrl_console.AppendText(text)

    def getSelections(self):
        returnSelections = []
        selected = self.m_listCtrl1.GetNextItem(-1, state = wx.LIST_STATE_SELECTED)
        while (selected >= 0):
            returnSelections.append(selected)
            selected = self.m_listCtrl1.GetNextItem(selected, state = wx.LIST_STATE_SELECTED)
        return returnSelections

    def resizeCols(self):
        if (self.m_listCtrl1.GetItemCount() > 0):
            self.m_listCtrl1.SetColumnWidth(0, wx.LIST_AUTOSIZE)
            self.m_listCtrl1.SetColumnWidth(1, wx.LIST_AUTOSIZE)
            self.m_listCtrl1.SetColumnWidth(2, wx.LIST_AUTOSIZE_USEHEADER)
            self.m_listCtrl1.SetColumnWidth(3, wx.LIST_AUTOSIZE_USEHEADER)
        else:
            self.m_listCtrl1.SetColumnWidth(0, wx.LIST_AUTOSIZE_USEHEADER)
            self.m_listCtrl1.SetColumnWidth(1, wx.LIST_AUTOSIZE_USEHEADER)
            self.m_listCtrl1.SetColumnWidth(2, wx.LIST_AUTOSIZE_USEHEADER)
            self.m_listCtrl1.SetColumnWidth(3, wx.LIST_AUTOSIZE_USEHEADER)

    def loadPrefs(self):
        try:
            config = ConfigParser.ConfigParser()
            config.read('settings.cfg')
            if (len(config.get('PrevState', 'outDir')) > 0):
                self.outDir = config.get('PrevState', 'outDir')
            else:
                if (sys.platform.find(self.win) >= 0):
                    if (os.path.isdir(os.getenv('USERPROFILE') + '\\My Documents')):
                        self.outDir = os.getenv('USERPROFILE') + '\\My Documents'
                elif (sys.platform.find(self.linux) >= 0):
                    if (os.path.isdir(os.getenv('HOME'))):
                        self.outDir = os.getenv('HOME')
                
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError, ConfigParser.ParsingError):
            # File not found
            #print sys.exc_info()[0], sys.exc_info()[1]
            if (sys.platform.find(self.win) >= 0):
                if (os.path.isdir(os.getenv('USERPROFILE') + '\\My Documents')):
                    self.outDir = os.getenv('USERPROFILE') + '\\My Documents'
            elif (sys.platform.find(self.linux) >= 0):
                if (os.path.isdir(os.getenv('HOME'))):
                    self.outDir = os.getenv('HOME')
            #pass

    def savePrefs(self):
        #try:
        config = ConfigParser.ConfigParser()
        config.add_section('PrevState')
        config.set('PrevState', 'outDir', self.outDir)

        with open('settings.cfg', 'wb') as configfile:
            config.write(configfile)
        #except

class Gui(wx.App):
    def OnInit(self):
        self.m_frame = MainFrame(None)
        self.m_frame.Show()
        self.SetTopWindow(self.m_frame)
        return True

app = Gui(0)
app.MainLoop()
