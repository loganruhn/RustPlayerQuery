import requests
import json
import wx
import sys
import cPickle as pickle
from ObjectListView import ObjectListView, ColumnDefn

class ListPanel(wx.Panel):
    def __init__(self, parent, statlist):
        self.statlist = statlist
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.listview = listview = ObjectListView(self, wx.ID_ANY, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.listview.cellEditMode = ObjectListView.CELLEDIT_SINGLECLICK
        self.setBooks()
        sizer.Add(self.listview, 1, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(sizer)

    def setBooks(self, data=None):
        self.listview.SetColumns([
            ColumnDefn('Stat', 'left', 300, 'stat'),
            ColumnDefn('Value', 'right', 120, 'value'),
        ])
        self.listview.SetObjects(self.statlist)

class StatBook(wx.Choicebook):
    def __init__(self, parent):
        wx.Choicebook.__init__(self, parent, wx.ID_ANY)
        categories = ['Combat', 'Arrows', 'Bullets', 'Harvesting']
        for cat in categories:
            if cat is 'Combat':
                self.statlist = DataInput.combat
                combattab = ListPanel(self, self.statlist)
                self.AddPage(combattab, 'Combat')
            elif cat is 'Arrows':
                self.statlist = DataInput.arrows
                arrowstab = ListPanel(self, self.statlist)
                self.AddPage(arrowstab, 'Arrows')
            elif cat is 'Bullets':
                self.statlist = DataInput.bullets
                bulletstab = ListPanel(self, self.statlist)
                self.AddPage(bulletstab, 'Bullets')
            elif cat is 'Harvesting':
                self.statlist = DataInput.harvesting
                harvesttab = ListPanel(self, self.statlist)
                self.AddPage(harvesttab, 'Harvesting')

class DataInput(wx.Dialog):
    combat = []
    arrows = []
    bullets = []
    harvesting = []
    def __init__(self):
        self.apikey = apikey = ''
        self.steamid = steamid = ''
        self.url = url = 'http://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/?appid=252490&key={0}&steamid={1}'.format(apikey, steamid)
        wx.Dialog.__init__(self, None, title="Please enter player information")
        iconfile = "RustLogo.ico"
        icon = wx.Icon(iconfile, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)
        sizer = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(self, -1, "Please enter your SteamAPI key in the first box. \nEnter the 64bit SteamID of the player you want to query in the second box.")
        sizer.Add(label, 0, wx.ALIGN_CENTER|wx.ALL, 5)
        box = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, -1, "SteamAPI: ")
        box.Add(label, 0, wx.ALIGN_CENTER|wx.ALL, 5)
        self.api_input = api_input = wx.TextCtrl(self, -1, "", size=(80, -1))
        box.Add(api_input, 1, wx.ALIGN_CENTER|wx.ALL, 5)
        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        box = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, -1, "64bit SteamID: ")
        box.Add(label, 0, wx.ALIGN_CENTER|wx.ALL, 5)
        self.steamid_input = steamid_input =  wx.TextCtrl(self, -1, "", size=(80, -1))
        box.Add(steamid_input, 1, wx.ALIGN_CENTER|wx.ALL, 5)
        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)
        btnsizer = wx.StdDialogButtonSizer()

        if wx.Platform != "__WXMSW__":
            btn = wx.ContextHelpButton(self)
            btnsizer.AddButton(btn)

        btn1 = wx.Button(self, wx.ID_OK)
        btn1.SetDefault()
        btnsizer.AddButton(btn1)
        self.Bind(wx.EVT_BUTTON, self.OnUpdate, btn1)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        btn2 = wx.Button(self, wx.ID_CANCEL)
        btnsizer.AddButton(btn2)
        self.Bind(wx.EVT_BUTTON, self.OnClose, btn2)
        btnsizer.Realize()
        sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        self.SetSizer(sizer)
        sizer.Fit(self)

    def OnUpdate(self, event):
        self.apikey = apikey = self.api_input.GetValue()
        self.steamid = steamid = self.steamid_input.GetValue()
        self.url = url = 'http://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/?appid=252490&key={0}&steamid={1}'.format(apikey, steamid)
        query = requests.get(url)
        plist = query.json()
        statlist = plist['playerstats']['stats']
        with open('categories.pickle', 'rb') as cuntwrench:
            categorylist = pickle.load(cuntwrench)
        with open('tabnames.pickle', 'rb') as dickspanner:
            propernames = pickle.load(dickspanner)
        rawstats = {}
        for x in statlist:
            name = x['name'].encode('utf-8').replace('.', '_')
            value = x['value']
            rawstats[name] = value
        for key, value in rawstats.iteritems():
            if any(key in x for x in categorylist['Combat']):
                ls = {}
                cname = propernames[key]
                ls['value'] = value
                ls['stat'] = cname
                self.combat.append(ls)
            elif any(key in x for x in categorylist['Arrows']):
                ls = {}
                cname = propernames[key]
                ls['value'] = value
                ls['stat'] = cname
                self.arrows.append(ls)
            elif any(key in x for x in categorylist['Bullets']):
                ls = {}
                cname = propernames[key]
                ls['value'] = value
                ls['stat'] = cname
                self.bullets.append(ls)
            elif any(key in x for x in categorylist['Harvesting']):
                ls = {}
                cname = propernames[key]
                ls['value'] = value
                ls['stat'] = cname
                self.harvesting.append(ls)
        MainWindow().Show()
        self.Hide()

    def OnClose(self, event):
        sys.exit(1)

class MainWindow(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, title="Rust Player Query", size=(490, 500))
        iconFile = "RustLogo.ico"
        icon1 = wx.Icon(iconFile, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon1)
        panel = wx.Panel(self)

        book = StatBook(panel)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        sizer.Add(book, 1, wx.ALL|wx.EXPAND, 5)
        panel.SetSizer(sizer)
        self.Layout()
        self.Show()

    def OnClose(self, event):
        sys.exit(1)

class MainApp(wx.App):
    def OnInit(self):
        self.frame = DataInput(None, -1)
        self.frame.Show(True)
        self.SetTopWindow(self.frame)
        return True

    if __name__ == '__main__':
        app = wx.App(0)
        frame = DataInput().Show()
        app.MainLoop()
    sys.exit(1)

