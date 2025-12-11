import win32com.client
import data_extraction.config.config as config
from data_extraction.utils import default_logger as logger

class SAPSession():
    def __init__(self, session=0, connection=0):
        sap_gui = win32com.client.GetObject("SAPGUI")
        application = sap_gui.GetScriptingEngine
        self.connection = application.Children(connection)
        self.session = self.connection.Children(session)
    
    def __getattr__(self, name):
        return getattr(self.session, name)
    
    def enter_table(self, table_name):
        self.findById("wnd[0]/usr/ctxtP_TAB").text = table_name
        self.findById("wnd[0]/tbar[1]/btn[8]").press()
    
    def checkbox_selection(self, selection):
        self.findById("wnd[0]/mbar/menu[3]/menu[2]").select()
        vertical_scroll = 0
        for scroll_element, checkbox_column in selection:
            vertical_scroll += scroll_element
            if scroll_element > 0:
                self.findById("wnd[1]/usr").verticalScrollbar.position = vertical_scroll

            for col in checkbox_column:
                self.findById(f"wnd[1]/usr/chk[2,{col}]").selected = True
        self.findById("wnd[1]/tbar[0]/btn[0]").press()

    def save_to_folder(self, filename):
        self.findById("wnd[0]/tbar[1]/btn[45]").press()
        self.findById("wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[1,0]").select()
        self.findById("wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[1,0]").setFocus()
        self.findById("wnd[1]/tbar[0]/btn[0]").press()
        self.findById("wnd[1]/usr/ctxtDY_PATH").text = config.OUTPUT_PATH
        self.findById("wnd[1]/usr/ctxtDY_FILENAME").text = f"{filename}.txt"
        self.findById("wnd[1]/usr/ctxtDY_FILE_ENCODING").text = config.ENCODING
        self.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 8
        self.findById("wnd[1]/tbar[0]/btn[11]").press()

    def vl06f_dashboard(self, variant_name):
        self.findById("wnd[0]/tbar[1]/btn[17]").press()
        self.findById("wnd[1]/usr/txtENAME-LOW").text = variant_name
        self.findById("wnd[1]/usr/txtENAME-LOW").caretPosition = 7
        self.findById("wnd[1]/tbar[0]/btn[8]").press()
        self.findById("wnd[1]/usr/cntlALV_CONTAINER_1/shellcont/shell").selectedRows = "0"
        self.findById("wnd[1]/usr/cntlALV_CONTAINER_1/shellcont/shell").doubleClickCurrentCell()
        self.findById("wnd[0]/usr/ctxtIT_WADAT-LOW").setFocus()
        self.findById("wnd[0]/usr/ctxtIT_WADAT-LOW").caretPosition = 5
        self.findById("wnd[0]/usr/btn%_IT_WADAT_%_APP_%-VALU_PUSH").press()
        self.findById("wnd[1]/tbar[0]/btn[16]").press()
        self.findById("wnd[1]/tbar[0]/btn[8]").press()
        self.findById("wnd[0]/tbar[1]/btn[8]").press()
        self.findById("wnd[0]/usr/cntlGRID1/shellcont/shell").setCurrentCell(-1,"WADAT")
        self.findById("wnd[0]/usr/cntlGRID1/shellcont/shell").selectColumn("WADAT")
        self.findById("wnd[0]/tbar[1]/btn[40]").press()

    def get_variant_name(self, variant_name):
        self.findById("wnd[0]/tbar[1]/btn[17]").press()
        self.findById("wnd[1]/usr/txtV-LOW").text = variant_name
        self.findById("wnd[1]/usr/txtENAME-LOW").text = ""
        self.findById("wnd[1]/usr/txtV-LOW").caretPosition = 3
        self.findById("wnd[1]/tbar[0]/btn[8]").press()
    