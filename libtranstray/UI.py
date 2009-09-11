import os.path
import threading

import dbus
import dbus.glib
import gobject
import glib
import gtk
import pynotify

import libtranstray
import libtranstray.gtrans as gtrans

class NetworkListener(gobject.GObject):

    SERVICE_NAME = "org.freedesktop.NetworkManager"
    SERVICE_PATH = "/org/freedesktop/NetworkManager"

    __gsignals__ =  { 
                "online": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, []),
                "offline": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [])
                }

    def __init__(self):
        gobject.GObject.__init__(self)
        self.online = False
        try:
                systemBus = dbus.SystemBus()
                proxy_obj = systemBus.get_object(NetworkListener.SERVICE_NAME,
                                                 NetworkListener.SERVICE_PATH)
                nm_interface = dbus.Interface(proxy_obj, NetworkListener.SERVICE_NAME)

                #magic number: aparently 3 == online
                self.online = int(nm_interface.state()) == 3
                
                nm_interface.connect_to_signal('DeviceNowActive', self.active_cb)
                nm_interface.connect_to_signal('DeviceNoLongerActive', self.inactive_cb)
        except dbus.DBusException, de:
                print "Error while connecting to NetworkManager: %s" % str(de)
                self.online = True

    def active_cb(self, path):
        self.online = True
        print "ONLINE"
        self.emit("online")

    def inactive_cb(self, path):
        print "OFFLINE"
        self.online = False
        self.emit("offline")

class TranslateThread(threading.Thread):
    def __init__(self, cb, frm, to, text):
        threading.Thread.__init__(self)
        self.cb = cb
        self.frm = frm
        self.to = to
        self.text = text

    def call_callback(self):
        self.cb(self.result)
        return False

    def run(self):
        try:
            self.result = gtrans.translate(self.frm, self.to, self.text)
            gobject.idle_add(self.call_callback)
        except gtrans.GTransError, e:
            print "TRANSLATION FAILED: %s" % e
        print "FINISHED"

class TrayIcon(gtk.StatusIcon):

    APP_NAME = "Trans"
    APP_DESCRIPTION = "Translate Stuff"
    APP_ICON = "translation-tray-icon"

    def __init__(self, languagefrom="de", languageto="en"):
        gtk.StatusIcon.__init__(self)

        self._langfrom = languagefrom
        self._langto = languageto

        if libtranstray.is_installed():
            self.set_from_icon_name(self.APP_ICON)
            gtk.window_set_default_icon_name(self.get_icon_name())
        else:
            self.set_from_file("%s.svg" % self.APP_ICON)
            gtk.window_set_default_icon(self.get_pixbuf())

        self.set_visible(True)
        self.connect('activate', self._on_activate)
        self.connect('popup-menu', self._on_popup_menu)

        self._create_right_menu()

        self._nl = NetworkListener()
        #monitor the selection clipboard
        self._clip_selection = gtk.clipboard_get("PRIMARY")

        pynotify.init(self.APP_NAME)

    def _create_right_menu(self):
        self._rmenu = gtk.Menu()
        prefs = gtk.ImageMenuItem(stock_id=gtk.STOCK_PREFERENCES)
        prefs.connect("activate", self._on_prefs_clicked)
        about = gtk.ImageMenuItem(stock_id=gtk.STOCK_ABOUT)
        about.connect("activate", self._on_about_clicked)
        quit = gtk.ImageMenuItem(stock_id=gtk.STOCK_QUIT)
        quit.connect("activate", self._on_exit_clicked)
        self._rmenu.add(prefs)
        self._rmenu.add(gtk.SeparatorMenuItem())
        self._rmenu.add(about)
        self._rmenu.add(quit)
        self._rmenu.show_all()

    def _on_popup_menu(self, status, button, time):
        self._rmenu.popup(None, None, gtk.status_icon_position_menu, button, time, self)

    def _on_activate(self, *args):
        if self._nl.online:
            #get the selected text
            self._clip_selection.request_text(self._clipboard_text_received)

    def _translation_finished(self, result):
        n = pynotify.Notification(
                "Translation",
                result
        )
        n.attach_to_status_icon(self)
        n.show()

    def _clipboard_text_received(self, clip, text, user_data):
        if text:
            t = TranslateThread(self._translation_finished, self._langfrom, self._langto, text)
            t.start()

    def _on_prefs_clicked(self, widget):
        def make_cb_label(store, label):
            hb = gtk.HBox(spacing=5)
            lbl = gtk.Label(label)
            lbl.props.xalign = 0.0
            hb.pack_start(lbl, expand=False)

            cb = gtk.ComboBox(store)
            cell = gtk.CellRendererText()
            cb.pack_start(cell, True)
            cb.add_attribute(cell, 'text', 0)

            hb.pack_start(cb, expand=True)
            return hb, cb, lbl

        def select_cb(cb, langcode):
            model = cb.get_model()
            selected = None

            iter_ = model.get_iter_root()
            while iter_:
                if model.get_value(iter_, 1) == langcode:
                    selected = iter_
                    break
                iter_ = model.iter_next(iter_)

            if selected:
                cb.set_active_iter(selected)

        s = gtk.ListStore( str, str )
        for name,code in gtrans.langs.items():
            s.append( (name, code) )

        dlg = gtk.Dialog(title="Preferences")
        dlg.add_button(gtk.STOCK_APPLY, gtk.RESPONSE_APPLY)
        dlg.vbox.props.spacing = 5
        dlg.props.default_width = 200

        lbl = gtk.Label("<b>Translate Selected Text</b>")
        lbl.props.xalign = 0.0
        lbl.props.use_markup = True
        dlg.vbox.pack_start(lbl)

        frm, frmcb, frmlbl = make_cb_label(s, "From")
        select_cb(frmcb, self._langfrom)
        dlg.vbox.pack_start(frm)

        to, tocb, tolbl = make_cb_label(s, "To")
        select_cb(tocb, self._langto)
        dlg.vbox.pack_start(to)

        sg = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
        sg.add_widget(frmlbl)
        sg.add_widget(tolbl)

        dlg.show_all()
        resp = dlg.run()

        if resp == gtk.RESPONSE_APPLY:
            self._langfrom = s.get_value(
                            frmcb.get_active_iter(),
                            1)
            self._langto = s.get_value(
                            tocb.get_active_iter(),
                            1)

        dlg.destroy()
                

    def _on_about_clicked(self, widget):
        dlg = gtk.AboutDialog()
        dlg.set_name(self.APP_NAME)
        dlg.set_comments(self.APP_DESCRIPTION)
        dlg.set_copyright("License: GPLv3")
        #dlg.set_website("http://nzjrs.github.com/facebook-notify/")
        #dlg.set_version("1.0")
        dlg.set_authors(("John Stowers",))
        #dlg.set_logo_icon_name(self._icon_name)
        dlg.run()
        dlg.destroy()

    def _on_exit_clicked(self, widget):
        gtk.main_quit()

