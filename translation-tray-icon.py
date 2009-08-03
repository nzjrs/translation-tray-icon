#!/usr/bin/env python

import gobject
import gtk

from libtranstray.UI import TrayIcon

if __name__ == "__main__":
    gobject.threads_init()
    t = TrayIcon()
    gtk.main()
