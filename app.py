"""Tableau de bord TVA — Meridian Distribution.

Lancement :  streamlit run app.py
La page se met à jour toute seule chaque fois que vous enregistrez ce fichier.

Complétez les TODO dans l'ordre des étapes du brief. Chaque TODO porte un nom
(par exemple « CHIFFRES ») que l'étape du brief vous indique.
ATTENTION : ils ne sont pas dans l'ordre du fichier (les étapes 3 et 6 sont en haut).
Cherchez-les avec Ctrl+F (Cmd+F sur Mac).
Ne passez à l'étape suivante que quand la vérification de l'étape en cours est bonne.
"""

import pandas as pd
import plotly.express as px  # noqa: F401 — servira aux étapes 2 et 4, ne pas supprimer
import streamlit as st
import base64

def time_to_str(tps):
    h = tps // 3600000
    tps = tps % 3600000
    m = tps // 60000
    s = tps % 60000
    if h > 0:
        return f'{h:2} h {m:2} min, {s:2} s'
    elif m > 0:
        return f'{m:2} min, {s:2} s'
    return f'{s:2} s'

st.set_page_config(page_title="Référentiel TVA", 
                   page_icon="📜",
                   layout="wide",
                   initial_sidebar_state="expanded")

style_hide_streamlit = \
    """
    <style>
    MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
    body { background-color: linen; }
    { color: red; text-align: center; margin-left: 40px; }
    </style>
    """
st.markdown(style_hide_streamlit, unsafe_allow_html=True)

st.markdown("""
<style>

/* Conteneur des onglets */
.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
    background-color: #f0f2f6;
    padding: 8px;
    border-radius: 12px;
}

/* Onglets non sélectionnés */
.stTabs [data-baseweb="tab"] {
    height: 45px;
    background-color: white;
    border-radius: 8px;
    padding: 10px 20px;
    border: 1px solid #d0d5dd;
    color: #344054;
    font-weight: 600;
}

/* Onglet sélectionné */
.stTabs [aria-selected="true"] {
    background-color: #2563eb !important;
    color: white !important;
    border: 1px solid #2563eb !important;
}

/* Supprimer le soulignement natif */
.stTabs [data-baseweb="tab-highlight"] {
    background-color: transparent;
}

</style>
""", unsafe_allow_html=True)

logo_base64 = None
with open("IMAGES/logo.png", "rb") as f:
    logo_base64 = base64.b64encode(f.read()).decode()

st.markdown(f"""
<div class="banner">
    <img src="data:image/png;base64,{logo_base64}"
         width="48"
         alt="Crédit Agricole Logo">
    Qualité du référentiel TVA  
</div>

""", unsafe_allow_html=True)

# Function to load custom CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load the CSS file
local_css(""".streamlit/assets/style.css""")

# Déjà écrit pour vous. @st.cache_data évite de relire le fichier à chaque clic.
@st.cache_data
def charger_donnees():
    df = pd.read_csv(
        "data/resultats_vies.csv", parse_dates=["date_saisie", "date_verification"]
    )
    df["etape_rejet"] = df["etape_rejet"].fillna("envoyé à VIES")
    return df


# Déjà écrit pour vous : sert à l'étape 4.
def taux_invalides(donnees, colonne):
    """Pour chaque valeur de `colonne` (chaque canal, chaque pays...), calcule la part
    de numéros invalides en %. Renvoie un tableau à deux colonnes : `colonne` et "taux d'erreur (%)"."""
    return (
        donnees.groupby(colonne)["statut"]
        .apply(lambda statuts: round((statuts == "invalide").mean() * 100, 1))
        .sort_values()
        .reset_index(name="taux d'erreur (%)")
    )


df = charger_donnees()

# =============================================================================
# ÉTAPE 3 — Les filtres (à faire APRÈS les étapes 1 et 2)
# =============================================================================


