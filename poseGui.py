import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class App(Gtk.Window):
    def __init__(self):
        super(App, self).__init__()
        
        self.set_title("HBox Layout App")
        self.set_size_request(640, 360)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        button = Gtk.Button("Start")
        button.connect("clicked", self.on_click_me_clicked)

        button1 = Gtk.Button("Deteksi")
        imageBox =  Gtk.Image()

        container = Gtk.Fixed()

        # 20 jarak kanan 30 karak atas
        container.put(button, 20, 30)
        container.put(button1, 100, 30)
        container.put(imageBox, 250, 60)
        
        # tambahkan layout hbox ke window
        self.add(container)
        
        self.connect("destroy", Gtk.main_quit)
        self.show_all()

    # 
    def on_click_me_clicked(self, button):
        print('"Click me" Button clik')
        
App()
Gtk.main()
