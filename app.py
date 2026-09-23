from __future__ import annotations
import base64
from datetime import datetime; from zoneinfo import ZoneInfo
import plotly.graph_objects as go
import requests
import streamlit as st

CITY = "Hamar"
COORDINATES = (60.7945, 11.0679)
WEATHER = {
    "clearsky": ("☀️", "Klart"), "fair": ("🌤️", "Lettskyet"),
    "partlycloudy": ("⛅", "Delvis skyet"), "cloudy": ("☁️", "Skyet"),
    "fog": ("🌫️", "Tåke"), "lightrain": ("🌦️", "Lett regn"),
    "rain": ("🌧️", "Regn"), "heavyrain": ("🌧️", "Kraftig regn"),
    "lightsleet": ("🌨️", "Lett sludd"), "sleet": ("🌨️", "Sludd"),
    "heavysleet": ("🌨️", "Kraftig sludd"), "lightsnow": ("🌨️", "Lett snø"),
    "snow": ("❄️", "Snø"), "heavysnow": ("❄️", "Kraftig snø"),
    "thunder": ("⛈️", "Torden"),
}

st.set_page_config(page_title="Værglimt", page_icon="🌦️", layout="wide")
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
.stApp{background:linear-gradient(160deg,#f4f8fa,#e9f1f4 55%,#f8f6f0);color:#183443}
h1,h2,h3{font-family:Manrope,sans-serif!important;color:#183443!important}
.block-container{max-width:1100px;padding-top:2.4rem;padding-bottom:3rem}
.hero{border-radius:26px;min-height:280px;padding:34px 40px;color:#183443;display:flex;flex-direction:column;justify-content:space-between;background:linear-gradient(90deg,rgba(255,255,255,.78),rgba(255,255,255,.15)),var(--scene);background-size:cover;background-position:center;box-shadow:0 18px 48px #1d526324}
.hero .eyebrow{font-size:12px;letter-spacing:.17em;text-transform:uppercase;font-weight:700}.hero h1{color:#183443!important;font-size:clamp(38px,6vw,64px)!important;margin:12px 0 3px}.hero p{color:#183443;font-size:17px;margin:0}
.hero .tag{display:inline-block;background:#ffffffbb;border:1px solid #333;border-radius:30px;padding:8px 14px;width:max-content}
div[data-testid="stMetric"]{background:#fff;border:1px solid #555;border-radius:18px;padding:16px 20px;box-shadow:0 8px 24px #284f6010}
div[data-testid="stMetricLabel"],div[data-testid="stMetricLabel"] p{color:#183443!important;opacity:1!important;font-weight:700!important}
div[data-testid="stMetricValue"],div[data-testid="stMetricValue"] div{color:#183443!important;opacity:1!important}
.stApp p,.stApp span,.stApp label{color:#31505b!important;opacity:1!important}div[data-testid="stPlotlyChart"] svg text{fill:#183443!important}
</style>""",unsafe_allow_html=True)

def scene_svg(condition: str) -> str:
    palettes={"sun":("#83b8c8","#f4ce91","#446c70"),"cloud":("#8199a5","#c5d0d0","#405966"),"rain":("#647d8e","#aebbc0","#374d60"),"snow":("#9ab9c7","#e5edf0","#657e8c"),"fog":("#a6b8bb","#d2d8d5","#75888a")}
    sky,sun,mountain=palettes[condition]
    effect=""
    if condition=="rain": effect='<path d="M250 120 220 190m130-70-30 70m130-70-30 70m650-80-30 70m130-70-30 70m130-70-30 70" stroke="#d8e8ed" stroke-width="8" stroke-linecap="round" opacity=".8"/>'
    elif condition=="snow": effect='<g fill="#fff"><circle cx="260" cy="160" r="8"/><circle cx="400" cy="105" r="6"/><circle cx="680" cy="180" r="8"/><circle cx="910" cy="120" r="7"/><circle cx="1290" cy="180" r="8"/></g>'
    elif condition in ("cloud","fog"): effect='<g fill="#eef3f1" opacity=".8"><ellipse cx="330" cy="175" rx="105" ry="31"/><ellipse cx="770" cy="130" rx="135" ry="36"/><ellipse cx="1260" cy="210" rx="115" ry="32"/></g>'
    sun_opacity=".88" if condition=="sun" else ".25"
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="650" viewBox="0 0 1500 650"><defs><linearGradient id="s" x2="0" y2="1"><stop stop-color="{sky}"/><stop offset="1" stop-color="#e8d9c2"/></linearGradient><linearGradient id="w" x2="0" y2="1"><stop stop-color="#6395a0"/><stop offset="1" stop-color="#193f55"/></linearGradient></defs><rect width="1500" height="650" fill="url(#s)"/><circle cx="1160" cy="150" r="72" fill="{sun}" opacity="{sun_opacity}"/>{effect}<path d="M0 405 200 170 330 330 520 105 760 385 970 145 1200 370 1370 190 1500 315V650H0Z" fill="{mountain}" opacity=".77"/><path d="m145 235 55-65 43 52 42-8 45 116-130-47Zm290 3 85-133 76 89 45-5 119 202-205-93Zm405 48 130-141 83 83 51-6 124 160-197-76Zm355-23 175-73 130 119v139l-189-93Z" fill="#dbe9e5" opacity=".86"/><path d="M0 405q180-24 360 0t360 0 390 0 390 0v245H0Z" fill="url(#w)"/><path d="M0 470q170-20 340 0t340 0 340 0 480 0M0 535q170-20 340 0t340 0 340 0 480 0" fill="none" stroke="#d4e4df" stroke-opacity=".32" stroke-width="4"/><path d="M1040 406h210l-27-42h-155z" fill="#f1e6cc"/><path d="M1110 364v-66l65 66z" fill="#f8f1df"/><path d="M1098 406v46m125-46v46" stroke="#563e32" stroke-width="8"/><text x="60" y="595" fill="#183443" font-family="sans-serif" font-size="22" letter-spacing="7">HAMAR · VÆR NÅ</text></svg>'''
    return "data:image/svg+xml;base64,"+base64.b64encode(svg.encode()).decode()

@st.cache_data(ttl=900,show_spinner=False)
def get_forecast()->dict:
    lat,lon=COORDINATES
    response=requests.get("https://api.met.no/weatherapi/locationforecast/2.0/complete",params={"lat":lat,"lon":lon},headers={"User-Agent":"VaerglimtSkoleprosjekt/1.0"},timeout=15)
    response.raise_for_status()
    return response.json()

st.title("Værglimt")
st.caption(f"Et lite skoleprosjekt om været i Hamar · Dato: {datetime.now(ZoneInfo('Europe/Oslo')).strftime('%d.%m.%Y')}")
try:
    with st.spinner("Henter værmelding for Hamar …"): payload=get_forecast()
except requests.RequestException as exc:
    st.error("Klarte ikke å hente værdata akkurat nå. Sjekk internettforbindelsen og prøv igjen.")
    st.caption(f"Teknisk informasjon: {exc}")
    st.stop()

times=[]; temperatures=[]; winds=[]; symbols=[]; uv_indexes=[]; precipitations=[]
for item in payload["properties"]["timeseries"][:24]:
    data=item["data"]; details=data["instant"]["details"]
    symbol=data.get("next_1_hours",{}).get("summary",{}).get("symbol_code","")
    temperature=details.get("air_temperature")
    if temperature is None: continue
    times.append(datetime.fromisoformat(item["time"].replace("Z","+00:00")))
    temperatures.append(temperature); winds.append(details.get("wind_speed")); symbols.append(symbol)
    uv_indexes.append(details.get("ultraviolet_index_clear_sky"))
    precipitations.append(data.get("next_1_hours",{}).get("details",{}).get("precipitation_amount"))

current_temperature=temperatures[0]; current_wind=winds[0]; symbol_code=symbols[0].lower()
symbol_key=symbol_code.split("_",1)[0].replace("and","")
icon,description=WEATHER.get(symbol_key,("🌡️","Værmelding"))
if "thunder" in symbol_code: condition="rain"; icon,description="⛈️","Tordenbyger"
elif "fog" in symbol_code: condition="fog"
elif "snow" in symbol_code or "sleet" in symbol_code: condition="snow"
elif "rain" in symbol_code or "shower" in symbol_code: condition="rain"
elif "cloud" in symbol_code or "fair" in symbol_code: condition="cloud"
else: condition="sun"
background=scene_svg(condition)
st.markdown(f'''<div class="hero" style="--scene:url('{background}')"><div><div class="eyebrow">Værmelding akkurat nå</div><h1>Hamar</h1><p>{icon} &nbsp;{description} &nbsp;·&nbsp; {current_temperature:.1f} °C</p></div><div class="tag">Norge&nbsp; · &nbsp; Yr</div></div>''',unsafe_allow_html=True)
st.write("")
col1,col2,col3=st.columns(3)
col1.metric("UV-indeks · klarvær",f"{uv_indexes[0]:.1f}" if uv_indexes[0] is not None else "Ikke tilgjengelig")
col2.metric("Vind",f"{current_wind:.1f} m/s" if current_wind is not None else "—")
col3.metric("Nedbør neste time",f"{precipitations[0]:.1f} mm" if precipitations[0] is not None else "Ingen prognose")
st.subheader("Temperaturen de neste timene")
fig=go.Figure(go.Scatter(x=times,y=temperatures,mode="lines+markers",line={"color":"#f3a45f","width":4,"shape":"spline"},marker={"size":8,"color":"#fff8e9","line":{"color":"#df8d4c","width":3}},fill="tozeroy",fillcolor="rgba(243,164,95,.15)",hovertemplate="%{x|%H:%M}<br><b>%{y:.1f} °C</b><extra></extra>"))
fig.update_layout(height=360,margin={"l":12,"r":12,"t":20,"b":8},paper_bgcolor="rgba(255,255,255,.68)",plot_bgcolor="rgba(255,255,255,.25)",font={"family":"DM Sans, sans-serif","color":"#183443"},xaxis={"title":None,"showgrid":False,"tickformat":"%H:%M","linecolor":"#c7d8dc"},yaxis={"title":"Temperatur (°C)","gridcolor":"#dce7e8","zerolinecolor":"#b7c9cc"},hovermode="x unified", hoverlabel={"bgcolor":"#183443","bordercolor":"#183443","font":{"color":"#ffffff"}})
st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
st.markdown('<p>Værdata fra <a href="https://www.yr.no/">Yr</a>, levert via <a href="https://developer.yr.no/">Yr sitt vær-API</a> (Locationforecast).</p>',unsafe_allow_html=True)