with st.sidebar:
    st.markdown("""<h1>⚙️ Filtres</h1>""", unsafe_allow_html=True)

    # Exemple déjà écrit : le filtre pays. Une liste vide veut dire « tous les pays ».
    pays = st.sidebar.multiselect(
        "Pays déclaré", 
        sorted(df["pays_declare"].unique()),
        help=("Filtre par pays.")
    )

    # TODO FILTRE_CANAL (étape 3a) : sur le même modèle, un filtre « Canal de saisie » sur la colonne source_saisie.
    canal = st.sidebar.multiselect(
        "Canal de saisie", 
        sorted(df["source_saisie"].unique()),
        help=("Filtre par source")
    )

    # TODO FILTRE_PERIODE (étape 3b) : un filtre « Période de saisie » avec st.sidebar.slider (voir le brief).
    debut, fin = st.sidebar.slider(
        "Période de saisie",
        min_value=df["date_saisie"].min().date(),
        max_value=df["date_saisie"].max().date(),
        value=(df["date_saisie"].min().date(), df["date_saisie"].max().date()),
        format="DD/MM/YYYY",
    )

    radio_background = st.radio(
        "Changer le fond d'écran :", ["Jaune", "Bleu"],
        help=("Faire la recherche dans le titre uniquement ou bien dans le contenu du document."),
        index = 0, horizontal = True)

    radio_card = st.radio(        
        "Changer l'apparence de la synthèse :", ["Initial", "Custom"],
        index = 0, horizontal = True)

    col1, col2 = st.columns(2)
    
    with col1:
        couleur_debut = st.color_picker(
            "Début",
            "#e2e387",
            label_visibility="collapsed"
        )

    with col2:
        couleur_fin = st.color_picker(
            "Fin",
            "#e5c1b2",
            label_visibility="collapsed"
        )
        
    st.markdown(f"""
        <style>
        [data-testid="stSidebar"] {{
            background: linear-gradient(
                180deg,
                {couleur_debut},
                {couleur_fin}
            );
        }}
        </style>
    """, unsafe_allow_html=True)

image_base64 = None

if radio_background == "Jaune":
    with open("IMAGES/20449.jpg", "rb") as f:
        image_base64 = base64.b64encode(f.read()).decode()

elif radio_background == "Bleu":
    with open("IMAGES/12441.jpg", "rb") as f:
        image_base64 = base64.b64encode(f.read()).decode()

# Injection du CSS
st.markdown(f"""
<style>

.stApp {{
    background:
        linear-gradient(
                rgba(255, 255, 255, 0.45),
                rgba(255, 255, 255, 0.45)
            ),
        url("data:image/jpeg;base64,{image_base64}")
        no-repeat center center fixed;
    background-size: cover;
}}

</style>
""", unsafe_allow_html=True)


# `selection` contient les lignes qui passent les filtres. Toute la suite utilise
# `selection`, jamais `df` : c'est ce qui fait réagir la page aux filtres.
selection = df

if pays:
    selection = selection[selection["pays_declare"].isin(pays)]

# TODO APPLIQUER_FILTRES (étape 3c) : appliquer le filtre canal et le filtre période à `selection`.
#           Toujours `selection = selection[...]`, jamais `selection = df[...]`.
if canal:
    selection = selection[selection["source_saisie"].isin(canal)]

# Filtre par période
selection = selection[selection["date_saisie"].dt.date.between(debut, fin)]


# ======================================================================================================

synthese, erreurs, a_traiter, delais = st.tabs(["📊 Synthèse", "🔍 Erreurs", "🎯 À traiter", "⏱️ Délais"], on_change="rerun")

with synthese:
    # =============================================================================
    # ÉTAPE 6 — Rendre la page lisible par tous (à faire APRÈS l'étape 5)
    # =============================================================================
    # TODO AIDE (étape 6a) : une phrase d'aide pour la directrice financière (st.write).
    st.write("""Résultats de la campagne VIES<br>
            Total des numéros valides / invalides / à trancher<br> \
            Répartition des numéros valides / invalides en fonction du pays et en fonction de la source de saisie
            """, unsafe_allow_html=True)

    # TODO DATE_REGLE (étape 6b) : la date de la dernière vérification VIES et la règle pour les non tranchés (st.info).
    st.info(f"""Date de la dernière vérification VIES : {df["date_verification"].max().date():%d/%m/%Y à %H:%M}\n
    Règles :\n
    - valide : VIES a confirmé le numéro
    - invalide : VIES a refusé le numéro, ou le numéro a été écarté avant l'envoi parce qu'il était absent ou mal formé
    - non_tranche : VIES n'a pas pu répondre (service du pays indisponible, délai dépassé). Ce n'est ni valide ni invalide
    """, icon="ℹ️")


    # =============================================================================
    # ÉTAPE 1 — Les quatre chiffres clés
    # =============================================================================
    col1, col2, col3, col4 = st.columns(4)
    # TODO CHIFFRES (étape 1) : dans col2, col3 et col4, le nombre de valides, d'invalides et de non tranchés,
    #          chacun avec son pourcentage du total.

    total = len(selection)
    valides = (selection["statut"] == "valide").sum()
    invalides = (selection["statut"] == "invalide").sum()
    non_tranches = (selection["statut"] == "non_tranche").sum()

    if radio_card == "Custom":
        with col1:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Total</div>
                <div class="kpi-value">📊 {total}</div>
                <div class="kpi-subtitle">&nbsp;</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Valides</div>
                <div class="kpi-value">🟢 {valides}</div>
                <div class="kpi-subtitle">{valides / total:.1%} du total</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Invalides</div>
                <div class="kpi-value">🔴 {invalides}</div>
                <div class="kpi-subtitle">{invalides / total:.1%} du total</div>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Non tranchés</div>
                <div class="kpi-value">⚖️ {non_tranches}</div>
                <div class="kpi-subtitle">{non_tranches / total:.1%} du total</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        col1.metric("Numéros", total)
        col2.metric("Valides", valides, f"{valides / total:.1%} du total", delta_color="green")
        col3.metric("Invalides", invalides, f"{invalides / total:.1%} du total", delta_color="red")
        col4.metric("Non tranchés", non_tranches, f"{non_tranches / total:.1%} du total", delta_color="blue")


    # =============================================================================
    # ÉTAPE 2 — L'entonnoir
    # =============================================================================
    st.subheader("Combien de numéros ont pu être envoyés à VIES ?")
    # TODO ENTONNOIR (étape 2) : compter, étape par étape, les numéros qui restent après le retrait des absents,
    #          des doublons, puis des numéros mal formés, et les afficher avec px.funnel.
    nb_absent    = (selection['etape_rejet'] == 'absent').sum()
    nb_doublon   = (selection['etape_rejet'] == 'doublon').sum()
    nb_structure = (selection['etape_rejet'] == "structure").sum()

    entonnoir = pd.DataFrame({
        "étape": ["Référentiel", "Sans les absents", "Sans les doublons", "Envoyés à VIES"],
        "numéros": [total,
                    total - nb_absent,
                    total - nb_absent - nb_doublon,
                    total - nb_absent - nb_doublon - nb_structure],
    })
    fig = px.funnel(entonnoir, x="numéros", y="étape",
                    title="Du référentiel aux numéros envoyés à VIES")
    st.plotly_chart(fig)


