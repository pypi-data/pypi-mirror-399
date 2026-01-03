# exedash/core.py

import pandas as pd
import xlsxwriter
from datetime import datetime
import os

class ExcelDashboard:
    """
    A powerful class to turn any Pandas DataFrame into a stylish Excel Dashboard
    with charts and a dynamic footer.
    """

    def __init__(self, df: pd.DataFrame, report_title: str = "Data Dashboard", filename: str = "dashboard.xlsx"):
        """
        Initialize the Dashboard.

        :param df: The pandas DataFrame to visualize.
        :param report_title: The main title of the dashboard.
        :param filename: The output Excel filename.
        """
        self.df = df
        self.title = report_title
        self.filename = filename
        self.generation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Ensure output directory exists
        self.output_dir = "reports"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        self.full_path = os.path.join(self.output_dir, self.filename)

    def _create_formats(self, workbook):
        """Define Excel styles."""
        fmt_bold = workbook.add_format({'bold': True, 'font_size': 12})
        fmt_title = workbook.add_format({'bold': True, 'font_size': 20, 'font_color': '#2C3E50'})
        fmt_header = workbook.add_format({'bold': True, 'bg_color': '#34495E', 'font_color': 'white', 'border': 1})
        fmt_footer = workbook.add_format({'font_size': 9, 'italic': True, 'font_color': 'gray'})
        fmt_currency = workbook.add_format({'num_format': '$#,##0.00'})
        return fmt_bold, fmt_title, fmt_header, fmt_footer, fmt_currency

    def _detect_chart_type(self, col_name):
        """Heuristic to guess the best chart for a numeric column."""
        dtype = self.df[col_name].dtype
        
        if pd.api.types.is_numeric_dtype(dtype):
            # If it's a float with many unique values, it might be a distribution or value
            if pd.api.types.is_float_dtype(dtype) and self.df[col_name].nunique() > 10:
                return 'histogram' # or scatter if paired with another number
            return 'bar' # Default for numbers
        
        if pd.api.types.is_datetime64_any_dtype(dtype):
            return 'line'
        
        return 'pie' # Categorical strings default to pie

    def generate(self):
        """Generate the Excel file with charts and footer."""
        
        # 1. Create Workbook
        writer = pd.ExcelWriter(self.full_path, engine='xlsxwriter')
        workbook = writer.book
        worksheet = writer.sheets['Sheet1']
        
        # Styles
        fmt_bold, fmt_title, fmt_header, fmt_footer, fmt_currency = self._create_formats(workbook)

        # 2. Write Title
        worksheet.merge_range('A1:F1', self.title, fmt_title)
        worksheet.write('A2', f"Generated on: {self.generation_time}", fmt_bold)
        
        # 3. Write DataFrame
        start_row = 4
        worksheet.write_row(start_row, 0, self.df.columns, fmt_header)
        
        # Write data without index
        for r_idx, row in enumerate(self.df.itertuples(index=False)):
            worksheet.write_row(start_row + 1 + r_idx, 0, row)

        # 4. Auto-Generate Charts
        chart_row = start_row + len(self.df) + 4
        
        numeric_cols = self.df.select_dtypes(include=['number']).columns.tolist()
        
        if not numeric_cols:
            print("⚠️ No numeric columns found. Skipping charts.")
        else:
            for col in numeric_cols:
                # Find a label column (first non-numeric)
                label_col = None
                for c in self.df.columns:
                    if c != col and self.df[c].dtype == 'object':
                        label_col = c
                        break
                
                # If no string label, use index or date
                if not label_col:
                    if 'date' in self.df.columns:
                        label_col = 'date'
                    else:
                        label_col = self.df.columns[0]

                # Define Chart
                chart_type = self._detect_chart_type(col)
                
                if chart_type == 'line' and label_col:
                    chart = workbook.add_chart({'type': 'line'})
                    chart.add_series({
                        'name':       f'=Sheet1!${self._get_col_letter(self.df.columns.get_loc(col))}${start_row+1}',
                        'categories': f'=Sheet1!${self._get_col_letter(self.df.columns.get_loc(label_col))}${start_row+1}:${self._get_col_letter(self.df.columns.get_loc(label_col))}${start_row+len(self.df)}',
                        'values':     f'=Sheet1!${self._get_col_letter(self.df.columns.get_loc(col))}${start_row+1}:${self._get_col_letter(self.df.columns.get_loc(col))}${start_row+len(self.df)}',
                    })
                elif chart_type == 'bar':
                    chart = workbook.add_chart({'type': 'column'})
                    chart.add_series({
                        'name':       f'=Sheet1!${self._get_col_letter(self.df.columns.get_loc(col))}${start_row}',
                        'categories': f'=Sheet1!${self._get_col_letter(self.df.columns.get_loc(label_col))}${start_row+1}:${self._get_col_letter(self.df.columns.get_loc(label_col))}${start_row+len(self.df)}',
                        'values':     f'=Sheet1!${self._get_col_letter(self.df.columns.get_loc(col))}${start_row+1}:${self._get_col_letter(self.df.columns.get_loc(col))}${start_row+len(self.df)}',
                    })
                else:
                    continue # Skip if logic fails

                chart.set_title({'name': f'{col} by {label_col}'})
                chart.set_size({'width': 600, 'height': 350})
                worksheet.insert_chart(f'A{chart_row}', chart)
                chart_row += 20 # Move down for next chart

        # 5. THE POWERFUL FOOTER ⚡
        footer_text = f"Powered By louati Mahdi"
        last_row = chart_row + 5 if numeric_cols.any() else start_row + len(self.df) + 5
        
        worksheet.merge_range(last_row, 0, last_row, 5, footer_text, fmt_footer)
        worksheet.set_row(last_row, 30) # Give it height

        # 6. Autofit columns for readability
        for i, col in enumerate(self.df.columns):
            worksheet.set_column(i, i, max(15, len(str(col)) + 2))

        writer.close()
        print(f"✅ Dashboard generated successfully at: {self.full_path}")

    def _get_col_letter(self, idx):
        """Convert 0-based index to Excel letter (0->A, 1->B)"""
        letter = ""
        while idx >= 0:
            letter = chr(idx % 26 + 65) + letter
            idx = idx // 26 - 1
        return letter