# pages/2_Analyse_Graphique.py
import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database import get_db_connection, get_translation_dictionary

st.set_page_config(layout="wide", page_title="Analyse Graphique", page_icon="📊")

# --- AJOUT LOGO SIDEBAR ---
logo_path = "logo_mdd.png"
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, width=100)
st.sidebar.markdown("---")

# =========================================================================
# GRANDES THÉMATIQUES (déduites du chiffre en tête du code : 1a -> 1)
# =========================================================================
THEMES_DEMANDE = {
    "1": "Droit de la famille / des personnes",
    "2": "Droit du logement",
    "3": "Droit de la consommation",
    "4": "Autres domaines du droit civil",
    "5": "Droit du travail / affaires / associations",
    "6": "Droit de la protection sociale",
    "7": "Droit pénal",
    "8": "Droit administratif",
    "9": "Démarches et formalités",
}
THEMES_SOLUTION = {
    "1": "Information",
    "2": "Aide aux démarches",
    "3": "Aide à la rédaction",
    "4": "Orientation professionnel du droit",
    "5": "Orientation MARD",
    "6": "Orientation administration",
    "7": "Orientation association",
    "8": "Orientation santé / social",
    "9": "Orientation organisme privé",
}

# Colonnes pouvant contenir plusieurs valeurs par dossier (séparées par " | ")
MULTI_COLS = ['nature_demande', 'theme_demande', 'reponse_orientation', 'theme_solution']
# Lien "détail -> thématique" pour une même table
CHILD_PARENT = {'nature_demande': 'theme_demande', 'reponse_orientation': 'theme_solution'}
SEP = ' | '


def theme_code(code):
    """'1a' -> '1', '10' -> '10', None -> None"""
    m = re.match(r'\d+', str(code)) if code is not None else None
    return m.group(0) if m else None


def split_multi(x):
    return [v.strip() for v in str(x).split(SEP) if v.strip()]


def codes_to_themes(s, mapping):
    if pd.isna(s) or str(s).strip() == "":
        return "Non renseigné"
    return SEP.join(mapping.get(c.strip(), c.strip()) for c in str(s).split(SEP))


@st.cache_data(ttl=60)
def load_and_prep_data():
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame(), {}

    try:
        query = """
            SELECT e.*,
                   (SELECT string_agg(m_dem.lib_m, ' | ' ORDER BY d.pos)
                    FROM DEMANDE d
                    LEFT JOIN MODALITE m_dem ON d.nature = m_dem.code AND m_dem.tab = 'DEMANDE' AND m_dem.pos = 3
                    WHERE d.num = e.num) AS nature_demande,
                   (SELECT string_agg(DISTINCT substring(d.nature::text from '^[0-9]+'), ' | ')
                    FROM DEMANDE d
                    WHERE d.num = e.num) AS theme_demande,
                   (SELECT string_agg(m_sol.lib_m, ' | ' ORDER BY s.pos)
                    FROM SOLUTION s
                    LEFT JOIN MODALITE m_sol ON s.nature = m_sol.code AND m_sol.tab = 'SOLUTION' AND m_sol.pos = 3
                    WHERE s.num = e.num) AS reponse_orientation,
                   (SELECT string_agg(DISTINCT substring(s.nature::text from '^[0-9]+'), ' | ')
                    FROM SOLUTION s
                    WHERE s.num = e.num) AS theme_solution
            FROM ENTRETIEN e
            ORDER BY e.date_ent
        """
        df = pd.read_sql(query, conn)

        # Correspondance libellé détaillé -> grande thématique
        df_mod = pd.read_sql(
            "SELECT tab, code, lib_m FROM MODALITE WHERE tab IN ('DEMANDE', 'SOLUTION') AND pos = 3", conn
        )
        conn.close()
        transco = get_translation_dictionary()

        theme_of = {'nature_demande': {}, 'reponse_orientation': {}}
        for _, r in df_mod.iterrows():
            tc = theme_code(r['code'])
            if r['tab'] == 'DEMANDE':
                theme_of['nature_demande'][r['lib_m']] = THEMES_DEMANDE.get(tc, "Non renseigné")
            else:
                theme_of['reponse_orientation'][r['lib_m']] = THEMES_SOLUTION.get(tc, "Non renseigné")

        if df.empty:
            return df, theme_of

        df.columns = [c.lower() for c in df.columns]
        if 'date_ent' in df.columns:
            df['date_ent'] = pd.to_datetime(df['date_ent'])
            df['mois'] = df['date_ent'].dt.strftime('%Y-%m')

        for col, mapping in transco.items():
            if col in df.columns:
                df[col] = df[col].map(mapping).fillna(df[col])
                df[col] = df[col].fillna("Non renseigné").astype(str)

        # Codes de thématique -> libellés
        df['theme_demande'] = df['theme_demande'].apply(lambda s: codes_to_themes(s, THEMES_DEMANDE))
        df['theme_solution'] = df['theme_solution'].apply(lambda s: codes_to_themes(s, THEMES_SOLUTION))

        for col in ['nature_demande', 'reponse_orientation']:
            df[col] = df[col].fillna("Non renseigné").astype(str)

        return df, theme_of
    except Exception as e:
        st.error(f"Erreur data : {e}")
        return pd.DataFrame(), {}


st.title("📊 Analyse Graphique")
st.markdown("---")

df, THEME_OF = load_and_prep_data()

