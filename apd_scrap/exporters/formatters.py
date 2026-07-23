"""
Formateador de Excel para exportación de datos.

Este módulo proporciona funcionalidades para formatear hojas de Excel
con estilos profesionales, ajustes automáticos y mejoras visuales.
"""

from openpyxl.styles import Font, Alignment, PatternFill, Border, Side, NamedStyle
from openpyxl.utils import get_column_letter


class ExcelFormatter:
    """
    Clase para formatear hojas de Excel con estilos profesionales.
    
    Proporciona métodos para formatear encabezados, ajustar columnas,
    aplicar estilos condicionales y mejorar la apariencia visual.
    """
    
    def __init__(self):
        """Inicializa el formateador con estilos predefinidos."""
        self._setup_styles()
    
    def _setup_styles(self):
        """Configura estilos predefinidos para formateo."""
        # Fuente para encabezados
        self.header_font = Font(
            name='Arial',
            size=11,
            bold=True,
            color='FFFFFF'  # Blanco
        )
        
        # Relleno para encabezados
        self.header_fill = PatternFill(
            start_color='366092',  # Azul oscuro
            end_color='366092',
            fill_type='solid'
        )
        
        # Alineación general
        self.center_alignment = Alignment(
            horizontal='center',
            vertical='center',
            wrap_text=True
        )
        
        # Alineación izquierda
        self.left_alignment = Alignment(
            horizontal='left',
            vertical='center',
            wrap_text=True
        )
        
        # Borde delgado
        self.thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        # Borde grueso
        self.thick_border = Border(
            left=Side(style='medium'),
            right=Side(style='medium'),
            top=Side(style='medium'),
            bottom=Side(style='medium')
        )
    
    def format_headers(self, sheet, sheet_name: str):
        """
        Formatea los encabezados de una hoja de Excel.
        
        Args:
            sheet: Hoja de Excel a formatear
            sheet_name: Nombre de la hoja para referencia
        """
        if sheet.max_row < 1:
            return
            
        # Formatear fila de encabezados
        for cell in sheet[1]:  # Primera fila
            cell.font = self.header_font
            cell.fill = self.header_fill
            cell.alignment = self.center_alignment
            cell.border = self.thin_border
        
        # Congelar paneles
        sheet.freeze_panes = 'A2'
        
        # Añadir título de hoja
        if sheet_name:
            sheet.title = sheet_name
    
    def format_summary_headers(self, sheet):
        """
        Formatea encabezados en la hoja de resumen con estilo especial.
        
        Args:
            sheet: Hoja de Excel a formatear
        """
        if sheet.max_row < 1:
            return
            
        # Formatear encabezados principales (fila 1)
        for cell in sheet[1]:
            cell.font = Font(name='Arial', size=14, bold=True, color='366092')
            cell.alignment = self.center_alignment
            cell.border = self.thick_border
        
        # Formatear encabezados secundarios (fila 3, 5, 7, etc.)
        for row_idx in [3, 5, 7, 9, 11, 13, 15]:  # Filas de categorías
            if row_idx <= sheet.max_row:
                for cell in sheet[row_idx]:
                    cell.font = Font(name='Arial', size=12, bold=True, color='366092')
                    cell.alignment = self.left_alignment
                    cell.border = self.thin_border
    
    def format_metadata_headers(self, sheet):
        """
        Formatea encabezados en la hoja de metadatos.
        
        Args:
            sheet: Hoja de Excel a formatear
        """
        if sheet.max_row < 1:
            return
            
        # Formatear encabezados principales
        for cell in sheet[1]:
            cell.font = Font(name='Arial', size=14, bold=True, color='366092')
            cell.alignment = self.center_alignment
            cell.border = self.thick_border
        
        # Formatear etiquetas de metadatos
        for row_idx in range(3, sheet.max_row + 1, 2):  # Filas impares
            if row_idx <= sheet.max_row:
                # Primera columna (etiquetas)
                for cell in sheet[row_idx]:
                    cell.font = Font(name='Arial', size=11, bold=True)
                    cell.alignment = self.left_alignment
                    cell.border = self.thin_border
                
                # Segunda columna (valores)
                if row_idx + 1 <= sheet.max_row:
                    for cell in sheet[row_idx + 1]:
                        cell.alignment = self.left_alignment
                        cell.border = self.thin_border
    
    def auto_adjust_columns(self, sheet, max_width: int = 50):
        """
        Ajusta automáticamente el ancho de las columnas.
        
        Args:
            sheet: Hoja de Excel a ajustar
            max_width: Ancho máximo para columnas
        """
        for column in sheet.columns:
            # Calcular ancho basado en contenido
            max_length = 0
            column_letter = get_column_letter(column[0].column)
            
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            
            # Aplicar ancho con límite
            adjusted_width = min(max_length + 2, max_width)
            sheet.column_dimensions[column_letter].width = adjusted_width
    
    def format_numeric_columns(self, sheet, numeric_columns: list):
        """
        Formatea columnas numéricas con formato apropiado.
        
        Args:
            sheet: Hoja de Excel a formatear
            numeric_columns: Lista de nombres de columnas numéricas
        """
        # Mapeo de nombres de columnas a índices
        header_row = sheet[1]
        column_map = {cell.value: cell.column for cell in header_row}
        
        for col_name in numeric_columns:
            if col_name in column_map:
                col_idx = column_map[col_name]
                
                # Aplicar formato numérico
                for row_idx in range(2, sheet.max_row + 1):
                    cell = sheet.cell(row=row_idx, column=col_idx)
                    try:
                        if cell.value is not None:
                            cell.number_format = '#,##0.00'
                    except:
                        pass
    
    def format_date_columns(self, sheet, date_columns: list):
        """
        Formatea columnas de fecha con formato apropiado.
        
        Args:
            sheet: Hoja de Excel a formatear
            date_columns: Lista de nombres de columnas de fecha
        """
        # Mapeo de nombres de columnas a índices
        header_row = sheet[1]
        column_map = {cell.value: cell.column for cell in header_row}
        
        for col_name in date_columns:
            if col_name in column_map:
                col_idx = column_map[col_name]
                
                # Aplicar formato de fecha
                for row_idx in range(2, sheet.max_row + 1):
                    cell = sheet.cell(row=row_idx, column=col_idx)
                    try:
                        if cell.value is not None:
                            cell.number_format = 'DD/MM/YYYY'
                    except:
                        pass
    
    def add_filter_and_sort(self, sheet):
        """
        Añade filtros y ordenamiento a la hoja de Excel.
        
        Args:
            sheet: Hoja de Excel a la que añadir filtros
        """
        if sheet.max_row > 1 and sheet.max_column > 1:
            # Añadir filtro a la primera fila
            sheet.auto_filter.ref = f"A1:{get_column_letter(sheet.max_column)}{sheet.max_row}"
    
    def highlight_alternate_rows(self, sheet, start_row: int = 2):
        """
        Resalta filas alternas para mejor legibilidad.
        
        Args:
            sheet: Hoja de Excel a formatear
            start_row: Fila desde comenzar el resaltado
        """
        if sheet.max_row < start_row:
            return
            
        # Color alternante suave
        light_gray = 'F5F5F5'
        
        for row_idx in range(start_row, sheet.max_row + 1):
            if row_idx % 2 == 0:  # Filas pares
                for cell in sheet[row_idx]:
                    cell.fill = PatternFill(start_color=light_gray, end_color=light_gray, fill_type='solid')
    
    def create_summary_row(self, sheet, summary_data: dict, start_row: int):
        """
        Crea una fila de resumen con formato especial.
        
        Args:
            sheet: Hoja de Excel
            summary_data: Diccionario con datos de resumen
            start_row: Fila donde comenzar el resumen
        """
        for i, (label, value) in enumerate(summary_data.items(), start=start_row):
            # Etiqueta en negrita
            sheet.cell(row=i, column=1).font = Font(bold=True)
            sheet.cell(row=i, column=1).value = label
            
            # Valor con formato
            sheet.cell(row=i, column=2).value = value
            sheet.cell(row=i, column=2).alignment = self.right_alignment
        
        # Añadir borde alrededor del resumen
        for i in range(start_row, start_row + len(summary_data)):
            for j in range(1, 3):
                sheet.cell(row=i, column=j).border = self.thick_border