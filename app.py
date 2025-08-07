import streamlit as st
import pandas as pd

st.set_page_config(page_title="Ocena roślin", page_icon="ikona.jpg")

st.markdown(
    """
    <style>
    .stApp {
        background-color: #f0f0f0;
        color: white;
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
choroby_input = st.text_input("Skróty chorób (np. Verticillium)", "Verticillium")
liczba_ocen = st.number_input("Liczba powtórzeń oceny", min_value=1, value=3, step=1)
liczba_kombinacji = st.number_input("Liczba kombinacji", min_value=1, value=2, step=1)

choroby = [c.strip() for c in choroby_input.split(",")]
aktualna_kombinacja = st.session_state.kombinacja
aktualne_powtorzenie = st.session_state.powtorzenie

st.markdown(f"<h3 style='color: darkred;'>Kombinacja {aktualna_kombinacja} – Powtórzenie {aktualne_powtorzenie}</h3>", unsafe_allow_html=True)

# --- Pobranie istniejącego rekordu do edycji jeśli jest ---
# Znajdź w zebranych danych rekord pasujący do aktualnej kombinacji i powtórzenia
istniejacy_rekord = None
for rekord in st.session_state.zebrane_dane:
    if rekord.get("Kombinacja") == aktualna_kombinacja and rekord.get("Powtórzenie") == aktualne_powtorzenie:
        istniejacy_rekord = rekord
        break

# Jeśli rekord jest, wczytujemy wartości do formularza, jeśli nie - start z 0
wartosci_start = {}
for choroba in choroby:
    wartosci_start[choroba] = istniejacy_rekord.get(choroba, 0) if istniejacy_rekord else 0

with st.form(key="ocena_form"):
    wartosci = {}
    for choroba in choroby:
        # min=0, max usunięty, krok 1
        wartosci[choroba] = st.number_input(
            f"{choroba}",
            min_value=0,
            value=wartosci_start[choroba],
            step=1,
            key=f"{choroba}_{aktualna_kombinacja}_{aktualne_powtorzenie}"
        )
    submitted = st.form_submit_button("Zapisz oceny")

if submitted:
    rekord = {"Kombinacja": aktualna_kombinacja, "Powtórzenie": aktualne_powtorzenie}
    rekord.update(wartosci)
    
    # Jeśli rekord istnieje, nadpisz w liście
    if istniejacy_rekord:
        index = st.session_state.zebrane_dane.index(istniejacy_rekord)
        st.session_state.zebrane_dane[index] = rekord
    else:
        st.session_state.zebrane_dane.append(rekord)

    # Po zapisie nie przeładowujemy automatycznie, żeby użytkownik mógł dalej edytować

# --- Wyświetlenie wprowadzonych danych dla aktualnej kombinacji i powtórzenia ---
st.markdown("### Aktualne zapisane wyniki dla tej kombinacji i powtórzenia")
if istniejacy_rekord:
    # Usuń klucze systemowe z wyświetlenia
    pokaz = {k: v for k, v in istniejacy_rekord.items() if k not in ["Kombinacja", "Powtórzenie"]}
    df_wyniki = pd.DataFrame(pokaz.items(), columns=["Choroba", "Wartość"])
    st.table(df_wyniki)
else:
    st.info("Brak zapisanych wyników dla tej kombinacji i powtórzenia.")

st.write("---")

# Obsługa przejścia dalej i nawigacji w kombinacjach i powtórzeniach (przerobiłem trochę)

if aktualne_powtorzenie < liczba_ocen:
    if st.button("Przejdź do następnego powtórzenia"):
        st.session_state.powtorzenie += 1
        st.experimental_rerun()
else:
    st.session_state.powtorzenie = 1
    if aktualna_kombinacja < liczba_kombinacji:
        if st.button("Przejdź do następnej kombinacji"):
            st.session_state.kombinacja += 1
            st.experimental_rerun()
        nowa = st.number_input("Wybierz nową kombinację:", min_value=1, max_value=liczba_kombinacji, step=1, key="nowa_komb")
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
