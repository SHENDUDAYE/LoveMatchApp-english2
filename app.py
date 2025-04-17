import streamlit as st
import random
from datetime import date, datetime, timedelta

# ------------------------ DATA CONFIGURATION ------------------------

zodiacs = ["Rat", "Ox", "Tiger", "Rabbit", "Dragon", "Snake",
           "Horse", "Goat", "Monkey", "Rooster", "Dog", "Pig"]
tiangans = ["Jia", "Yi", "Bing", "Ding", "Wu", "Ji", "Geng", "Xin", "Ren", "Gui"]
dizhis  = ["Zi", "Chou", "Yin", "Mao", "Chen", "Si",
           "Wu", "Wei", "Shen", "You", "Xu", "Hai"]

# NaYin (simplified): (Ganzhi_pair) -> (NaYin_name, element)
nayin_map = {
    ("JiaZi", "YiChou"): ("Gold in Sea", "Metal"),
    ("BingYin", "DingMao"): ("Fire in Furnace", "Fire"),
    # ... fill in the rest of the 60 JiaZi pairs ...
}

# Zodiac relationships
rel_config = {
    "Six Harmony":   [("Rat","Ox"), ("Tiger","Pig"), ("Rabbit","Dog"),
                      ("Dragon","Rooster"), ("Snake","Monkey"), ("Horse","Goat")],
    "Six Clash":     [("Rat","Horse"), ("Ox","Goat"), ("Tiger","Monkey"),
                      ("Rabbit","Rooster"), ("Dragon","Dog"), ("Snake","Pig")],
    "Six Harm":      [("Rat","Goat"), ("Ox","Horse"), ("Tiger","Snake"),
                      ("Rabbit","Dragon"), ("Dog","Rooster"), ("Monkey","Pig")],
    "Three Harmony": [["Monkey","Rat","Dragon"],
                      ["Tiger","Horse","Dog"],
                      ["Snake","Rooster","Ox"],
                      ["Pig","Rabbit","Goat"]],
}

# ------------------------ CORE FUNCTIONS ------------------------

def get_zodiac(year: int) -> str:
    """Return Zodiac sign by year (ignoring Chinese solar terms)"""
    return zodiacs[(year - 4) % 12]

def get_ganzhi(year: int) -> str:
    """Return Year Pillar (Heavenly Stem + Earthly Branch)"""
    g = tiangans[(year - 4) % 10]
    d = dizhis[(year - 4) % 12]
    return g + d

def get_nayin(ganzhi: str) -> tuple[str,str]:
    """Return NaYin name and element by matching ganzhi"""
    for keys, val in nayin_map.items():
        if ganzhi in keys:
            return val
    return ("Unknown NaYin", "Unknown")

def analyze_zodiac(a: str, b: str) -> list[str]:
    """Return list of Zodiac relations between two signs"""
    relations = []
    for rel, pairs in rel_config.items():
        if rel == "Three Harmony":
            if any(a in group and b in group for group in pairs):
                relations.append(rel)
        else:
            if (a,b) in pairs or (b,a) in pairs:
                relations.append(rel)
    return relations or ["Ordinary"]

def wuxing_relation(e1: str, e2: str) -> tuple[str,str]:
    """Return five‑element relation and arrow text"""
    flow = {
        "Wood":   {"generates":"Fire", "overcomes":"Earth"},
        "Fire":   {"generates":"Earth","overcomes":"Metal"},
        "Earth":  {"generates":"Metal","overcomes":"Water"},
        "Metal":  {"generates":"Water","overcomes":"Wood"},
        "Water":  {"generates":"Wood","overcomes":"Fire"},
    }
    if e2 == flow.get(e1,{}).get("generates"):
        return ("Generates","{}→{}".format(e1, e2))
    if e2 == flow.get(e1,{}).get("overcomes"):
        return ("Overcomes","{}→{}".format(e1, e2))
    if e1 == flow.get(e2,{}).get("generates"):
        return ("Generates","{}→{}".format(e2, e1))
    if e1 == flow.get(e2,{}).get("overcomes"):
        return ("Overcomes","{}→{}".format(e2, e1))
    return ("Balances","")

