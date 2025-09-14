import streamlit as st
import pandas as pd
from spese_app.db import DatabaseManager
from spese_app.llm import ExpenseLLM
import sys

db = DatabaseManager()
llm = ExpenseLLM()

# --- Funzione per formattare importi in stile italiano ---
def format_importo_(val):
    """Formatta un numero come valuta in stile italiano (es: 1.000,00 €)."""
    return f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " €"

def main():
    st.title("💰 Gestione Entrate/Uscite Personali")

    # --- Inserimento transazioni ---
    st.subheader("➕ Aggiungi transazione")
    with st.form("transaction_form"):
        tipo = st.radio("Tipo di transazione", ["entrata", "uscita"])
        categoria = st.text_input("Categoria (es. Stipendio, Spesa, Affitto...)")
        importo_ = st.number_input("importo_ (€)", min_value=0.01, format="%.2f")
        col1, col2, col3 = st.columns(3)
        giorno = col1.number_input("Giorno", min_value=1, max_value=31, value=1)
        mese = col2.number_input("Mese", min_value=1, max_value=12, value=1)
        anno = col3.number_input("Anno", min_value=2000, max_value=2100, value=2025)

        submitted = st.form_submit_button("Salva")
        if submitted:
            db.add_transaction(tipo, categoria, importo_, giorno, mese, anno)
            st.success("Transazione salvata!")

    # --- Filtri & Report ---
    st.subheader("📊 Report")
    col1, col2 = st.columns(2)
    mese_filtro = col1.selectbox("Mese", options=["Tutti"] + list(range(1, 13)))
    anno_filtro = col2.number_input("Anno", min_value=2000, max_value=2100, value=2025)

    if mese_filtro == "Tutti":
        transactions = db.get_transactions(anno=anno_filtro)
    else:
        transactions = db.get_transactions(mese=int(mese_filtro), anno=anno_filtro)

    if transactions:
        df = pd.DataFrame(transactions, columns=["id", "tipo", "categoria", "importo_", "giorno", "mese", "anno"])

        # Applica formattazione
        df["importo"] = df["importo_"].apply(format_importo_)

        st.write("### Entrate")
        st.table(df[df["tipo"] == "entrata"][["giorno", "mese", "anno", "categoria", "importo"]])

        st.write("### Uscite")
        st.table(df[df["tipo"] == "uscita"][["giorno", "mese", "anno", "categoria", "importo"]])

        entrate_tot = df[df["tipo"] == "entrata"]["importo_"].sum()
        uscite_tot = df[df["tipo"] == "uscita"]["importo_"].sum()
        saldo = entrate_tot - uscite_tot

        st.metric("Totale Entrate", format_importo_(entrate_tot))
        st.metric("Totale Uscite", format_importo_(uscite_tot))
        st.metric("Saldo", format_importo_(saldo))

    else:
        st.warning("Nessuna transazione trovata per i filtri selezionati.")

    # --- Reset DB ---
    st.subheader("⚙️ Gestione Database")
    if st.button("🔄 Reset Database"):
        db.reset_transactions()
        st.warning("Database resettato! Tutte le transazioni sono state cancellate.")

    # --- Chat LLM ---
    st.subheader("🤖 Chiedi a Phil per spendere meno!")
    user_question = st.text_input("Fai una domanda (es. Dove ho speso di più?)")
    if user_question:
        with st.spinner("Sto pensando..."):
            answer = llm.ask(user_question)
        st.success(answer)

# Entry point
if __name__ == "__main__":
    main()


