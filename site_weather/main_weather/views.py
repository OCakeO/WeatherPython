from django.shortcuts import render
from .__init__ import nameCites,timeZoneCity,latitudeCity,longitudeCity 
from .other_modules.weather import weather_in_city
hourly_dataframe ={} 
daily_data = {}

def index(request):
    try:
        search_input = request.GET['search-input']
        if search_input in nameCites:
            index = nameCites.index(search_input)
            hourly_dataframe, daily_data = weather_in_city(latitudeCity[index], longitudeCity[index])
            daily_list = zip(daily_data["date"], daily_data['temperature_2m_max'], daily_data['temperature_2m_min'], hourly_dataframe)
            
            context = {
                'nameCity' : f"в г.{search_input}",
                'cities' : nameCites,
                'days' :  daily_list
            }
            return render(request, 'home/weather.html', context)
        else:
            context = {
                'cities' : nameCites,
                'noCity' : "Такого города нет"
            }
            return render(request, 'home/weather.html', context)
    except:
        context = {
            'nameCity' : "",
            'cities' : nameCites,
        }
        
        return render(request, 'home/weather.html', context)
