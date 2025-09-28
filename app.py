import gradio as gr
import requests
import pycountry

# Function to get latitude and longitude of a country using Open-Meteo Geocoding API
def get_coordinates(country_name):
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={country_name}&count=1"
    try:
        response = requests.get(url).json()
    except Exception:
        return None, None
    if "results" in response:
        result = response["results"][0]
        return result["latitude"], result["longitude"]
    return None, None

# Function to get weather forecast
def get_weather(country_name):
    lat, lon = get_coordinates(country_name)
    if lat is None or lon is None:
        return "❌ Could not find weather for this country."

    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&current=temperature_2m,"
        f"relative_humidity_2m,apparent_temperature,weather_code"
    )
    try:
        response = requests.get(url).json()
    except Exception:
        return "❌ Error fetching weather data."

    if "current" not in response:
        return "❌ Weather data not available."

    current = response["current"]
    temp = current.get("temperature_2m", "N/A")
    feels_like = current.get("apparent_temperature", "N/A")
    humidity = current.get("relative_humidity_2m", "N/A")
    code = current.get("weather_code", -1)

    weather_condition = {
        0: "Clear sky ☀️",
        1: "Mainly clear 🌤️",
        2: "Partly cloudy ⛅",
        3: "Overcast ☁️",
        45: "Fog 🌫️",
        48: "Rime fog ❄️",
        51: "Light drizzle 🌦️",
        61: "Rain 🌧️",
        71: "Snow ❄️",
        80: "Rain showers 🌧️",
        95: "Thunderstorm ⛈️",
    }.get(code, "Unknown 🌍")

    return (
        f"🌍 Country: {country_name}\n"
        f"🌡️ Temperature: {temp} °C\n"
        f"🥵 Feels Like: {feels_like} °C\n"
        f"💧 Humidity: {humidity}%\n"
        f"🌦️ Condition: {weather_condition}"
    )

# Dropdown list of all countries
country_list = sorted([country.name for country in pycountry.countries])

# Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("## 🌍 Global Weather Forecast App")
    country = gr.Dropdown(
        choices=country_list,
        label="Select Country",
        type="value",
        allow_custom_value=True,
    )
    output = gr.Textbox(label="Weather Info", lines=6)
    btn = gr.Button("Check Weather")

    btn.click(fn=get_weather, inputs=country, outputs=output)

# Run app
if __name__ == "__main__":
    demo.launch()
