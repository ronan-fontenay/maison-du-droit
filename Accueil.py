# Accueil.py
# -*- coding: utf-8 -*-
import streamlit as st
import sys
import os
from PIL import Image
import datetime

# --- CORRECTION DU CHEMIN POUR IMPORTS ---
sys.path.append(os.path.dirname(__file__))
from database import get_form_config, get_options_for_table, save_entretien_complet


# --- FONCTION DE NETTOYAGE DU FORMULAIRE ---
def clear_form():
    # On convertit en liste pour pouvoir modifier le dictionnaire pendant l'itération
    for key in list(st.session_state.keys()):
        if key.startswith("in_") or key in ["multi_demandes", "multi_solutions"]:
            del st.session_state[key]


def build_home():
    st.set_page_config(
        page_title="Maison du Droit - Accueil & Saisie",
        page_icon="🏛️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # --- CSS PERSONNALISÉ POUR LE STYLE ---
    st.markdown("""
        <style>
        .big-font { font-size:20px !important; }
        .card {
            background-color: #f9f9f9;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 1px 1px 3px rgba(0,0,0,0.1);
            text-align: center;
            margin-bottom: 10px;
        }
        .main-header {
            font-size: 2.5rem;
            color: #2E4053;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- EN-TÊTE AVEC LOGO ---
    col_logo, col_titre = st.columns([1, 5])

    with col_logo:
        logo_path = "pages/logo_mdd.png"
        if os.path.exists(logo_path):
            image = Image.open(logo_path)
            st.image(image, width=130)
        else:
            st.info("🏛️")  # Fallback icône si pas d'image

    with col_titre:
        st.markdown('<h1 class="main-header">Maison du Droit</h1>', unsafe_allow_html=True)
        st.caption("Gestion administrative, Saisie des entretiens et Suivi statistique")

    st.markdown("---")

    # --- ACCÈS RAPIDE AUX AUTRES PAGES (ADMIN / STATS) ---
    with st.expander("🧭 Accès Rapide aux autres modules", expanded=False):
        c1, c2, c3 = st.columns(3)
        try:
            with c1:
                st.page_link("pages/2_Analyse_Graphique.py", label="📊 Voir les Statistiques", icon="📈",
                             use_container_width=True)
            with c2:
                st.page_link("pages/3_Export_Donnees.py",