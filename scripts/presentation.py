import os
import matplotlib.pyplot as plt
import numpy as np
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def generate_dashboard_coherent_charts():

    os.makedirs("graphique", exist_ok=True)
    
    # Palette de couleurs du Dashboard
    BG_DARK = "#0F172A"       # Bleu nuit sombre
    TEXT_LIGHT = "#F8FAFC"    # Blanc cassé
    BLUE_STREAMLIT = "#2563EB"  # Bleu principal
    RED_STREAMLIT = "#EF4444"   # Rouge alerte
    GREEN_STREAMLIT = "#10B981" # Vert Émeraude
    GRID_COLOR = "#1E293B"    # Gris de grille

    # --- GRAPHIQUE 1 : Ratio S/P par Tranche d'Âge (Page 2 Streamlit) ---
    fig, ax = plt.subplots(figsize=(6, 3.8), facecolor=BG_DARK)
    ax.set_facecolor(BG_DARK)
    
    tranches = ['< 25 ans', '25-35 ans', '36-50 ans', '51-64 ans', '65 ans +']
    ratios_sp = [280.33, 214.54, 469.85, 268.02, 281.97]
    
    bars = ax.bar(tranches, ratios_sp, color=RED_STREAMLIT, alpha=0.9, zorder=2)
    
    ax.set_title("Dashboard : Ratio S/P (%) par Tranche d'Âge", color=TEXT_LIGHT, fontsize=10, fontweight='bold', pad=12)
    ax.tick_params(colors=TEXT_LIGHT, labelsize=8)
    ax.set_ylabel("Ratio S/P (%)", color=TEXT_LIGHT, fontsize=8)
    ax.grid(color=GRID_COLOR, linestyle='--', linewidth=0.5, zorder=1)
    
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.1f}%',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', color=TEXT_LIGHT, fontsize=7)

    for spine in ax.spines.values(): spine.set_color(GRID_COLOR)

    plt.tight_layout()
    chart1_path = os.path.join("graphique", "chart_sp_age.png")
    plt.savefig(chart1_path, dpi=200, facecolor=BG_DARK)
    plt.close()

    # --- GRAPHIQUE 2 : Délais de Gestion (Médiane vs P90) ---
    fig, ax = plt.subplots(figsize=(6, 3.8), facecolor=BG_DARK)
    ax.set_facecolor(BG_DARK)
    
    garanties = ['Tempête', 'Collision', 'Dégât Eaux', 'RC', 'Bris Glace', 'Incendie', 'Vol']
    mediane = [4, 5, 5, 5, 6, 6, 5]
    p90 = [16.8, 20.0, 19.2, 17.8, 18.7, 23.0, 25.0]

    y = np.arange(len(garanties))
    width = 0.35

    ax.barh(y - width/2, mediane, width, label='Médiane (j)', color=GREEN_STREAMLIT, zorder=2)
    ax.barh(y + width/2, p90, width, label='P90 (j)', color=BLUE_STREAMLIT, zorder=2)

    ax.set_yticks(y)
    ax.set_yticklabels(garanties, color=TEXT_LIGHT, fontsize=8)
    ax.tick_params(colors=TEXT_LIGHT, labelsize=8)
    ax.set_xlabel("Jours de Gestion", color=TEXT_LIGHT, fontsize=8)
    ax.set_title("Dashboard : Délais Médiane vs P90 par Garantie", color=TEXT_LIGHT, fontsize=10, fontweight='bold', pad=12)
    ax.legend(facecolor=BG_DARK, edgecolor=GRID_COLOR, labelcolor=TEXT_LIGHT, fontsize=8)
    ax.grid(color=GRID_COLOR, linestyle='--', linewidth=0.5, zorder=1)

    for spine in ax.spines.values(): spine.set_color(GRID_COLOR)

    plt.tight_layout()
    chart2_path = os.path.join("graphique", "chart_delais_dashboard.png")
    plt.savefig(chart2_path, dpi=200, facecolor=BG_DARK)
    plt.close()

    return chart1_path, chart2_path


