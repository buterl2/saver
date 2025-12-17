import win32com.client
from typing import Any, List, Tuple
import data_script.config.constants as constant

class SAPSession():
    def __init__(self, session: int = 0, connection: int = 0) -> None:
        sap_gui = win32com.client.GetObject("SAPGUI")
        app = sap_gui.GetScriptingEngine
        self.connection = app.Children(connection)
        self.session = self.connection.Children(session)

    def __getattr__(self, name: str) -> Any:
        return getattr(self.session, name)

    def table(self, table_name: str) -> None:
        self.findById("wnd[0]/usr/ctxtP_TAB").text = table_name
        self.findById("wnd[0]/tbar[1]/btn[8]").press()

    def checkbox_selection(self, selection: List[Tuple[int, List[int]]]) -> None:
        self.findById("wnd[0]/mbar/menu[3]/menu[2]").select()
        vertical_scroll: int = 0
        for scroll_element, checkbox_column in selection:
            vertical_scroll += scroll_element
            if scroll_element > 0:
                self.findById("wnd[1]/usr").verticalScrollbar.position = vertical_scroll

            for col in checkbox_column:
                self.findById(f"wnd[1]/usr/chk[2,{col}]").selected = True
        self.findById("wnd[1]/tbar[0]/btn[0]").press()

    def save_to_folder(self, folder: str, filename: str) -> None:
        self.findById("wnd[0]/tbar[1]/btn[45]").press()
        self.findById("wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[1,0]").select()
        self.findById("wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[1,0]").setFocus()
        self.findById("wnd[1]/tbar[0]/btn[0]").press()
        self.findById("wnd[1]/usr/ctxtDY_PATH").text = f"{constant.OUTPUT_PATH}/{folder}"
        self.findById("wnd[1]/usr/ctxtDY_FILENAME").text = f"{filename}.txt"
        self.findById("wnd[1]/usr/ctxtDY_FILE_ENCODING").text = constant.ENCODING_SAP
        self.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 8
        self.findById("wnd[1]/tbar[0]/btn[11]").press()

    def vl06f_dashboard(self, variant_name: str) -> None:
        """Handles VL06F transaction variant selection and configuration"""
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