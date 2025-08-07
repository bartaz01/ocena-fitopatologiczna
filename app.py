
import streamlit as st
import pandas as pd

# Inicjalizacja sesji
if "dane" not in st.session_state:
    st.session_state.dane = []
if "powtorzenie" not in st.session_state:
    st.session_state.powtorzenie = 1
if "kombinacja" not in st.session_state:
    st.session_state.kombinacja = 1
if "zebrane_dane" not in st.session_state:
    st.session_state.zebrane_dane = []

st.title("Ocena fitopatologiczna – tryb krokowy")

# Dane wejściowe
choroby_input = st.text_input("Skróty chorób (np. V, S, Z)", "V, S, Z")
liczba_ocen = st.number_input("Liczba powtórzeń oceny", min_value=1, value=3, step=1)
liczba_kombinacji = st.number_input("Liczba kombinacji", min_value=1, value=2, step=1)

choroby = [c.strip() for c in choroby_input.split(",")]
aktualna_kombinacja = st.session_state.kombinacja
aktualne_powtorzenie = st.session_state.powtorzenie

st.markdown(f"### Kombinacja {aktualna_kombinacja} – Powtórzenie {aktualne_powtorzenie}")

# Formularz
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
        st.rerun()
    else:
        st.session_state.powtorzenie = 1
        if aktualna_kombinacja < liczba_kombinacji:
            if st.button("Przejdź do następnej kombinacji"):
                st.session_state.kombinacja += 1
                st.experimental_rerun()
            if st.button("Wybierz kombinację ręcznie"):
                nowa = st.number_input("Wybierz nową kombinację:", min_value=1, step=1, key="nowa_komb")
                if st.button("Przejdź do wybranej"):
                    st.session_state.kombinacja = nowa
                    st.experimental_rerun()
        else:
            st.success("Zakończono wszystkie kombinacje")

# Eksport
if st.button("Eksportuj wszystko do Excela"):
    df = pd.DataFrame(st.session_state.zebrane_dane)
    df.to_excel("oceny_krokowe.xlsx", index=False)
    st.success("Zapisano jako 'oceny_krokowe.xlsx'")
