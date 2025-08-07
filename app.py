import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Dziennik ocen", page_icon="ikona.jpg")

st.markdown(
    """
    <style>
    .stApp {
        background-color: #f0f0f0;
        color: #333333;
    }
    .stButton > button {
        width: 100%;
        padding: 10px;
        margin: 5px 0;
        font-size: 14px;
        border-radius: 5px;
    }
    .stButton > button[kind="secondary"] {
        background-color: #3498db;
        color: white;
        border: none;
    }
    .stButton > button[kind="secondary"]:hover {
        background-color: #2980b9;
    }
    .stButton > button[kind="primary"] {
        background-color: #2ecc71;
        color: white;
        border: none;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #27ae60;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <h1 style='text-align: center; color: #2c3e50;'>Dziennik ocen</h1>
    """,
    unsafe_allow_html=True,
)

# Inicjalizacja sesji
for key in ["powtorzenie", "kombinacja", "zebrane_dane", "fitopatologiczne_aktywne", "herbologiczne_aktywne", "insektycydowe_aktywne"]:
    if key not in st.session_state:
        st.session_state[key] = 1 if key in ["powtorzenie", "kombinacja"] else [] if key == "zebrane_dane" else True

# Ustawienia liczby powtórzeń i kombinacji
liczba_ocen = st.number_input("Liczba powtórzeń oceny (może być 0)", min_value=0, value=3, step=1)
liczba_kombinacji = st.number_input("Liczba kombinacji (może być 0)", min_value=0, value=2, step=1)

# Opcje Tak/Nie dla kategorii
st.markdown("### Wybierz kategorie do oceny")
st.session_state.fitopatologiczne_aktywne = st.checkbox("Oceny fitopatologiczne", value=st.session_state.fitopatologiczne_aktywne)
st.session_state.herbologiczne_aktywne = st.checkbox("Oceny herbologiczne", value=st.session_state.herbologiczne_aktywne)
st.session_state.insektycydowe_aktywne = st.checkbox("Oceny insektycydowe", value=st.session_state.insektycydowe_aktywne)

# Pola tekstowe tylko dla aktywnych kategorii
fitopatologiczne = []
herbologiczne = []
insektycydowe = []

if st.session_state.fitopatologiczne_aktywne:
    fitopatologiczne_input = st.text_input("Oceny fitopatologiczne (np. F1, F2)", "F1, F2")
    fitopatologiczne = [c.strip() for c in fitopatologiczne_input.split(",") if c.strip()]
else:
    fitopatologiczne = []

if st.session_state.herbologiczne_aktywne:
    herbologiczne_input = st.text_input("Oceny herbologiczne (np. H1, H2)", "H1, H2")
    herbologiczne = [c.strip() for c in herbologiczne_input.split(",") if c.strip()]
else:
    herbologiczne = []

if st.session_state.insektycydowe_aktywne:
    insektycydowe_input = st.text_input("Oceny insektycydowe (np. I1, I2)", "I1, I2")
    insektycydowe = [c.strip() for c in insektycydowe_input.split(",") if c.strip()]
else:
    insektycydowe = []

wszystkie_cechy = fitopatologiczne + herbologiczne + insektycydowe

# Obsługa sesji i wartości domyślnych
if liczba_kombinacji == 0:
    st.session_state.kombinacja = 1
else:
    st.session_state.kombinacja = min(max(st.session_state.kombinacja, 1), liczba_kombinacji)

if liczba_ocen == 0:
    st.session_state.powtorzenie = 1
else:
    st.session_state.powtorzenie = min(max(st.session_state.powtorzenie, 1), liczba_ocen)

aktualna_kombinacja = st.session_state.kombinacja
aktualne_powtorzenie = st.session_state.powtorzenie

# --- MAPKA NAD FORMULARZEM ---
if liczba_kombinacji > 0 and liczba_ocen > 0:
    st.markdown("### Mapa powtórzeń i kombinacji — kliknij, aby przejść do wybranej oceny")
    cols = st.columns(liczba_ocen, gap="small")
    for k in range(1, liczba_kombinacji + 1):
        for p in range(1, liczba_ocen + 1):
            with cols[p-1]:
                selected = (k == aktualna_kombinacja and p == aktualne_powtorzenie)
                button_key = f"mapka_k{k}_p{p}"
                st.button(
                    f"K{k}-P{p}",
                    key=button_key,
                    help=f"Przejdź do Kombinacji {k} - Powtórzenia {p}",
                    on_click=lambda k=k, p=p: (setattr(st.session_state, "kombinacja", k), setattr(st.session_state, "powtorzenie", p)),
                    args=(),
                    kwargs={},
                    disabled=False,
                    use_container_width=True,
                    type="secondary" if not selected else "primary",
                )
else:
    st.info("Mapa nie jest dostępna, gdy liczba kombinacji lub powtórzeń jest 0.")

st.markdown(
    f"<h3 style='color: #2ecc71; text-align: center;'>Wyniki dla Kombinacji {aktualna_kombinacja} – Powtórzenia {aktualne_powtorzenie}</h3>",
    unsafe_allow_html=True,
)

# --- Formularz ---
istniejacy_rekord = None
for rekord in st.session_state.zebrane_dane:
    if rekord.get("Kombinacja") == aktualna_kombinacja and rekord.get("Powtórzenie") == aktualne_powtorzenie:
        istniejacy_rekord = rekord
        break

wartosci_start = {cecha: 0 for cecha in wszystkie_cechy}  # Wszystkie wartości początkowe na 0

