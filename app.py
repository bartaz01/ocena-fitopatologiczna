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
    .grid-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
        gap: 8px;
        margin-top: 10px;
        margin-bottom: 20px;
    }
    .grid-item {
        background-color: #3498db;
        color: white;
        padding: 12px;
        text-align: center;
        border-radius: 5px;
        cursor: pointer;
        user-select: none;
        font-weight: bold;
        transition: background-color 0.3s ease;
    }
    .grid-item:hover {
        background-color: #2980b9;
    }
    .selected {
        background-color: #2ecc71 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <h1 style='text-align: center; color: #2c3e50;'>Ocena fitopatologiczna – tryb krokowy</h1>
    """,
    unsafe_allow_html=True,
)

# Inicjalizacja sesji
for key in ["powtorzenie", "kombinacja", "zebrane_dane"]:
    if key not in st.session_state:
        st.session_state[key] = 1 if key != "zebrane_dane" else []

# Ustawienia liczby powtórzeń i kombinacji — minimalna 0
liczba_ocen = st.number_input("Liczba powtórzeń oceny (może być 0)", min_value=0, value=3, step=1)
liczba_kombinacji = st.number_input("Liczba kombinacji (może być 0)", min_value=0, value=2, step=1)

# Listy cech
fitopatologiczne_input = st.text_input("Choroby fitopatologiczne (np. V, S, Z)", "V, S, Z")
herbologiczne_input = st.text_input("Oceny herbologiczne (np. H1, H2)", "H1, H2")
insektycydowe_input = st.text_input("Oceny insektycydowe (np. I1, I2)", "I1, I2")

fitopatologiczne = [c.strip() for c in fitopatologiczne_input.split(",") if c.strip()]
herbologiczne = [c.strip() for c in herbologiczne_input.split(",") if c.strip()]
insektycydowe = [c.strip() for c in insektycydowe_input.split(",") if c.strip()]
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

    grid_html = "<div class='grid-container'>"
    for k in range(1, liczba_kombinacji + 1):
        for p in range(1, liczba_ocen + 1):
            selected_class = "selected" if (k == aktualna_kombinacja and p == aktualne_powtorzenie) else ""
            grid_html += (
                f"<div class='grid-item {selected_class}' "
                f"onclick='window.dispatchEvent(new CustomEvent(\"selectCell\", {{detail: {{komb: {k}, powt: {p}}}}}))'>"
                f"K{k} - P{p}"
                "</div>"
            )
    grid_html += "</div>"

    st.markdown(grid_html, unsafe_allow_html=True)

    # JS do przeładowania z parametrami w URL (kliknięcie mapki)
    st.markdown(
        """
        <script>
        const gridItems = window.parent.document.querySelectorAll('.grid-item');
        gridItems.forEach(item => {
            item.addEventListener('click', (e) => {
                const komb = parseInt(e.target.textContent.match(/K(\\d+)/)[1]);
                const powt = parseInt(e.target.textContent.match(/P(\\d+)/)[1]);
                window.location.href = window.location.pathname + `?kombinacja=${komb}&powtorzenie=${powt}`;
            });
        });
        </script>
        """,
        unsafe_allow_html=True,
    )
else:
    st.info("Mapa nie jest dostępna, gdy liczba kombinacji lub powtórzeń jest 0.")

# --- Odczyt parametrów z URL ---
params = st.experimental_get_query_params()
if "kombinacja" in params:
    try:
        k = int(params["kombinacja"][0])
        if 1 <= k <= max(liczba_kombinacji, 1):
            st.session_state.kombinacja = k
            aktualna_kombinacja = k
    except:
        pass

if "powtorzenie" in params:
    try:
        p = int(params["powtorzenie"][0])
        if 1 <= p <= max(liczba_ocen, 1):
            st.session_state.powtorzenie = p
            aktualne_powtorzenie = p
    except:
        pass

st.markdown(
    f"<h3 style='color: #7f8c8d;'>Kombinacja {aktualna_kombinacja} – Powtórzenie {aktualne_powtorzenie}</h3>",
    unsafe_allow_html=True,
)

# --- Formularz ---
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

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        poprzednie_disabled = aktualne_powtorzenie <= 1
        poprzednie = st.form_submit_button("Poprzednie powtórzenie", disabled=poprzednie_disabled)
    with col2:
        zapisz = st.form_submit_button("Zapisz oceny")
    with col3:
        nastepne_disabled = aktualne_powtorzenie >= liczba_ocen or liczba_ocen == 0
        nastepne = st.form_submit_button("Następne powtórzenie", disabled=nastepne_disabled)

if zapisz or poprzednie or nastepne:
    rekord = {"Kombinacja": aktualna_kombinacja, "Powtórzenie": aktualne_powtorzenie}
    rekord.update(wartosci)

    if istniejacy_rekord:
        index = st.session_state.zebrane_dane.index(istniejacy_rekord)
        st.session_state.zebrane_dane[index] = rekord
    else:
        st.session_state.zebrane_dane.append(rekord)

    if poprzednie and aktualne_powtorzenie > 1:
        st.session_state.powtorzenie -= 1
        st.experimental_rerun()
    elif nastepne and aktualne_powtorzenie < liczba_ocen:
        st.session_state.powtorzenie += 1
        st.experimental_rerun()
    else:
        st.experimental_rerun()

# --- Wyświetlanie wyników dla aktualnej kombinacji i powtórzenia ---
st.markdown("### Aktualne zapisane wyniki dla tej kombinacji i powtórzenia")
if istniejacy_rekord:
    pokaz = {k: v for k, v in istniejacy_rekord.items() if k not in ["Kombinacja", "Powtórzenie"]}
    df_wyniki = pd.DataFrame(pokaz.items(), columns=["Cecha", "Wartość"])
    st.table(df_wyniki)
else:
    st.info("Brak zapisanych wyników dla tej kombinacji i powtórzenia.")

st.write("---")

# --- Średnie z całego zbioru ---
if st.session_state.zebrane_dane:
    df_all = pd.DataFrame(st.session_state.zebrane_dane)
    df_all.fillna(0, inplace=True)
    for cecha in wszystkie_cechy:
        df_all[cecha] = pd.to_numeric(df_all[cecha], errors="coerce").fillna(0)
    srednie = df_all[wszystkie_cechy].mean().round(2)
    srednie_df = srednie.reset_index()
    srednie_df.columns = ["Cecha", "Średnia wartość"]
    st.markdown("### Średnie wartości podsumowane dla wszystkich kombinacji i powtórzeń")
    st.table(srednie_df)
else:
    st.info("Brak danych do wyliczenia średnich.")

st.write("---")

# Eksport danych
if st.button("Eksportuj wszystko do Excela"):
    df_export = pd.DataFrame(st.session_state.zebrane_dane)
    df_export.to_excel("oceny_krokowe.xlsx", index=False)
    st.success("Zapisano jako 'oceny_krokowe.xlsx'")