def calculate_score(z_rels: list[str], wx_rel: tuple[str,str], nayin_match: bool) -> int:
    """Composite compatibility score out of 100"""
    score = 60
    score += len(z_rels) * 10
    if "Six Harmony" in z_rels: score += 15
    if "Three Harmony" in z_rels: score += 10
    if wx_rel[0] == "Generates": score += 20
    if wx_rel[0] == "Overcomes": score -= 15
    if nayin_match: score += 10
    return max(0, min(score, 100))

def recommend_date(z: str) -> str:
    """Recommend wedding years based on Three‑Harmony mapping"""
    mapping = {
        "Rat":  [2024,2028,2032], "Monkey":[2024,2028,2032], "Dragon":[2024,2028,2032],
        "Tiger":[2026,2030,2034], "Dog":[2026,2030,2034], "Horse":[2026,2030,2034],
        "Snake":[2025,2029,2033], "Rooster":[2025,2029,2033], "Ox":[2025,2029,2033],
        "Rabbit":[2027,2031,2035], "Goat":[2027,2031,2035], "Pig":[2027,2031,2035],
    }
    years = mapping.get(z, [])
    return f"{years[0]} – {years[-1]}" if years else "Any"

def child_prediction(wx_rel: tuple[str,str]) -> str:
    """Child fortune advice based on five‑element relation"""
    if wx_rel[0] == "Generates":
        return "Favorable child fortune — elements flow smoothly."
    if wx_rel[0] == "Overcomes":
        return "Exercise care in child health; suggest prenatal balance."
    return "Balanced child fortune; upbringing is key."

# ------------------------ STREAMLIT APP ------------------------

def main():
    st.set_page_config(page_title="Love Match Compatibility Analyzer", layout="wide")
    st.title("💘 Love Match Compatibility Analyzer")
    st.write("Enter both partners’ birth dates to get a full compatibility report.")

    with st.form("compatibility_form"):
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Partner A")
            date_a = st.date_input("Birth date", value=date(1990,1,1))
        with col2:
            st.subheader("Partner B")
            date_b = st.date_input("Birth date", value=date(1992,1,1))
        submitted = st.form_submit_button("Analyze Compatibility")

    if submitted:
        # Prepare data for each partner
        def partner_data(dt: date):
            y = dt.year
            gz = get_ganzhi(y)
            ny_name, ny_elem = get_nayin(gz)
            return {
                "birth": dt,
                "zodiac": get_zodiac(y),
                "ganzhi": gz,
                "nayin": (ny_name, ny_elem),
                "element": ny_elem
            }

        A = partner_data(date_a)
        B = partner_data(date_b)

        # Zodiac relation
        z_rels = analyze_zodiac(A["zodiac"], B["zodiac"])
        # Five‑element relation
        wx_rel = wuxing_relation(A["element"], B["element"])
        # NaYin match?
        nayin_match = A["nayin"][0][-1] == B["nayin"][0][-1]
        # Score
        score = calculate_score(z_rels, wx_rel, nayin_match)

        # Display results
        st.markdown("### 🔍 Basic Info")
        st.write(f"- Partner A: {A['birth']} → {A['zodiac']}, Pillar: {A['ganzhi']}, NaYin: {A['nayin'][0]} ({A['nayin'][1]})")
        st.write(f"- Partner B: {B['birth']} → {B['zodiac']}, Pillar: {B['ganzhi']}, NaYin: {B['nayin'][0]} ({B['nayin'][1]})")

        st.markdown("### 🐲 Zodiac Relations")
        st.write(", ".join(z_rels))

        st.markdown("### 🌳 Five‑Element Relations")
        st.write(f"{wx_rel[0]}   {wx_rel[1]}")

        st.markdown("### 💯 Compatibility Score")
        st.write(f"{score}/100")
        st.progress(score / 100)

        st.markdown("### 📅 Wedding Year Recommendation")
        st.write(recommend_date(A["zodiac"]))

        st.markdown("### 👶 Child Forecast")
        st.write(child_prediction(wx_rel))

if __name__ == "__main__":
    main()