with st.form(key="ocena_form"):
    wartosci = {}
    if st.session_state.fitopatologiczne_aktywne:
        st.markdown("#### Oceny fitopatologiczne")
        for cecha in fitopatologiczne:
            wartosci[cecha] = st.number_input(
                f"{cecha}", min_value=0, value=wartosci_start[cecha], step=1, key=f"{cecha}_{aktualna_kombinacja}_{aktualne_powtorzenie}"
            )
    if st.session_state.herbologiczne_aktywne:
        st.markdown("#### Oceny herbologiczne")
        for cecha in herbologiczne:
            wartosci[cecha] = st.number_input(
                f"{cecha}", min_value=0, value=wartosci_start[cecha], step=1, key=f"{cecha}_{aktualna_kombinacja}_{aktualne_powtorzenie}"
            )
    if st.session_state.insektycydowe_aktywne:
        st.markdown("#### Oceny insektycydowe")
        for cecha in insektycydowe:
            wartosci[cecha] = st.number_input(
                f"{cecha}", min_value=0, value=wartosci_start[cecha], step=1, key=f"{cecha}_{aktualna_kombinacja}_{aktualne_powtorzenie}"
            )

    st.markdown(
        """
        <style>
        .stButton > button {
            width: 100%;
            padding: 10px;
            margin: 5px 0;
            font-size: 14px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    col1, col2, col3, col4, col5 = st.columns([1.5, 1.5, 2, 1.5, 1.5])
    with col1:
        poprzednie_komb_disabled = aktualna_kombinacja <= 1
        poprzednie_komb = st.form_submit_button("Poprz. kombinacja", disabled=poprzednie_komb_disabled)
    with col2:
        poprzednie_disabled = aktualne_powtorzenie <= 1
        poprzednie = st.form_submit_button("Poprz. powtórzenie", disabled=poprzednie_disabled)
    with col3:
        zapisz = st.form_submit_button("Zapisz oceny")
    with col4:
        nastepne_disabled = aktualne_powtorzenie >= liczba_ocen or liczba_ocen == 0
        nastepne = st.form_submit_button("Nast. powtórzenie", disabled=nastepne_disabled)
    with col5:
        nastepne_komb_disabled = aktualna_kombinacja >= liczba_kombinacji or liczba_kombinacji == 0
        nastepne_komb = st.form_submit_button("Nast. kombinacja", disabled=nastepne_komb_disabled)

if zapisz or poprzednie or nastepne or poprzednie_komb or nastepne_komb:
    rekord = {"Kombinacja": aktualna_kombinacja, "Powtórzenie": aktualne_powtorzenie}
    rekord.update(wartosci)

    if istniejacy_rekord:
        index = st.session_state.zebrane_dane.index(istniejacy_rekord)
        st.session_state.zebrane_dane[index] = rekord
    else:
        st.session_state.zebrane_dane.append(rekord)

    if poprzednie_komb and aktualna_kombinacja > 1:
        st.session_state.kombinacja -= 1
        st.session_state.powtorzenie = 1
        st.rerun()
    elif nastepne_komb and aktualna_kombinacja < liczba_kombinacji:
        st.session_state.kombinacja += 1
        st.session_state.powtorzenie = 1
        st.rerun()
    elif poprzednie and aktualne_powtorzenie > 1:
        st.session_state.powtorzenie -= 1
        st.rerun()
    elif nastepne and aktualne_powtorzenie < liczba_ocen:
        st.session_state.powtorzenie += 1
        st.rerun()
    else:
        st.rerun()

# --- Wyświetlanie wyników dla wszystkich powtórzeń w bieżącej kombinacji ---
st.markdown(f"### Wyniki dla Kombinacji {aktualna_kombinacja}")
if liczba_ocen > 0 and wszystkie_cechy:
    dane_tabela = []
    for p in range(1, liczba_ocen + 1):
        rekord = None
        for r in st.session_state.zebrane_dane:
            if r.get("Kombinacja") == aktualna_kombinacja and r.get("Powtórzenie") == p:
                rekord = r
                break
        wiersz = {"Kombinacja-Powtórzenie": f"K{aktualna_kombinacja}-P{p}"}
        for cecha in wszystkie_cechy:
            wiersz[cecha] = rekord.get(cecha, 0) if rekord else 0
        dane_tabela.append(wiersz)
    df_wyniki = pd.DataFrame(dane_tabela)
    st.table(df_wyniki)
else:
    st.info("Brak zapisanych wyników lub aktywnych cech dla tej kombinacji.")

st.divider()

# --- Średnie z całego zbioru ---
if st.session_state.zebrane_dane and wszystkie_cechy:
    df_all = pd.DataFrame(st.session_state.zebrane_dane)
    df_all.fillna(0, inplace=True)
    for cecha in wszystkie_cechy:
        if cecha in df_all.columns:
            df_all[cecha] = pd.to_numeric(df_all[cecha], errors="coerce").fillna(0)
    srednie = df_all[wszystkie_cechy].mean().round(2)
    srednie_df = srednie.reset_index()
    srednie_df.columns = ["Cecha", "Średnia wartość"]
    st.markdown("### Średnie wartości podsumowane dla wszystkich kombinacji i powtórzeń")
    st.table(srednie_df)
else:
    st.info("Brak danych lub aktywnych cech do wyliczenia średnich.")

st.divider()

# Eksport danych
if st.button("Eksportuj wszystko do Excela"):
    df_export = pd.DataFrame(st.session_state.zebrane_dane)
    buffer = io.BytesIO()
    df_export.to_excel(buffer, index=False)
    st.download_button(
        label="Pobierz plik Excel",
        data=buffer,
        file_name="oceny_krokowe.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    st.success("Plik gotowy do pobrania!")
