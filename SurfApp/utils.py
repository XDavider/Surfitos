def decode_weather_code(code):
    if code == 0:
        return "☀️ Cielo despejado"
    elif code == 1:
        return "🌤️ Mayormente despejado"
    elif code == 2:
        return "⛅ Parcialmente nublado"
    elif code == 3:
        return "☁️ Nublado"
    elif code == 45:
        return "🌫️ Niebla"
    elif code == 48:
        return "🌫️ Niebla con escarcha"
    elif code == 51:
        return "🌦️ Llovizna ligera"
    elif code == 53:
        return "🌧️ Llovizna moderada"
    elif code == 55:
        return "🌧️ Llovizna intensa"
    elif code == 56:
        return "🌧️❄️ Llovizna helada ligera"
    elif code == 57:
        return "🌧️❄️ Llovizna helada intensa"
    elif code == 61:
        return "🌦️ Lluvia ligera"
    elif code == 63:
        return "🌧️ Lluvia moderada"
    elif code == 65:
        return "🌧️ Lluvia intensa"
    elif code == 66:
        return "🌧️❄️ Lluvia helada ligera"
    elif code == 67:
        return "🌧️❄️ Lluvia helada intensa"
    elif code == 71:
        return "🌨️ Nieve ligera"
    elif code == 73:
        return "🌨️ Nieve moderada"
    elif code == 75:
        return "🌨️ Nieve intensa"
    elif code == 77:
        return "❄️ Granos de nieve"
    elif code == 80:
        return "🌦️ Chubascos ligeros"
    elif code == 81:
        return "🌧️ Chubascos moderados"
    elif code == 82:
        return "🌧️🌩️ Chubascos fuertes"
    elif code == 85:
        return "🌨️ Chubascos de nieve ligeros"
    elif code == 86:
        return "🌨️ Chubascos de nieve intensos"
    elif code == 95:
        return "⛈️ Tormenta eléctrica"
    elif code == 96:
        return "⛈️ Tormenta con granizo ligero"
    elif code == 99:
        return "⛈️ Tormenta con granizo fuerte"
    else:
        return f"🔍 Código desconocido: {code}"