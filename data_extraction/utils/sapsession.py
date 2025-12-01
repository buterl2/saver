import win32com.client
import data_extraction.config.config as config
from data_extraction.utils import default_logger as logger

class SAPSession():
    def __init__(self, session=0, connection=0):
        sap_gui = win32com.client.GetObject("SAPGUI")
        application = sap_gui.GetScriptingEngine
        self.connection = application.Children(connection)
        self.session = self.connection.Children(session)
        logger.info(f"Connected successfully to connection: {connection} and session: {session}")
    
    def __getattr__(self, name):
        return getattr(self.session, name)
    
    def enter_table(self, table_name):
        self.findById("wnd[0]/usr/ctxtP_TAB").text = table_name
        self.findById("wnd[0]/tbar[1]/btn[8]").press()
        logger.info(f"{table_name} successfully started")
    
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
        logger.info("Fields selection successfully done")

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
        logger.info(f"{filename} successfully saved")