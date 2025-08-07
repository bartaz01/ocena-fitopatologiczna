import streamlit as st
import pandas as pd

st.set_page_config(page_title="Ocena Fitopatologiczna", page_icon="ikona.jpg")

st.markdown(
    """
    <style>
    .stApp {
        background-color: #f0f0f0;
        color: #333333;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <h1 style='text-align: center; color: #2c3e50;'>Ocena fitopatologiczna – tryb krokowy</h1>
    """,
    unsafe_allow_html=True
)

# Inicjalizacja sesji
for key in ["powtorzenie", "kombinacja", "zebrane_dane"]:
    if key not in st.session_state:
        st.session_state[key] = 1 if key != "zebrane_dane" else []

# Wprowadź listy chorób / cech dla 3 typów ocen:
fitopatologiczne_input = st.text_input("Choroby fitopatologiczne (np. V, S, Z)", "V, S, Z")
herbologiczne_input = st.text_input("Oceny herbologiczne (np. H1, H2)", "H1, H2")
insektycydowe_input = st.text_input("Oceny insektycydowe (np. I1, I2)", "I1, I2")

liczba_ocen = st.number_input("Liczba powtórzeń oceny", min_value=1, value=3, step=1)
liczba_kombinacji = st.number_input("Liczba kombinacji", min_value=1, value=2, step=1)

# Lista wszystkich cech do oceny
fitopatologiczne = [c.strip() for c in fitopatologiczne_input.split(",") if c.strip()]
herbologiczne = [c.strip() for c in herbologiczne_input.split(",") if c.strip()]
insektycydowe = [c.strip() for c in insektycydowe_input.split(",") if c.strip()]

wszystkie_cechy = fitopatologiczne + herbologiczne + insektycydowe

aktualna_kombinacja = st.session_state.kombinacja
aktualne_powtorzenie = st.session_state.powtorzenie

st.markdown(
    f"<h3 style='color: #7f8c8d;'>Kombinacja {aktualna_kombinacja} – Powtórzenie {aktualne_powtorzenie}</h3>",
    unsafe_allow_html=True,
)

# Znajdź istniejący rekord dla aktualnej kombinacji i powtórzenia
istniejacy_rekord = None
for rekord in st.session_state.zebrane_dane:
    if rekord.get("Kombinacja") == aktualna_kombinacja and rekord.get("Powtórzenie") == aktualne_powtorzenie:
        istniejacy_rekord = rekord
        break

wartosci_start = {}
for cecha in wszystkie_cechy:
    wartosci_start[cecha] = istniejacy_rekord.get(cecha, 0) if istniejacy_rekord else 0

with st.form(key="ocena_form"):
    st.markdown("#### Oceny fitopatologiczne")
    wartosci = {}
    for cecha in fitopatologiczne:
        wartosci[cecha] = st.number_input(
            f"{cecha}", min_value=0, value=wartosci_start[cecha], step=1, key=f"{cecha}_{aktualna_kombinacja}_{aktualne_powtorzenie}"
        )
    st.markdown("#### Oceny herbologiczne")
    for cecha in herbologiczne:
        wartosci[cecha] = st.number_input(
            f"{cecha}", min_value=0, value=wartosci_start[cecha], step=1, key=f"{cecha}_{aktualna_kombinacja}_{aktualne_powtorzenie}"
        )
    st.markdown("#### Oceny insektycydowe")
    for cecha in insektycydowe:
        wartosci[cecha] = st.number_input(
            f"{cecha}", min_value=0, value=wartosci_start[cecha], step=1, key=f"{cecha}_{aktualna_kombinacja}_{aktualne_powtorzenie}"
        )

    submitted = st.form_submit_button("Zapisz oceny")

if submitted:
    rekord = {"Kombinacja": aktualna_kombinacja, "Powtórzenie": aktualne_powtorzenie}
    rekord.update(wartosci)

    if istniejacy_rekord:
        index = st.session_state.zebrane_dane.index(istniejacy_rekord)
        st.session_state.zebrane_dane[index] = rekord
    else:
        st.session_state.zebrane_dane.append(rekord)

# Wyświetlanie zapisanych wyników dla aktualnej kombinacji i powtórzenia
st.markdown("### Aktualne zapisane wyniki dla tej kombinacji i powtórzenia")
if istniejacy_rekord:
    pokaz = {k: v for k, v in istniejacy_rekord.items() if k not in ["Kombinacja", "Powtórzenie"]}
    df_wyniki = pd.DataFrame(pokaz.items(), columns=["Cecha", "Wartość"])
    st.table(df_wyniki)
else:
    st.info("Brak zapisanych wyników dla tej kombinacji i powtórzenia.")

st.write("---")

# Obliczanie średnich dla każdej cechy na podstawie wszystkich zebranych danych
if st.session_state.zebrane_dane:
    df_all = pd.DataFrame(st.session_state.zebrane_dane)
    # Ustawiamy typy liczbowe (może być problem z pustymi, więc fillna)
    df_all.fillna(0, inplace=True)
    for cecha in wszystkie_cechy:
        df_all[cecha] = pd.to_numeric(df_all[cecha], errors='coerce').fillna(0)

    srednie = df_all[wszystkie_cechy].mean().round(2)
    srednie_df = srednie.reset_index()
    srednie_df.columns = ["Cecha", "Średnia wartość"]

    st.markdown("### Średnie wartości podsumowane dla wszystkich kombinacji i powtórzeń")
    st.table(srednie_df)
else:
    st.info("Brak danych do wyliczenia średnich.")

st.write("---")

# Nawigacja pomiędzy powtórzeniami i kombinacjami
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
        nowa = st.number_input(
            "Wybierz nową kombinację:", min_value=1, max_value=liczba_kombinacji, step=1, key="nowa_komb"
        )
        if st.button("Przejdź do wybranej"):
            st.session_state.kombinacja = nowa
            st.experimental_rerun()
    else:
        st.success("Zakończono wszystkie kombinacje")

st.write("---")

# Eksport danych do Excela
if st.button("Eksportuj wszystko do Excela"):
    df_export = pd.DataFrame(st.session_state.zebrane_dane)
    df_export.to_excel("oceny_krokowe.xlsx", index=False)
    st.success("Zapisano jako 'oceny_krokowe.xlsx'")
