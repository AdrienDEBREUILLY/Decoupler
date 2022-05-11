import wx
from core.functional import check


class FilePicker(wx.FlexGridSizer):

    def __init__(self, parent, label, forme=None, isdir=False):
        self.isdir = isdir
        self.label = label
        self.parent = parent
        self.format = None
        if forme == "exl":
            self.format = "Excel File (*.xlsx,*.xls)|*.xlsx;*.xls"
        elif forme == "csv":
            self.format = "Excel File (*.csv)|*.csv"

        super().__init__(1, 3, 0, 0)
        super().AddGrowableCol(0, 3)
        super().AddGrowableCol(1, 8)
        super().AddGrowableCol(2, 1)
        txt = wx.StaticText(parent=self.parent, label=self.label, size=(150, 20))
        self.Add(txt)
        self.input = wx.TextCtrl(parent=self.parent, size=(300, 20))
        self.Add(self.input)
        self.btn = wx.Button(parent=self.parent, label="...", id=wx.ID_OK)
        self.btn.Bind(wx.EVT_BUTTON, self.on_click)
        self.Add(self.btn)

    def on_click(self, event: wx.Event):
        if self.isdir:
            picker = wx.DirDialog(
                parent=self.parent,
                message=self.label,
                style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
            )
        else:
            picker = wx.FileDialog(
                parent=self.parent,
                message=self.label,
                wildcard=self.format,
                style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
            )
        result = picker.ShowModal()
        if result == wx.ID_OK:
            path = picker.GetPath()
            self.input.SetValue(path)
        picker.Destroy()
        event.Skip()

    def get_value(self) -> str:
        return self.input.GetValue()


class MainFrame(wx.Frame):

    def __init__(self, title: str):
        super().__init__(None, title=title)
        self.SetBackgroundColour("#EEEEEE")
        self.master_box = wx.BoxSizer(wx.VERTICAL)
        self.master_box.SetMinSize((580, 300))

        inpt_txt = wx.StaticText(parent=self, label="INPUT")
        self.master_box.Add(inpt_txt, 0, wx.LEFT, 10)

        configuration_name_txt = wx.StaticText(parent=self, label="Configuration Name", size=(150, 20))
        self.master_box.Add(configuration_name_txt, 0, wx.LEFT, 10)
        self.configuration_name_input = wx.TextCtrl(parent=self, size=(300, 20))
        self.master_box.Add(self.configuration_name_input)

        self.master_box.Add(wx.StaticLine(self), 0, wx.ALL | wx.EXPAND, 5)

        cable_list_name_txt = wx.StaticText(parent=self, label="Cable List Name", size=(150, 20))
        self.master_box.Add(cable_list_name_txt, 0, wx.LEFT, 10)
        self.cable_list_name_input = wx.TextCtrl(parent=self, size=(300, 20))
        self.master_box.Add(self.cable_list_name_input)

        self.cable_list_input = FilePicker(parent=self, label="Cable List", forme="exl")
        self.master_box.Add(self.cable_list_input, 0, wx.LEFT, 10)

        self.global_path_input = FilePicker(parent=self, label="Global Path", forme="exl")
        self.master_box.Add(self.global_path_input, 0, wx.LEFT, 10)

        self.dec_room_list_input = FilePicker(parent=self, label="Decoupling Room List", forme="csv")
        self.master_box.Add(self.dec_room_list_input, 0, wx.LEFT, 10)

        pattern_list_name_txt = wx.StaticText(parent=self, label="Pattern List Name", size=(150, 20))
        self.master_box.Add(pattern_list_name_txt, 0, wx.LEFT, 10)
        self.pattern_list_name_input = wx.TextCtrl(parent=self, size=(300, 20))
        self.master_box.Add(self.pattern_list_name_input)

        self.dec_pattern_list_input = FilePicker(parent=self, label="Decoupling Pattern List", forme="exl")
        self.master_box.Add(self.dec_pattern_list_input, 0, wx.LEFT, 10)

        self.master_box.Add(wx.StaticLine(self), 0, wx.ALL | wx.EXPAND, 5)

        outp_txt = wx.StaticText(parent=self, label="OUTPUT")
        self.master_box.Add(outp_txt, 0, wx.LEFT, 10)

        output_grid = wx.FlexGridSizer(1, 2, 0, 0)

        self.folder_path_output = FilePicker(parent=self, label="Output Folder", isdir=True)
        self.master_box.Add(self.folder_path_output, 0, wx.LEFT, 10)

        file_name_txt = wx.StaticText(parent=self, label="File Name", size=(150, 20))
        output_grid.Add(file_name_txt)
        self.file_name_output = wx.TextCtrl(parent=self, size=(300, 20))
        output_grid.Add(self.file_name_output)

        self.master_box.Add(output_grid, 0, wx.LEFT, 10)

        self.btn = wx.Button(parent=self, label="launch", id=wx.ID_OK)
        self.btn.Bind(wx.EVT_BUTTON, self.on_click)
        self.master_box.Add(self.btn, 0, wx.LEFT, 425)

        self.SetSizerAndFit(self.master_box)

    def on_click(self, event: wx.Event):
        # creation !!!
        progress_dialog = wx.ProgressDialog("Decoupleur", "",
                                            maximum=11,
                                            parent=self,
                                            style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE)
        conf_name = self.configuration_name_input.GetValue()
        cable_list_name = self.cable_list_name_input.GetValue()
        cable_list = self.cable_list_input.get_value()
        global_path = self.global_path_input.get_value()
        room_list = self.dec_room_list_input.get_value()
        pattern_list_name = self.pattern_list_name_input.GetValue()
        decoupling_pattern_list = self.dec_pattern_list_input.get_value()
        output_folder = self.folder_path_output.get_value()
        file_name = self.file_name_output.GetValue()
        status, message = check(conf_name, cable_list_name, cable_list, global_path, room_list, pattern_list_name,
                                decoupling_pattern_list, output_folder, file_name, progress_dialog)
        # destruction!!!
        progress_dialog.Close()
        progress_dialog.Destroy()
        # todo close session database
        if status:
            display_information(self.btn.Parent, message)
        else:
            if type(message) == KeyError:
                message = f"Key Error: '{message.args[0]}' is not valid"
            display_warning(self.btn.Parent, message)
        event.Skip()


#   Information
def display_information(parent, message, title=None):
    header = "INFO"
    if title is not None:
        header += f": {title}"
    return display_ok_box(parent, message, header, wx.ICON_INFORMATION)


#   Warning
def display_warning(parent, message, title=None):
    header = "WARNING"
    if title is not None:
        header += f": {title}"
    return display_ok_box(parent, message, header, wx.ICON_EXCLAMATION)


def display_ok_box(parent, message, caption, style=wx.DEFAULT_DIALOG_STYLE, ok_label="OK"):
    style |= wx.OK | wx.OK_DEFAULT
    dlg = wx.MessageDialog(parent, message, caption, style=style)
    dlg.SetOKLabel(ok_label)
    result = dlg.ShowModal()
    return result == wx.ID_OK


def main(title: str):
    app = wx.App()
    main_frame = MainFrame(title)
    main_frame.Show(True)
    app.MainLoop()
