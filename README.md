# Værglimt – værapp for Hamar

En liten Python-app laget med Streamlit. Appen viser vær og temperatur for Hamar, temperaturprognosen for de neste timene og en bakgrunn som skifter etter værtypen. Den viser også UV-indeks for klarvær, vind og forventet nedbør neste time.

## Kjør appen lokalt

1. Installer Python.
2. Installer pakkene:

   ```bash
   python -m pip install -r requirements.txt
   ```

3. Start appen:

   ```bash
   python -m streamlit run app.py
   ```

Appen trenger internett for å hente oppdatert værmelding.

## Datakilde

Værdata hentes fra Yr sitt Locationforecast-API.
