from muttlib.gsheetsconn import GSheetsClient
from pathlib import Path
import pandas as pd

class GoogleSheetsClient:
    def __init__(self, gsheets_json: str, gsheets_id: str) -> None:
        print('Conectando a Google Sheets...', end='')
        self.client = GSheetsClient(Path(gsheets_json))
        self.gsheets_id = gsheets_id
        print('Ok')

    def new_sheet(self, gsheet_name: str) -> None:
        """
        Creates a new worksheet
        """
        spread = self.client.get_spreadsheet(self.gsheets_id, gsheet_name)

    def write_at_bottom(self, gsheet_name: str, data: pd.DataFrame) -> None:
        """
        Writes 'data' DataFrame into the last available row of column A
        """
        # Obtener la ultima fila en blanco
        try:
            row_df = self.client.to_frame(
                spreadsheet=self.gsheets_id,
                worksheet=gsheet_name,
                first_cell_loc='A1',
                num_header_rows=0
            )
        except Exception as e:
            print('ERROR: no se pudo leer del gsheets.\n', e)
            return

        # Dejamos una fila mas para el encabezado
        row = int(row_df.iloc[0, 0]) + 2

        try:
            self.client.insert_from_frame(
                df=data, 
                spreadsheet=self.gsheets_id, 
                index=False, 
                header=False, 
                first_cell_loc=f'A{row}', 
                worksheet=gsheet_name, 
                preclean_sheet=False, 
                freeze_headers=False
            )
        except Exception:
            print('ERROR: no se pudo actualizar la info en gsheets.')
