import openpyxl

def set_city():
    nameCites = []
    timeZoneCity = []
    latitudeCity = []
    longitudeCity= []
    wb = openpyxl.load_workbook(filename = "main_weather\\other_modules\\RU.xlsx", read_only=True)
    sheet = wb['Sheet']
    for i in range(1, sheet.max_row+1):
        nameCites.append(sheet[f'A{i}'].value)
        timeZoneCity.append(sheet[f'B{i}'].value)
        latitudeCity.append(sheet[f'C{i}'].value)
        longitudeCity.append(sheet[f'D{i}'].value)

    return nameCites,timeZoneCity,latitudeCity,longitudeCity 
nameCites,timeZoneCity,latitudeCity,longitudeCity = set_city()