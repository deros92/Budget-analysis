import os
from dotenv import load_dotenv
from google import genai
import sqlite3
import pandas as pd

DB_NAME = "spese.db"

# Carica chiave API da .env
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

class ExpenseLLM:
    def __init__(self):
        if not API_KEY:
            raise ValueError("Chiave API Gemini non trovata! Controlla il file .env")
        # Inizializza client Gemini
        self.client = genai.Client(api_key=API_KEY)

    def get_summary_from_db(self):
        conn = sqlite3.connect(DB_NAME)
        df = pd.read_sql_query("SELECT tipo, categoria, importo, mese, anno FROM transactions", conn)
        conn.close()
        if df.empty:
            return "Nessuna transazione registrata."
        summary = df.groupby(["tipo", "categoria"])[["importo"]].sum().reset_index()
        return summary.to_string(index=False)

    def ask(self, question: str) -> str:
        summary = self.get_summary_from_db()
        prompt = f"Sei Phil, un assistente finanziario che deve rispondere in maniera sintetica ma efficace. Ecco i dati:\n{summary}\nDomanda: {question}\nRisposta:"
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text
