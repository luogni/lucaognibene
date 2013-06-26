# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Feb 17 2010)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx

###########################################################################
## Class KindleMangaFrame
###########################################################################

class KindleMangaFrame ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"KindleManga", pos = wx.DefaultPosition, size = wx.Size( 700,540 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		self.m_menubar1 = wx.MenuBar( 0 )
		self.m_menu1 = wx.Menu()
		self.m_menuItem_open = wx.MenuItem( self.m_menu1, wx.ID_ANY, u"&Open"+ u"\t" + u"Ctrl + O", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu1.AppendItem( self.m_menuItem_open )
		
		self.m_menubar1.Append( self.m_menu1, u"&File" ) 
		
		self.SetMenuBar( self.m_menubar1 )
		
		bSizer1 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_panel2 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		fgSizer1 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer1.AddGrowableCol( 1 )
		fgSizer1.AddGrowableRow( 0 )
		fgSizer1.SetFlexibleDirection( wx.BOTH )
		fgSizer1.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		bSizer2 = wx.BoxSizer( wx.VERTICAL )
		
		fgSizer1.Add( bSizer2, 1, wx.EXPAND, 5 )
		
		bSizer6 = wx.BoxSizer( wx.VERTICAL )
		
		fgSizer41 = wx.FlexGridSizer( 1, 3, 0, 0 )
		fgSizer41.SetFlexibleDirection( wx.BOTH )
		fgSizer41.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_button_add = wx.Button( self.m_panel2, wx.ID_ANY, u"Add Files", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer41.Add( self.m_button_add, 0, wx.ALL, 5 )
		
		self.m_button_rem = wx.Button( self.m_panel2, wx.ID_ANY, u"Remove", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer41.Add( self.m_button_rem, 0, wx.ALL, 5 )
		
		self.m_button_proc = wx.Button( self.m_panel2, wx.ID_ANY, u"Process", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer41.Add( self.m_button_proc, 0, wx.ALL, 5 )
		
		bSizer6.Add( fgSizer41, 0, 0, 5 )
		
		fgSizer3 = wx.FlexGridSizer( 1, 3, 0, 0 )
		fgSizer3.AddGrowableCol( 1 )
		fgSizer3.SetFlexibleDirection( wx.BOTH )
		fgSizer3.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText4 = wx.StaticText( self.m_panel2, wx.ID_ANY, u"Output Directory:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText4.Wrap( -1 )
		fgSizer3.Add( self.m_staticText4, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )
		
		self.m_textCtrl_outDir = wx.TextCtrl( self.m_panel2, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer3.Add( self.m_textCtrl_outDir, 0, wx.BOTTOM|wx.EXPAND|wx.RIGHT|wx.TOP, 5 )
		
		self.m_button_outDir = wx.Button( self.m_panel2, wx.ID_ANY, u"Browse", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer3.Add( self.m_button_outDir, 0, wx.ALL, 5 )
		
		bSizer6.Add( fgSizer3, 0, wx.EXPAND, 5 )
		
		self.m_listCtrl1 = wx.ListCtrl( self.m_panel2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_NO_SORT_HEADER|wx.LC_REPORT|wx.LC_VRULES )
		bSizer6.Add( self.m_listCtrl1, 1, wx.EXPAND, 5 )
		
		sbSizer2 = wx.StaticBoxSizer( wx.StaticBox( self.m_panel2, wx.ID_ANY, wx.EmptyString ), wx.VERTICAL )
		
		fgSizer4 = wx.FlexGridSizer( 2, 2, 0, 0 )
		fgSizer4.AddGrowableCol( 1 )
		fgSizer4.SetFlexibleDirection( wx.BOTH )
		fgSizer4.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText41 = wx.StaticText( self.m_panel2, wx.ID_ANY, u"Archive Name:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText41.Wrap( -1 )
		fgSizer4.Add( self.m_staticText41, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )
		
		self.m_staticText_archiveName = wx.StaticText( self.m_panel2, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText_archiveName.Wrap( -1 )
		fgSizer4.Add( self.m_staticText_archiveName, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_staticText1 = wx.StaticText( self.m_panel2, wx.ID_ANY, u"Series:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText1.Wrap( -1 )
		fgSizer4.Add( self.m_staticText1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )
		
		self.m_textCtrl_series = wx.TextCtrl( self.m_panel2, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_textCtrl_series.SetMaxLength( 100 ) 
		fgSizer4.Add( self.m_textCtrl_series, 0, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )
		
		self.m_staticText2 = wx.StaticText( self.m_panel2, wx.ID_ANY, u"Volume / Chapter:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText2.Wrap( -1 )
		fgSizer4.Add( self.m_staticText2, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )
		
		self.m_textCtrl_volume = wx.TextCtrl( self.m_panel2, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_textCtrl_volume.SetMaxLength( 10 ) 
		fgSizer4.Add( self.m_textCtrl_volume, 0, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )
		
		self.m_staticText8 = wx.StaticText( self.m_panel2, wx.ID_ANY, u"Chapter:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText8.Wrap( -1 )
		fgSizer4.Add( self.m_staticText8, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )
		
		self.m_textCtrl_ch = wx.TextCtrl( self.m_panel2, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer4.Add( self.m_textCtrl_ch, 0, wx.EXPAND, 5 )
		
		sbSizer2.Add( fgSizer4, 1, wx.EXPAND, 5 )
		
		bSizer6.Add( sbSizer2, 0, wx.EXPAND, 5 )
		
		self.m_textCtrl_console = wx.TextCtrl( self.m_panel2, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_AUTO_URL|wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_WORDWRAP )
		bSizer6.Add( self.m_textCtrl_console, 1, wx.ALL|wx.EXPAND, 5 )
		
		fgSizer5 = wx.FlexGridSizer( 1, 1, 0, 0 )
		fgSizer5.SetFlexibleDirection( wx.BOTH )
		fgSizer5.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_gauge_progress = wx.Gauge( self.m_panel2, wx.ID_ANY, 100, wx.DefaultPosition, wx.DefaultSize, wx.GA_HORIZONTAL )
		self.m_gauge_progress.SetValue( 0 ) 
		self.m_gauge_progress.SetMinSize( wx.Size( 300,15 ) )
		self.m_gauge_progress.SetMaxSize( wx.Size( 300,15 ) )
		
		fgSizer5.Add( self.m_gauge_progress, 1, wx.EXPAND|wx.ALIGN_RIGHT, 5 )
		
		bSizer6.Add( fgSizer5, 0, wx.ALIGN_RIGHT, 5 )
		
		fgSizer1.Add( bSizer6, 1, wx.EXPAND, 5 )
		
		self.m_panel2.SetSizer( fgSizer1 )
		self.m_panel2.Layout()
		fgSizer1.Fit( self.m_panel2 )
		bSizer1.Add( self.m_panel2, 1, wx.EXPAND, 5 )
		
		self.SetSizer( bSizer1 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.Bind( wx.EVT_CLOSE, self.OnClose )
		self.Bind( wx.EVT_MENU, self.OnOpen, id = self.m_menuItem_open.GetId() )
		self.m_button_add.Bind( wx.EVT_BUTTON, self.OnOpen )
		self.m_button_rem.Bind( wx.EVT_BUTTON, self.OnRemove )
		self.m_button_proc.Bind( wx.EVT_BUTTON, self.OnProcess )
		self.m_textCtrl_outDir.Bind( wx.EVT_TEXT, self.OnOutDir )
		self.m_button_outDir.Bind( wx.EVT_BUTTON, self.OnOutDirButton )
		self.m_listCtrl1.Bind( wx.EVT_LIST_ITEM_SELECTED, self.OnSelectJob )
		self.m_textCtrl_series.Bind( wx.EVT_TEXT, self.OnTextSeries )
		self.m_textCtrl_volume.Bind( wx.EVT_TEXT, self.OnTextVolume )
		self.m_textCtrl_ch.Bind( wx.EVT_TEXT, self.OnTextChapter )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnClose( self, event ):
		event.Skip()
	
	def OnOpen( self, event ):
		event.Skip()
	
	
	def OnRemove( self, event ):
		event.Skip()
	
	def OnProcess( self, event ):
		event.Skip()
	
	def OnOutDir( self, event ):
		event.Skip()
	
	def OnOutDirButton( self, event ):
		event.Skip()
	
	def OnSelectJob( self, event ):
		event.Skip()
	
	def OnTextSeries( self, event ):
		event.Skip()
	
	def OnTextVolume( self, event ):
		event.Skip()
	
	def OnTextChapter( self, event ):
		event.Skip()
	

###########################################################################
## Class dialog_dir_not_found
###########################################################################

class dialog_dir_not_found ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Directory not found...", pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.CAPTION )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		bSizer4 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_staticText6 = wx.StaticText( self, wx.ID_ANY, u"Output directory not found.", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText6.Wrap( -1 )
		self.m_staticText6.SetFont( wx.Font( 10, 70, 90, 92, False, wx.EmptyString ) )
		
		bSizer4.Add( self.m_staticText6, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		self.m_staticText7 = wx.StaticText( self, wx.ID_ANY, u"Do you want to create it?", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText7.Wrap( -1 )
		bSizer4.Add( self.m_staticText7, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		gSizer1 = wx.GridSizer( 2, 2, 0, 0 )
		
		self.m_button_dir_ok = wx.Button( self, wx.ID_ANY, u"Ok", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer1.Add( self.m_button_dir_ok, 0, wx.ALL, 5 )
		
		self.m_button_dir_cancel = wx.Button( self, wx.ID_ANY, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer1.Add( self.m_button_dir_cancel, 0, wx.ALL, 5 )
		
		bSizer4.Add( gSizer1, 1, wx.EXPAND, 5 )
		
		self.SetSizer( bSizer4 )
		self.Layout()
		bSizer4.Fit( self )
		
		self.Centre( wx.BOTH )
	
	def __del__( self ):
		pass
	

