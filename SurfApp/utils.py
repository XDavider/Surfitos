def decode_weather_code(code):
    if code == 0:
        return "☀️ Cielo despejado"
    elif code in [1, 2, 3]:
        return "🌤️ Parcialmente nublado"
    elif code in [45, 48]:
        return "🌫️ Niebla"
    elif code in [51, 53, 55]:
        return "🌦️ Llovizna"
    elif code in [56, 57]:
        return "🌧️ Llovizna helada"
    elif code in [61, 63, 65]:
        return "🌧️ Lluvia"
    elif code in [66, 67]:
        return "🌧️ Lluvia helada"
    elif code in [71, 73, 75]:
        return "❄️ Nieve"
    elif code == 77:
        return "❄️ Copos de nieve"
    elif code in [80, 81, 82]:
        return "🌧️ Chubascos"
    elif code in [85, 86]:
        return "🌨️ Chubascos de nieve"
    elif code == 95:
        return "⛈️ Tormenta"
    elif code in [96, 99]:
        return "🌩️ Tormenta con granizo"
    else:
        return f"🔍 Código: {code}"
