# импортируем необходимые библиотеки
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
import json
import requests

# загружаем данные
url = "https://services.swpc.noaa.gov/json/ovation_aurora_latest.json"
response = requests.get(url)
data = json.loads(response.content)

# преобразуем данные в формат DataFrame
df = pd.DataFrame(data["coordinates"], columns=["longitude", "latitude", "aurora"])
df["datetime"] = pd.to_datetime(data["Forecast Time"])
df.set_index("datetime", inplace=True)
df = df.loc[:, ["latitude", "aurora"]]
df.columns = ["latitude", "kp"]
df.index.name = "datetime"
df = df.resample("H").mean()
df.fillna(method="ffill", inplace=True)

# выбираем данные для северного полушария
data_northern = df.loc[df["latitude"] >= 0]

# создаем признаки для прогнозирования
data_northern["hour"] = data_northern.index.hour
data_northern["day_of_week"] = data_northern.index.dayofweek

# обучаем модель
X = data_northern[["hour", "day_of_week"]]
y = data_northern["kp"]
model = LinearRegression()

if len(X) > 0:
    model.fit(X, y)
else:
    print("No data available for training the model")

# делаем прогноз на следующие 24 часа
last_datetime = data_northern.index[-1]
next_datetime = last_datetime + timedelta(hours=1)
forecast = pd.DataFrame(index=pd.date_range(next_datetime, periods=24, freq="H"))
forecast["hour"] = forecast.index.hour
forecast["day_of_week"] = forecast.index.dayofweek
forecast["kp"] = model.predict(forecast[["hour", "day_of_week"]])

# выводим график прогноза
if len(data_northern) > 0:
    # получаем максимальное и минимальное значения широты для построения овала
    lat_min, lat_max = data_northern["latitude"].min(), data_northern["latitude"].max()
    lat_mid = (lat_min + lat_max) / 2

    # рисуем овал на карте
    from mpl_toolkits.basemap import Basemap
    fig = plt.figure(figsize=(8, 8))
    m = Basemap(projection="ortho", lat_0=lat_mid, lon_0=-30, resolution="l")
    m.drawmapboundary(fill_color="black")
    m.drawparallels(np.arange(-90., 90., 10.), color="gray", labels=[1, 0, 0, 0], fontsize=10)
    m.drawmeridians(np.arange(-180., 180., 10.), color="gray", labels=[0, 0, 0, 1], fontsize=10)
    x, y = m(data_northern["longitude"].values, data_northern["latitude"].values)
    sc = m.scatter(x, y, c=data_northern["kp"], cmap=plt.cm.get_cmap("jet"), edgecolors="none")
cbar = plt.colorbar(sc)
cbar.ax.set_ylabel("KP Index")
plt.title("KP Index Forecast for Northern Hemisphere")
plt.show()

# выводим график прогноза
plt.plot(data_northern.index, data_northern["kp"], label="actual")
plt.plot(forecast.index, forecast["kp"], label="forecast")
plt.legend()
plt.title("KP Index Forecast for Northern Hemisphere")
plt.xlabel("Date")
plt.ylabel("KP Index")
plt.show()