if not df.empty:
    # --- FILTRES EN SIDEBAR ---
    st.sidebar.header("🔍 Filtres")
    df_filtered = df.copy()
    excluded_cols = ['num', 'date_ent', 'mois']
    available_filters = [c for c in df.columns if c not in excluded_cols]

    filtres_actifs = st.sidebar.multiselect("Critères de filtrage :", available_filters)

    selections = {}  # col -> set des valeurs choisies (réutilisé pour le graphique)
    for col in filtres_actifs:
        if col in MULTI_COLS:
            valeurs = sorted({v for x in df[col] for v in split_multi(x)})
        else:
            valeurs = sorted(df[col].astype(str).unique())

        choix = st.sidebar.multiselect(f"{col}", valeurs, key=f"filtre_{col}")

        if choix:
            choix_set = set(choix)
            selections[col] = choix_set
            if col in MULTI_COLS:
                # Garde les dossiers contenant AU MOINS une des valeurs choisies
                mask = df_filtered[col].apply(lambda x: bool(choix_set & set(split_multi(x))))
                df_filtered = df_filtered[mask]
            else:
                df_filtered = df_filtered[df_filtered[col].astype(str).isin(choix_set)]

    # --- KPI EN HAUT DE PAGE ---
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Total Dossiers", len(df))
    kpi2.metric("Dossiers Filtrés", len(df_filtered))
    pourcentage = (len(df_filtered) / len(df)) * 100 if len(df) > 0 else 0
    kpi3.metric("% du total", f"{pourcentage:.1f} %")

    st.markdown("---")

    # --- CONFIGURATION GRAPHIQUE ---
    with st.container():
        st.subheader("Visualisation")
        c1, c2, c3 = st.columns([1, 2, 1])
        with c1:
            type_graph = st.selectbox("Type de graphique", ["Barres", "Camembert", "Courbe", "Treemap"])
        with c2:
            cols_x = [c for c in df.columns if c != 'num']
            var_x = st.selectbox("Axe X / Groupe principal", cols_x, index=0)
        with c3:
            var_color = st.selectbox("Segmentation (Couleur)", ["Aucun"] + [c for c in cols_x if c != var_x])

        color_arg = None if var_color == "Aucun" else var_color

        if not df_filtered.empty:
            df_plot = df_filtered.copy()

            def explode_col(d, col):
                d = d.copy()
                d[col] = d[col].apply(split_multi)
                d = d.explode(col)
                d[col] = d[col].fillna("Non renseigné")
                return d

            def restrict(d, col):
                """Après éclatement, ne garde que les lignes cohérentes avec les filtres,
                pour 'isoler' graphiquement les valeurs choisies."""
                if col in selections:
                    d = d[d[col].isin(selections[col])]
                parent = CHILD_PARENT.get(col)
                if parent and parent in selections:
                    d = d[d[col].map(THEME_OF.get(col, {})).isin(selections[parent])]
                return d

            to_explode = [c for c in [var_x, color_arg] if c in MULTI_COLS]

            # Cas particulier : détail + thématique de la même table (ex. X = nature_demande,
            # couleur = theme_demande). On éclate le détail et on en déduit la thématique,
            # sinon on obtiendrait un produit croisé incohérent.
            pair = next(((ch, pa) for ch, pa in CHILD_PARENT.items() if {ch, pa} <= set(to_explode)), None)
            if pair:
                child, parent = pair
                df_plot = explode_col(df_plot, child)
                df_plot[parent] = df_plot[child].map(THEME_OF.get(child, {})).fillna("Non renseigné")
                df_plot = restrict(df_plot, child)
                df_plot = restrict(df_plot, parent)
                to_explode = [c for c in to_explode if c not in pair]

            for c in to_explode:
                df_plot = explode_col(df_plot, c)
                df_plot = restrict(df_plot, c)

            if df_plot.empty:
                st.warning("Aucune donnée avec ces filtres.")
                st.stop()

            # On compte des DOSSIERS distincts (un dossier avec 1a et 1b ne compte qu'une fois en "famille")
            def count_by(cols):
                return df_plot.groupby(cols)['num'].nunique().reset_index(name='Dossiers')

            grp = [var_x, color_arg] if color_arg else [var_x]

            if type_graph == "Barres":
                data = count_by(grp)
                fig = px.bar(data, x=var_x, y='Dossiers', color=color_arg,
                             title=f"Répartition par {var_x}", text_auto=True)
            elif type_graph == "Camembert":
                data = count_by([var_x])
                fig = px.pie(data, names=var_x, values='Dossiers', title=f"Répartition {var_x}", hole=0.4)
            elif type_graph == "Courbe":
                data = count_by(grp).sort_values(var_x)
                fig = px.line(data, x=var_x, y='Dossiers', color=color_arg, markers=True)
            elif type_graph == "Treemap":
                data = count_by(grp)
                fig = px.treemap(data, path=grp, values='Dossiers')

            st.plotly_chart(fig, use_container_width=True)

            if to_explode or pair:
                st.caption("ℹ️ Un dossier peut avoir plusieurs demandes/réponses : il peut donc apparaître "
                           "dans plusieurs barres. La somme des barres peut dépasser le nombre de dossiers filtrés.")

            with st.expander("🔎 Voir les données brutes utilisées pour ce graphique"):
                st.dataframe(df_plot, use_container_width=True)
        else:
            st.warning("Aucune donnée avec ces filtres.")
else:
    st.info("La base de données est vide.")