with erreurs:
    # =============================================================================
    # ÉTAPE 4 — D'où viennent les erreurs ?
    # =============================================================================
    st.subheader("D'où viennent les erreurs ?")
    # TODO GRAPHIQUES (étape 4) : avec taux_invalides(selection, "source_saisie"), puis "pays_declare",
    #          deux graphiques en barres horizontales avec la valeur écrite sur chaque barre,
    #          puis une phrase (st.caption) qui explique quel canal sort du lot.
    taux = taux_invalides(selection, "source_saisie")
    fig = px.bar(taux, x="taux d'erreur (%)", y="source_saisie", orientation="h",
                text="taux d'erreur (%)", title="Part de numéros invalides par canal de saisie")
    st.plotly_chart(fig)

    st.caption("Remarque : Les données venant du canal 'reprise_erp' sont sources d'erreurs \
            car provenant de l'ancien logiciel ERP")

    taux = taux_invalides(selection, "pays_declare")
    fig = px.bar(taux, x="taux d'erreur (%)", y="pays_declare", orientation="h",
                text="taux d'erreur (%)", title="Part de numéros invalides par pays")
    st.plotly_chart(fig)


with a_traiter:
    # =============================================================================
    # ÉTAPE 5 — Les numéros à traiter
    # =============================================================================
    st.subheader("Numéros à traiter")
    # TODO A_TRAITER (étape 5) : la liste des invalides et des non tranchés, avec une colonne « action »,
    #          et un bouton pour la télécharger.
    # 1. Garder les lignes dont le statut n'est pas "valide" (!= veut dire « différent de »)
    a_traiter = selection[selection["statut"] != "valide"].copy()

    # 2. Ajouter une colonne "action" : .map remplace chaque statut par le texte associé
    a_traiter["action"] = a_traiter["statut"].map({
        "invalide": "Demander un nouveau numéro au client",
        "non_tranche": "Revérifier sur VIES avant la prochaine facture",
    })

    # 3. Afficher le nombre et le tableau, avec les colonnes utiles pour la comptabilité
    colonnes = ["raison_sociale", "numero_saisi", "pays_declare", "statut", "motif", "action"]
    st.write(f"{len(a_traiter)} numéros demandent une action.")
    st.dataframe(a_traiter[colonnes], hide_index=True)

    # 4. Le bouton de téléchargement
    st.download_button(
        "Télécharger la liste",
        a_traiter[colonnes].to_csv(index=False, sep=";").encode("utf-8-sig"),
        file_name="numeros_a_traiter.csv",
        icon=":material/download:",
    )

with delais:
    # =============================================================================
    # ÉTAPE 7 — BONUS
    # =============================================================================
    st.subheader("Temps de réponses VIES")
    median = selection['temps_reponse_ms'].median()
    st.write(f"Médiane des temps de réponse VIES :\t {median} ms")
    group = selection.groupby('pays_declare')['temps_reponse_ms'].median().sort_values()
    st.bar_chart(group)

    st.subheader("Graphique des non tranchés par pays")
    df_non_tranches = df[df["statut"] == "non_tranche"]
    group = df_non_tranches.groupby('pays_declare')['temps_reponse_ms'].count()
    st.bar_chart(group)