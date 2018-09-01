#!/usr/bin/env python
 
import wx
import sys
from wx.lib.floatcanvas import NavCanvas, Resources, FloatCanvas
from wx.lib.floatcanvas import FloatCanvas as FC
from wx.lib.floatcanvas.Utilities import BBox
 
import numpy as N
 
## here we create some new mixins:
 
class MovingObjectMixin:
    """
    Methods required for a Moving object
    """
    def GetOutlinePoints(self):
        BB = self.BoundingBox
        OutlinePoints = N.array( ( (BB[0,0], BB[0,1]), (BB[0,0], BB[1,1]),
                                    (BB[1,0], BB[1,1]), (BB[1,0], BB[0,1]),))
 
        return OutlinePoints
 
class ConnectorObjectMixin:
    """
    Mixin class for DrawObjects that can be connected with lines
 
    NOte that this versionony works for Objects that have an "XY" attribute:
      that is, one that is derived from XHObjectMixin.
    """
    def GetConnectPoint(self):
        return self.XY
 
class MovingBitmap(FC.ScaledBitmap, MovingObjectMixin, ConnectorObjectMixin):
    """
    ScaledBitmap Object that can be moved
    """
    ## All we need to do is is inherit from:
    ##      ScaledBitmap, MovingObjectMixin and ConnectorObjectMixin
    pass
 
class DrawFrame(wx.Frame):
    """
    A simple frame used for the Demo
    """
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
 
        self.CreateStatusBar()               
        # Add the Canvas
        Canvas = FloatCanvas.FloatCanvas(self, ProjectionFun = None, Debug = 0, BackgroundColor = "WHITE")
 
        self.Canvas = Canvas
 
        Canvas.Bind(FC.EVT_MOTION, self.OnMove )
        Canvas.Bind(FC.EVT_LEFT_UP, self.OnLeftUp )
 
        self.Bitmaps = []
        ## create the bitmaps first
        for Point in ((-100,-100), (55,1)):
            print Point
            btm = Resources.getMondrianImage()
            mbtm = MovingBitmap(btm, Point, btm.GetHeight(), Position='cc')
            self.Bitmaps.append((mbtm))
            Canvas.AddObject(mbtm)
 
        for bmp in self.Bitmaps:
            bmp.Bind(FC.EVT_FC_LEFT_DOWN, self.ObjectHit)
            print bmp.XY
 
        self.Show(True)
 
        self.add_again()
        # How can I get all the objects on the canvas?
        # print Canvas.GetObjects()
        # And for each object, can I get position?
 
        self.MoveObject = None
        self.Moving = False
 
    def add_again(self):
        print self.Canvas
        self.Canvas.ClearAll()
        print self.Canvas.HitDict
        for bmp in self.Bitmaps:
            print bmp
            self.Canvas.AddObject(bmp)
            bmp.Bind(FC.EVT_FC_LEFT_DOWN, self.ObjectHit)
            print self.Canvas._DrawList
            print self.Canvas.HitDict
 
        self.Show(True)
 
    def ObjectHit(self, object):
        if not self.Moving:
            print object.CalcBoundingBox()
            self.Moving = True
            self.StartPoint = object.HitCoordsPixel
            self.StartObject = self.Canvas.WorldToPixel(object.GetOutlinePoints())
            self.MoveObject = None
            self.MovingObject = object
 
    def OnMove(self, event):
        """
        Updates the status bar with the world coordinates
        and moves the object it is clicked on
        """
        self.SetStatusText("%.4f, %.4f"%tuple(event.Coords))
 
        if self.Moving:
            dxy = event.GetPosition() - self.StartPoint # Not start point, but prevoius move point.
            self.StartPoint = event.GetPosition()
            dxy = self.Canvas.ScalePixelToWorld(dxy)
            self.MovingObject.Move(dxy)
            self.Canvas.Draw(True)
 
    def OnLeftUp(self, event):
        if self.Moving:
            self.Moving = False
 
if __name__ == "__main__":
    app = wx.PySimpleApp(0)
    DrawFrame(None, -1, "FloatCanvas Moving Object App", wx.DefaultPosition, (500,500) )
    app.MainLoop()