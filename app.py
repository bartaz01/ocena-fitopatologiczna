import streamlit as st
import pandas as pd

st.set_page_config(page_title="Ocena Fitopatologiczna", page_icon="ikona.jpg")

st.markdown(
    """
    <h1 style='text-align: center; color: green;'>Ocena fitopatologiczna – tryb krokowy</h1>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
    div.stButton > button:first-child {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 10px 24px;
        margin-top: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

if "dane" not in st.session_state:
    st.session_state.dane = []
if "powtorzenie" not in st.session_state:
    st.session_state.powtorzenie = 1
if "kombinacja" not in st.session_state:
    st.session_state.kombinacja = 1
if "zebrane_dane" not in st.session_state:
    st.session_state.zebrane_dane = []

st.markdown("<h3 style='color: darkblue;'>Dane wejściowe</h3>", unsafe_allow_html=True)
choroby_input = st.text_input("Skróty chorób (np. V, S, Z)", "V, S, Z")
liczba_ocen = st.number_input("Liczba powtórzeń oceny", min_value=1, value=3, step=1)
liczba_kombinacji = st.number_input("Liczba kombinacji", min_value=1, value=2, step=1)

choroby = [c.strip() for c in choroby_input.split(",")]
aktualna_kombinacja = st.session_state.kombinacja
aktualne_powtorzenie = st.session_state.powtorzenie

st.markdown(f"<h3 style='color: darkred;'>Kombinacja {aktualna_kombinacja} – Powtórzenie {aktualne_powtorzenie}</h3>", unsafe_allow_html=True)

with st.form(key="ocena_form"):
    wartosci = {}
    for choroba in choroby:
        wartosci[choroba] = st.number_input(f"{choroba}", min_value=0, max_value=100, step=1, key=f"{choroba}_{aktualna_kombinacja}_{aktualne_powtorzenie}")
    submitted = st.form_submit_button("Zapisz oceny")

if submitted:
    rekord = {"Kombinacja": aktualna_kombinacja, "Powtórzenie": aktualne_powtorzenie}
    rekord.update(wartosci)
    st.session_state.zebrane_dane.append(rekord)

    if aktualne_powtorzenie < liczba_ocen:
        st.session_state.powtorzenie += 1
        st.experimental_rerun()
    else:
        st.session_state.powtorzenie = 1
        if aktualna_kombinacja < liczba_kombinacji:
            if st.button("Przejdź do następnej kombinacji"):
                st.session_state.kombinacja += 1
                st.experimental_rerun()
            nowa = st.number_input("Wybierz nową kombinację:", min_value=1, step=1, key="nowa_komb")
            if st.button("Przejdź do wybranej"):
                st.session_state.kombinacja = nowa
                st.experimental_rerun()
        else:
            st.success("Zakończono wszystkie kombinacje")

st.write("---")

if st.button("Eksportuj wszystko do Excela"):
    df = pd.DataFrame(st.session_state.zebrane_dane)
    df.to_excel("oceny_krokowe.xlsx", index=False)
    st.success("Zapisano jako 'oceny_krokowe.xlsx'")
