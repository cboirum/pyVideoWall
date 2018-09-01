#!/usr/bin/python
# Print some information about the X environment, the monitor setup, currently active window and cursor position
import gtk.gdk

screen = gtk.gdk.screen_get_default()
print "X default screen size: %d x %d" % (screen.get_width(), screen.get_height())
print "xid of root window: %d" % screen.get_root_window().xid

monitors = int(screen.get_n_monitors())
print "== %d monitors ==" % monitors
for m in range(0, monitors):
    print " - geometry of monitor %d: %s" % (m, screen.get_monitor_geometry(m))

window = screen.get_active_window()
win_x, win_y, win_w, win_h, win_bit_depth = window.get_geometry()
print "active window on monitor: %d" % screen.get_monitor_at_point((win_x+(win_w/2)),(win_y+(win_h/2)))
print "window geometry (x,y,w,h): %d, %d, %d, %d" % (win_x,win_y,win_w,win_h)

display = gtk.gdk.display_get_default()
pointer = display.get_pointer()
print "cursor position (x, y): %d, %d" % (pointer[1], pointer[2])
print "cursor on monitor: %d" % screen.get_monitor_at_point(pointer[1],pointer[2])