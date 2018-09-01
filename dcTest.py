#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
ZetCode wxPython tutorial 

This program draws a line in 
a paint event

author: Jan Bodnar
website: zetcode.com 
last edited: November 2010
"""

import wx

class Example(wx.Frame):
    def __init__(self, parent, title):
        super(Example, self).__init__(parent, title=title, 
            size=(250, 150))

        self.Bind(wx.EVT_PAINT, self.OnPaint)

        self.Centre()
        self.Show()

    def OnPaint(self, e):
        dc = wx.PaintDC(self)
        dc.DrawBitmap()
        #dc.DrawLine(50, 60, 190, 60)

if __name__ == '__main__':
    app = wx.App()
    Example(None, 'Line')
    app.MainLoop()