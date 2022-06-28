
import streamlit as st
import streamlit_authenticator as stauth
import yaml


from src.diverse.funksjoner import load_page, title_page
from src.apps.bergvarmekalkulatoren import bergvarmekalkulatoren_app
from src.apps.forside import forside_app

st.set_page_config(page_title="AV Grunnvarme", page_icon=":bar_chart:", layout="centered")

with open('src/innlogging/config.yaml') as file:
    config = yaml.load(file, Loader=stauth.SafeLoader)
authenticator = stauth.Authenticate(config['credentials'],config['cookie']['name'],config['cookie']['key'],config['cookie']['expiry_days'])
name, authentication_status, username = authenticator.login('Asplan Viak🌱 Innlogging for grunnvarme', 'main')

if authentication_status == False:
    st.error('Ugyldig brukernavn/passord')
    
elif authentication_status == None:
    load_page()

#App start 
elif authentication_status:
    with st.sidebar:
        authenticator.logout('Logg ut', 'sidebar')
        st.title(f'Hei {name}!')

        options = ["Forside", "Bergvarmekalkulatoren", "PROFet", "Maler", "TRT"]
        selected = st.radio("Velg app", options)

    if selected == "Forside":
        forside_app()

    if selected == "Bergvarmekalkulatoren":
        bergvarmekalkulatoren_app()
        











