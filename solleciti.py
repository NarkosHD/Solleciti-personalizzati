import os
import streamlit as st
from datetime import datetime, timedelta
from pathlib import Path

# Directory delle impostazioni
settings_dir = Path("Settings")
settings_dir.mkdir(exist_ok=True)

# Funzione per calcolare la data di scadenza
def calcola_data_scadenza(data_emissione, giorni_scadenza):
    return data_emissione + timedelta(days=giorni_scadenza)

# Funzione per generare il testo della mail
def genera_testo_mail(destinatario, nome, n_fattura, data_emissione, importo, data_scadenza, sollecito, testi_mail):
    testo = testi_mail[f"{destinatario}_{sollecito}"]
    testo = testo.replace("[Destinatario]", nome)
    testo = testo.replace("[N.Fattura]", n_fattura)
    testo = testo.replace("[Data Emissione]", data_emissione.strftime('%d/%m/%Y'))
    testo = testo.replace("[Importo]", str(importo))
    testo = testo.replace("[Data Scadenza]", data_scadenza.strftime('%d/%m/%Y'))
    return testo

# Funzione per leggere i testi dalle impostazioni
def leggi_testi_mail():
    testi = {}
    for key in ["Persona_Normale", "Persona_Urgente", "Azienda_Normale", "Azienda_Urgente"]:
        file_path = settings_dir / f"{key}.txt"
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as file:
                testi[key] = file.read()
        else:
            testi[key] = ""
            with open(file_path, "w", encoding="utf-8") as file:
                file.write("")
    return testi

# Funzione per salvare i testi nelle impostazioni
def salva_testo_mail(key):
    testo = st.session_state[key]
    file_path = settings_dir / f"{key}.txt"
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(testo)

# Legge i testi delle mail dalle impostazioni
testi_mail = leggi_testi_mail()

# Stato della sessione per tenere traccia delle modifiche nelle text_area
if "testi_mail" not in st.session_state:
    st.session_state.testi_mail = testi_mail
    for key, testo in testi_mail.items():
        st.session_state[key] = testo

# Interfaccia Streamlit
st.title("Generatore di Solleciti di Pagamento")

# Radiobutton per selezionare il destinatario
destinatario = st.radio("Destinatario", ["Persona", "Azienda"])

# Caselle di testo per inserire i dettagli
nome = st.text_input("Azienda/Persona")
n_fattura = st.text_input("N.Fattura")
data_emissione = st.date_input("Data Emissione")
importo = st.text_input("Importo")
giorni_scadenza = st.selectbox("Scadenza", [30, 60, 90])

# Calcola la data di scadenza
data_scadenza = calcola_data_scadenza(data_emissione, giorni_scadenza)
st.text_input("Data Scadenza", data_scadenza.strftime('%d/%m/%Y'), disabled=True)

# Menu a tendina per il tipo di sollecito
sollecito = st.selectbox("Sollecito", ["Normale", "Urgente"])

# Impostazioni dei testi delle mail
with st.expander("Impostazioni testi sollecito"):
    st.text_area("Destinatario della mail Persona, Tipo di sollecito Normale", st.session_state["Persona_Normale"], key="Persona_Normale", on_change=salva_testo_mail, args=("Persona_Normale",))
    st.text_area("Destinatario della mail Persona, Tipo di sollecito Urgente", st.session_state["Persona_Urgente"], key="Persona_Urgente", on_change=salva_testo_mail, args=("Persona_Urgente",))
    st.text_area("Destinatario della mail Azienda, Tipo di sollecito Normale", st.session_state["Azienda_Normale"], key="Azienda_Normale", on_change=salva_testo_mail, args=("Azienda_Normale",))
    st.text_area("Destinatario della mail Azienda, Tipo di sollecito Urgente", st.session_state["Azienda_Urgente"], key="Azienda_Urgente", on_change=salva_testo_mail, args=("Azienda_Urgente",))

# Genera il testo della mail
if st.button("Genera Testo Mail"):
    testo_mail = genera_testo_mail(destinatario, nome, n_fattura, data_emissione, importo, data_scadenza, sollecito, st.session_state.testi_mail)
    st.text_area("Testo della Mail", testo_mail, height=200)
