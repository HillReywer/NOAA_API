import requests
import json
import matplotlib.pyplot as plt

# Отправка запроса на API и получение данных в формате json
response = requests.get('https://services.swpc.noaa.gov/products/10cm-flux-30-day.json')
data = json.loads(response.text)

# Создание списка времени и списка значений
time_tags = [row[0] for row in data[1:]]
flux = [int(row[1]) for row in data[1:]]

# Создание графика
plt.plot(time_tags, flux)

# Настройка осей
plt.xlabel('Time')
plt.ylabel('Flux')
plt.title('Flux over time')

# Отображение графика
plt.show()
