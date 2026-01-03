import openpyxl
import unidecode

def get_first_column_from_all_sheets_function(excel_file):
    try:
        workbook = openpyxl.load_workbook(excel_file)
        data = {}
        for sheet_name in workbook.sheetnames:
            sheet = workbook[sheet_name]
            first_column_data = []
            counter = 0
            for cell in sheet['A']:
                if counter >= 2:
                    first_column_data.append(str(cell.value).upper())
                counter += 1
            data[str(sheet_name).upper()] = first_column_data
        return data
    except FileNotFoundError:
        print(f"Error: The file '{excel_file}' was not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None