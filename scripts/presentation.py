import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_modern_presentation():
    prs = Presentation()
    # Format 16:9 moderne
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # Palette de couleurs Boréal Assurances
    NAVY = RGBColor(15, 23, 42)       # #0F172A
    BLUE = RGBColor(37, 99, 235)      # #2563EB
    LIGHT_BG = RGBColor(248, 250, 252) # #F8FAFC
    WHITE = RGBColor(255, 255, 255)
    DARK_TEXT = RGBColor(30, 41, 59)
    MUTED_TEXT = RGBColor(100, 116, 139)
    CARD_BG = RGBColor(238, 242, 255) # Bleu très doux
    ACCENT_GREEN = RGBColor(16, 185, 129)

    blank_layout = prs.slide_layouts[6]

    def add_header(slide, title_text, category="BORÉAL ASSURANCES — SOUTENANCE"):
        # Bandeau haut
        header_box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.1))
        header_box.fill.solid()
        header_box.fill.fore_color.rgb = NAVY
        header_box.line.color.rgb = NAVY

        tf = header_box.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.6)
        tf.margin_top = Inches(0.15)

        p_cat = tf.paragraphs[0]
        p_cat.text = category.upper()
        p_cat.font.size = Pt(10)
        p_cat.font.bold = True
        p_cat.font.color.rgb = BLUE

        p_title = tf.add_paragraph()
        p_title.text = title_text
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = WHITE

    
    # SLIDE 1: COUVERTURE (Style Sombre)
    
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = NAVY
    bg1.line.color.rgb = NAVY

    # Box Titre
    tb1 = s1.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(11.333), Inches(3.5))
    tf1 = tb1.text_frame
    tf1.word_wrap = True

    p = tf1.paragraphs[0]
    p.text = "BORÉAL ASSURANCES"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = BLUE

    p2 = tf1.add_paragraph()
    p2.text = "Entrepôt de Données & Dashboard Décisionnel"
    p2.font.size = Pt(36)
    p2.font.bold = True
    p2.font.color.rgb = WHITE

    p3 = tf1.add_paragraph()
    p3.text = "Soutenance du Projet Boréal"
    p3.font.size = Pt(20)
    p3.font.color.rgb = MUTED_TEXT

    p4 = tf1.add_paragraph()
    p4.text = "\nPrésenté par : Christe Celina KAYA MAXIME"
    p4.font.size = Pt(14)
    p4.font.color.rgb = WHITE

    
    # SLIDE 2: CONTEXTE & ENJEUX
    
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "1. Contexte & Enjeux Business")

    # 3 Cartes côte à côte
    cards = [
        ("Problématique", "• Multiplicité des sources (CRM, Contrats, Sinistres, 64 Règlements).\n• Présence d'anomalies de saisie (primes <= 0, incohérences de dates).\n• Reporting manuel lourd et risqué."),
        ("Objectifs Techniques", "• Unifier les flux dans DuckDB (Architecture Médaillon).\n• Automatiser les contrôles qualité (Quarantaine R01-R15).\n• Reconstitution instantanée et reproductible du DWH."),
        ("Impact Business", "• Vision 360° du portefeuille et du ratio S/P.\n• Identification des clients clés (Analyse de Pareto).\n• Dashboard interactif Streamlit pour le pilotage.")
    ]

    for i, (title, content) in enumerate(cards):
        left = Inches(0.8 + i * 3.9)
        card = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, Inches(1.8), Inches(3.6), Inches(5.0))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = BLUE

        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Inches(0.25)
        tf.margin_top = Inches(0.3)

        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.color.rgb = NAVY

        p_body = tf.add_paragraph()
        p_body.text = f"\n{content}"
        p_body.font.size = Pt(13)
        p_body.font.color.rgb = DARK_TEXT

    
    # SLIDE 3: ARCHITECTURE MÉDAILLON
    
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "2. Architecture Médaillon sous DuckDB")

    layers = [
        ("🟤 Couche RAW", "Ingestion Brute", "• Stockage des fichiers sources CSV & Parquet.\n• Conservation de l'historique sans altération.\n• Ingestion rapide de 64 fichiers de règlements."),
        ("⚪ Couche PREP", "Qualité & Nettoyage", "• Application dynamique des règles R01 à R15.\n• Isolation automatique en table prep.quarantaine.\n• Typage fort et dédoublonnage."),
        ("🟡 Couche DWH", "Modèle en Étoile", "• Schéma dimensionnel de Kimball.\n• Table de faits (contrats, sinistres, règlements).\n• Clés substitutives (SK) et performances DuckDB.")
    ]

    for i, (l_title, l_sub, l_desc) in enumerate(layers):
        top = Inches(1.6 + i * 1.8)
        box = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), top, Inches(11.733), Inches(1.5))
        box.fill.solid()
        box.fill.fore_color.rgb = WHITE
        box.line.color.rgb = BLUE

        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.3)

        p = tf.paragraphs[0]
        p.text = f"{l_title}  —  {l_sub}"
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = NAVY

        p_desc = tf.add_paragraph()
        p_desc.text = l_desc
        p_desc.font.size = Pt(12)
        p_desc.font.color.rgb = DARK_TEXT

    
    # SLIDE 4: QUALITÉ ET QUARANTAINE
    
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "3. Contrôle Qualité & Bilan Quarantaine")

    # Carte gauche : Règles
    c_left = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.6), Inches(6.0), Inches(5.2))
    c_left.fill.solid()
    c_left.fill.fore_color.rgb = WHITE
    c_left.line.color.rgb = BLUE

    tf_l = c_left.text_frame
    tf_l.word_wrap = True
    tf_l.margin_left = Inches(0.3)
    p = tf_l.paragraphs[0]
    p.text = "Règles de Validation (R01 à R15)"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = NAVY

    p_body = tf_l.add_paragraph()
    p_body.text = "\n• R05 : Primes annuelles <= 0€ (Rejeté)\n• R06 : Date résiliation < Date effet\n• R10 : Date déclaration < Date survenance\n• R11/R15 : Sinistres ou règlements orphelins (sans contrat)\n\n--> Mécanisme non bloquant : Le pipeline continue d'alimenter le DWH avec les lignes valides."
    p_body.font.size = Pt(13)
    p_body.font.color.rgb = DARK_TEXT

    # Carte droite : Bilan Chiffré
    c_right = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.2), Inches(1.6), Inches(5.333), Inches(5.2))
    c_right.fill.solid()
    c_right.fill.fore_color.rgb = CARD_BG
    c_right.line.color.rgb = BLUE

    tf_r = c_right.text_frame
    tf_r.word_wrap = True
    tf_r.margin_left = Inches(0.3)

    p = tf_r.paragraphs[0]
    p.text = "Bilan du Dernier Execution"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = NAVY

    p_kpi = tf_r.add_paragraph()
    p_kpi.text = "\n87 Lignes en Quarantaine"
    p_kpi.font.size = Pt(28)
    p_kpi.font.bold = True
    p_kpi.font.color.rgb = BLUE

    p_details = tf_r.add_paragraph()
    p_details.text = "\n- R05 (Primes invalides) : 25 lignes\n- R15 (Règlements orphelins) : 22 lignes\n- R06 (Dates contrats) : 20 lignes\n- R10 (Dates sinistres) : 15 lignes\n- R11 (Sinistres orphelins) : 5 lignes\n\nConformité Globale : 99.4%"
    p_details.font.size = Pt(13)
    p_details.font.color.rgb = DARK_TEXT

    
    # SLIDE 5: DÉMO LIVE 1 PIPELINE
    
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "4. Démonstration Live : Pipeline ETL Orchestré")

    box_demo = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(11.733), Inches(4.8))
    box_demo.fill.solid()
    box_demo.fill.fore_color.rgb = NAVY
    box_demo.line.color.rgb = NAVY

    tf_d = box_demo.text_frame
    tf_d.word_wrap = True
    tf_d.margin_left = Inches(0.5)

    p = tf_d.paragraphs[0]
    p.text = "> Executing Live Demonstration in Terminal..."
    p.font.size = Pt(16)
    p.font.color.rgb = ACCENT_GREEN

    p_cmd = tf_d.add_paragraph()
    p_cmd.text = "\nCommande exécutée :\npython scripts/run_pipeline.py"
    p_cmd.font.size = Pt(22)
    p_cmd.font.bold = True
    p_cmd.font.color.rgb = WHITE

    p_steps = tf_d.add_paragraph()
    p_steps.text = "\nÉtape 1 : Ingestion Raw (01_ingest_raw.py) --> [OK]\nÉtape 2 : Qualité & Quarantaine (02_quality_prep.py) --> 87 isolés\nÉtape 3 : Alimentation DWH (02_schema.py) --> 20 109 faits contrats\nÉtape 4 : Génération Pareto (04_valeur_clients.py) --> Graphique généré"
    p_steps.font.size = Pt(15)
    p_steps.font.color.rgb = RGBColor(226, 232, 240)

    
    # SLIDE 6: DÉMO LIVE 2 DASHBOARD STREAMLIT
    
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "5. Démonstration Live : Dashboard Streamlit")

    pages_st = [
        ("📊 Page 1 : Portefeuille", "• KPIs stratégiques (Primes, Sinistres, S/P Global).\n• Distribution géographique et démographique.\n• Évolution temporelle des souscriptions."),
        ("📈 Page 2 : Analyse Technique", "• Courbe de Pareto (Concentration de la valeur Top 10%).\n• Matrice de rétention par cohorte.\n• Ratios S/P par tranche d'âge et garanties."),
        ("⚙️ Page 3 : Exploitation", "• Fraîcheur des données dynamiques (J-0).\n• Suivi des volumes par couche (Raw/Prep/DWH).\n• Audit en direct des lignes en quarantaine.")
    ]

    for i, (p_title, p_desc) in enumerate(pages_st):
        left = Inches(0.8 + i * 3.9)
        card = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, Inches(1.8), Inches(3.6), Inches(5.0))
        card.fill.solid()
        card.fill.fore_color.rgb = WHITE
        card.line.color.rgb = BLUE

        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.25)

        p = tf.paragraphs[0]
        p.text = p_title
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = NAVY

        p_b = tf.add_paragraph()
        p_b.text = f"\n{p_desc}"
        p_b.font.size = Pt(13)
        p_b.font.color.rgb = DARK_TEXT

    
    # SLIDE 7: CONCLUSION
    
    s7 = prs.slides.add_slide(blank_layout)
    bg7 = s7.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg7.fill.solid()
    bg7.fill.fore_color.rgb = NAVY
    bg7.line.color.rgb = NAVY

    tb7 = s7.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(11.333), Inches(4.5))
    tf7 = tb7.text_frame
    tf7.word_wrap = True

    p = tf7.paragraphs[0]
    p.text = "CONCLUSION & PERSPECTIVES"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = BLUE

    p2 = tf7.add_paragraph()
    p2.text = "Projet Intégrateur Boréal Assurances Finalisé avec Succès"
    p2.font.size = Pt(28)
    p2.font.bold = True
    p2.font.color.rgb = WHITE

    p3 = tf7.add_paragraph()
    p3.text = "\nRecommandations Métier :\n1. Réajustement tarifaire sur les segments à fort ratio S/P (jeunes conducteurs).\n2. Politiques de fidélisation ciblées sur le Top 10% des clients rentables (Pareto).\n\nMerci de votre attention !"
    p3.font.size = Pt(16)
    p3.font.color.rgb = RGBColor(226, 232, 240)

    # Sauvegarde
    output_filename = "KAYA_Boreal_Presentation.pptx"
    prs.save(output_filename)
    print(f"[SUCCÈS] Présentation moderne régénérée avec succès : {output_filename}")

if __name__ == "__main__":
    create_modern_presentation()