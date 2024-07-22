import openpyxl


def set_city():
    nameCity = []
    wb = openpyxl.load_workbook(filename = "main_weather\\other_modules\\RU.xlsx", read_only=True)
    sheet = wb['Sheet']
    for i in range(1, sheet.max_row+1):
        nameCity.append(sheet[f'B{i}'].value)
    return nameCity
nameCity = set_city()