def create_complete_presentation():
    chart1_path, chart2_path = generate_dashboard_coherent_charts()
    
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    NAVY = RGBColor(15, 23, 42)          # #0F172A
    BLUE = RGBColor(37, 99, 235)         # #2563EB
    WHITE = RGBColor(255, 255, 255)
    DARK_TEXT = RGBColor(30, 41, 59)
    MUTED_TEXT = RGBColor(100, 116, 139)
    CARD_BG = RGBColor(238, 242, 255)    # Bleu doux

    blank_layout = prs.slide_layouts[6]

    def add_header(slide, title_text, category="BORÉAL ASSURANCES — DASHBOARD ANALYTICS"):
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


    # SLIDE 1: COUVERTURE
    
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = NAVY
    bg1.line.color.rgb = NAVY

    tb1 = s1.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(11.333), Inches(3.5))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    p.text = "BORÉAL ASSURANCES"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = BLUE
    p2 = tf1.add_paragraph()
    p2.text = "Construire la Chaîne de Données et Analyser le Portefeuille"
    p2.font.size = Pt(34)
    p2.font.bold = True
    p2.font.color.rgb = WHITE
    p3 = tf1.add_paragraph()
    p3.text = "Soutenance de Projet"
    p3.font.size = Pt(20)
    p3.font.color.rgb = MUTED_TEXT
    p4 = tf1.add_paragraph()
    p4.text = "\nPrésenté par : Christe Celina KAYA MAXIME"
    p4.font.size = Pt(14)
    p4.font.color.rgb = WHITE

    
    # SLIDE 2: DÉTAIL DES COUCHES
    
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "1. Architecture sous DuckDB (Détail des Couches)")

    layers = [
        ("🟤 Couche RAW (Brute)", "Ingestion Multi-Sources", "• Stockage initial sans altération des fichiers CSV & Parquet.\n• Ingestion automatisée du CRM, Contrats, Sinistres et des 64 fichiers de règlements mensuels.\n• Conservation de l'historique brut pour audit et traçabilité."),
        ("⚪ Couche PREP (Qualité)", "Nettoyage & Quarantaine", "• Application dynamique des 15 règles de gestion (R01 à R15).\n• Isolation automatique en table prep.quarantaine (87 lignes isolées au dernier run).\n• Typage fort des colonnes, dédoublonnage et validation chronologique."),
        ("🟡 Couche DWH (Entrepôt)", "Modélisation en Étoile (Kimball)", "• Création du schéma dimensionnel optimisé sous DuckDB.\n• Table de faits (20 109 faits contrats actifs, sinistres, règlements) & Dimensions.\n• Utilisation de clés substitutives (SK) et alimentation haute performance (<100ms).")
    ]

    for i, (l_title, l_sub, l_desc) in enumerate(layers):
        top = Inches(1.5 + i * 1.85)
        box = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), top, Inches(11.733), Inches(1.65))
        box.fill.solid()
        box.fill.fore_color.rgb = WHITE
        box.line.color.rgb = BLUE

        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.3)
        tf.margin_top = Inches(0.15)

        p = tf.paragraphs[0]
        p.text = f"{l_title}  —  {l_sub}"
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = NAVY

        p_desc = tf.add_paragraph()
        p_desc.text = l_desc
        p_desc.font.size = Pt(12)
        p_desc.font.color.rgb = DARK_TEXT

    
    # SLIDE 3: VUE PORTEFEUILLE & KPIS GLOBAUX
    
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "Indicateurs Clés")
    cards = [
        ("Volume & Contrats", "• Contrats Actifs : 20 109[cite: 5]\n• Taux de Résiliation : 32.5% (Alerte attrition)[cite: 5]\n• Fréquence des sinistres : 20.1%[cite: 5]"),
        ("Alerte Rentabilité", "• Ratio S/P Global : 333.0%[cite: 5]\n• Seuil d'équilibre critique dépassé (objectif < 70%)[cite: 5].\n• Coût Moyen par sinistre : 7 309 €[cite: 5]."),
        ("Pipeline Data", "• Moteur DuckDB + Streamlit.\n• 87 anomalies isolées en quarantaine.\n• Traitement robuste et non bloquant.")
    ]
    for i, (title, content) in enumerate(cards):
        card = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8 + i * 3.9), Inches(1.8), Inches(3.6), Inches(5.0))
        card.fill.solid()
        card.fill.fore_color.rgb = WHITE
        card.line.color.rgb = BLUE
        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.25)
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(17)
        p.font.bold = True
        p.font.color.rgb = NAVY
        p_b = tf.add_paragraph()
        p_b.text = f"\n{content}"
        p_b.font.size = Pt(13)
        p_b.font.color.rgb = DARK_TEXT

    
    # SLIDE 4: VISUEL RATIO S/P PAR TRANCHE D'ÂGE
    
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "3. Segmentation Technique : Ratio S/P par Tranche d'Âge")
    
    s4.shapes.add_picture(chart1_path, Inches(0.8), Inches(1.6), width=Inches(5.8))

    c_right = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.9), Inches(1.6), Inches(5.6), Inches(5.2))
    c_right.fill.solid()
    c_right.fill.fore_color.rgb = CARD_BG
    c_right.line.color.rgb = BLUE
    tf_r = c_right.text_frame
    tf_r.word_wrap = True
    tf_r.margin_left = Inches(0.3)
    p = tf_r.paragraphs[0]
    p.text = "Analyse:"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p_body = tf_r.add_paragraph()
    p_body.text = "\n• Déséquilibre Global : Tous les segments affichent des ratios S/P supérieurs à 200%[cite: 7].\n\n• Pic Critique : La tranche 36-50 ans atteint un ratio record de 469.85%[cite: 7].\n\n• Action Métier : Refonte tarifaire globale requise pour redresser la marge sur l'ensemble du portefeuille[cite: 7]."
    p_body.font.size = Pt(13)
    p_body.font.color.rgb = DARK_TEXT

    
    # SLIDE 5: VISUEL DÉLAIS DE GESTION
    
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "4. Performance Opérationnelle : Délais de Gestion")

    s5.shapes.add_picture(chart2_path, Inches(0.8), Inches(1.6), width=Inches(5.8))

    c_r5 = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.9), Inches(1.6), Inches(5.6), Inches(5.2))
    c_r5.fill.solid()
    c_r5.fill.fore_color.rgb = WHITE
    c_r5.line.color.rgb = BLUE
    tf_r5 = c_r5.text_frame
    tf_r5.word_wrap = True
    tf_r5.margin_left = Inches(0.3)
    p = tf_r5.paragraphs[0]
    p.text = "Analyse des Délais (Gouvernance) :"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p_b5 = tf_r5.add_paragraph()
    p_b5.text = "\n• Réactivité Standard : Médiane homogène entre 4 et 6 jours[cite: 10].\n\n• Goulots d'étranglement (P90) :\n  - VOL : 25 jours[cite: 10]\n  - INCENDIE : 23 jours[cite: 10]\n\n• Recommandation : Digitaliser l'instruction des dossiers complexes pour réduire le P90."
    p_b5.font.size = Pt(13)
    p_b5.font.color.rgb = DARK_TEXT

    
    # SLIDE 6: RECOMMANDATIONS STRATÉGIQUES
    
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "5. Recommandations Décisionnelles & Plan d'Action")
    recs = [
        ("1. Réajustement Tarifaire Global", "Correction des tarifs sur les segments déficitaires (ex: 36-50 ans à 469% de S/P) pour ramener le ratio global sous le seuil d'équilibre de 70%[cite: 5, 7]."),
        ("2. Programme Rétention & Lutte Anti-Attrition", "Mise en place d'actions ciblées pour enrayer le taux de résiliation élevé (32.5%) et fidéliser le portefeuille[cite: 5]."),
        ("3. Fluidification des Sinistres Complexes", "Automatisation des expertises sur les garanties Vol et Incendie pour faire baisser le P90 de 25 jours[cite: 10].")
    ]
    for i, (title, content) in enumerate(recs):
        box = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.6 + i * 1.8), Inches(11.733), Inches(1.5))
        box.fill.solid()
        box.fill.fore_color.rgb = CARD_BG
        box.line.color.rgb = BLUE
        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.3)
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = NAVY
        p_desc = tf.add_paragraph()
        p_desc.text = content
        p_desc.font.size = Pt(12)
        p_desc.font.color.rgb = DARK_TEXT

    
    # SLIDE 7: CONCLUSION
    
    s7 = prs.slides.add_slide(blank_layout)
    bg7 = s7.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg7.fill.solid()
    bg7.fill.fore_color.rgb = NAVY
    bg7.line.color.rgb = NAVY

    tb7 = s7.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(11.333), Inches(4.0))
    tf7 = tb7.text_frame
    tf7.word_wrap = True
    p = tf7.paragraphs[0]
    p.text = "CONCLUSION"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = BLUE
    p2 = tf7.add_paragraph()
    p2.text = "Boréal Assurances dispose aujourd'hui d'une plateforme data robuste et d'un outil décisionnel clé en main pour redresser sa rentabilité et piloter son portefeuille avec précision."
    p2.font.size = Pt(28)
    p2.font.bold = True
    p2.font.color.rgb = WHITE
    p3 = tf7.add_paragraph()
    p3.text = "\n Merci de votre attention !"
    p3.font.size = Pt(15)
    p3.font.color.rgb = RGBColor(226, 232, 240)

    # Sauvegarde sécurisée
    output_filename = "KAYA_Boreal_Presentation.pptx"
    try:
        prs.save(output_filename)
        print(f"[SUCCÈS] Présentation générée : {output_filename}")
    except PermissionError:
        output_filename = "KAYA_Boreal_Presentation_v2.pptx"
        prs.save(output_filename)
        print(f"[AVERTISSEMENT] Fichier verrouillé. Sauvegardé sous : {output_filename}")

if __name__ == "__main__":
    create_complete_presentation()