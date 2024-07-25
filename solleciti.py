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
def genera_testo_mail(destinatario, nome, fatture, sollecito, testi_mail):
    key = f"{destinatario}_{sollecito}"
    testo = testi_mail[key]
    testo = testo.replace("[Destinatario]", nome)
    fatture_testo = "\n\n".join(
        [
            f"Fattura N.{fattura['n_fattura']} emessa il {fattura['data_emissione'].strftime('%d/%m/%Y')} per un importo di {fattura['importo']} scaduta il {fattura['data_scadenza'].strftime('%d/%m/%Y')}"
            for fattura in fatture
        ]
    )
    testo = testo.replace("[Fatture]", fatture_testo)
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

# Stato della sessione per le fatture
if "fatture" not in st.session_state:
    st.session_state.fatture = [{
        "n_fattura": "",
        "data_emissione": datetime.today(),
        "importo": "",
        "giorni_scadenza": 30,
        "data_scadenza": calcola_data_scadenza(datetime.today(), 30)
    }]

# Funzione per aggiungere una nuova fattura
def aggiungi_fattura():
    st.session_state.fatture.append({
        "n_fattura": "",
        "data_emissione": datetime.today(),
        "importo": "",
        "giorni_scadenza": 30,
        "data_scadenza": calcola_data_scadenza(datetime.today(), 30)
    })
    st.experimental_rerun()

# Funzione per rimuovere una fattura
def rimuovi_fattura(idx):
    if 0 <= idx < len(st.session_state.fatture):
        st.session_state.fatture.pop(idx)
        st.experimental_rerun()

# Interfaccia Streamlit
st.title("Generatore di Solleciti di Pagamento")

# Radiobutton per selezionare il destinatario
destinatario = st.radio("Destinatario", ["Persona", "Azienda"])

# Casella di testo per inserire il nome del destinatario
nome = st.text_input("Azienda/Persona")

# Sezione per aggiungere e visualizzare le fatture
st.header("Fatture")
for idx, fattura in enumerate(st.session_state.fatture):
    st.subheader(f"Fattura {idx + 1}")
    fattura["n_fattura"] = st.text_input(f"N.Fattura {idx + 1}", fattura["n_fattura"], key=f"n_fattura_{idx}")
    fattura["data_emissione"] = st.date_input(f"Data Emissione {idx + 1}", fattura["data_emissione"], key=f"data_emissione_{idx}")
    fattura["importo"] = st.text_input(f"Importo {idx + 1}", fattura["importo"], key=f"importo_{idx}")
    fattura["giorni_scadenza"] = st.selectbox(f"Scadenza {idx + 1}", [30, 60, 90], index=[30, 60, 90].index(fattura["giorni_scadenza"]), key=f"giorni_scadenza_{idx}")
    fattura["data_scadenza"] = calcola_data_scadenza(fattura["data_emissione"], fattura["giorni_scadenza"])
    st.text_input(f"Data Scadenza {idx + 1}", fattura["data_scadenza"].strftime('%d/%m/%Y'), key=f"data_scadenza_{idx}", disabled=True)
    if st.button(f"Rimuovi Fattura {idx + 1}", key=f"rimuovi_fattura_{idx}"):
        rimuovi_fattura(idx)

# Pulsante per aggiungere una nuova fattura
if st.button("Aggiungi Fattura"):
    aggiungi_fattura()

# Menu a tendina per il tipo di sollecito
sollecito = st.selectbox("Sollecito", ["Normale", "Urgente"])

# Impostazioni dei testi delle mail
with st.expander("Impostazioni testi sollecito"):
    st.text_area("Destinatario della mail Persona, Tipo di sollecito Normale", st.session_state.get("Persona_Normale", ""), key="Persona_Normale", on_change=salva_testo_mail, args=("Persona_Normale",))
    st.text_area("Destinatario della mail Persona, Tipo di sollecito Urgente", st.session_state.get("Persona_Urgente", ""), key="Persona_Urgente", on_change=salva_testo_mail, args=("Persona_Urgente",))
    st.text_area("Destinatario della mail Azienda, Tipo di sollecito Normale", st.session_state.get("Azienda_Normale", ""), key="Azienda_Normale", on_change=salva_testo_mail, args=("Azienda_Normale",))
    st.text_area("Destinatario della mail Azienda, Tipo di sollecito Urgente", st.session_state.get("Azienda_Urgente", ""), key="Azienda_Urgente", on_change=salva_testo_mail, args=("Azienda_Urgente",))

# Genera il testo della mail
if st.button("Genera Testo Mail"):
    testo_mail = genera_testo_mail(destinatario, nome, st.session_state.fatture, sollecito, st.session_state.testi_mail)
    st.text_area("Testo della Mail", testo_mail, height=200)
