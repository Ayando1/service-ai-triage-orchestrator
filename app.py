import os
import json
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

st.set_page_config(
    page_title="AI Service Triage & Retention Orchestrator",
    page_icon="⚡",
    layout="wide"
)

# --- Stílus ---
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border-left: 5px solid #2b5c8f;
        padding: 12px;
        border-radius: 6px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚡ Enterprise Service Triage & Retention Orchestrator")
st.caption("AI-vezérelt incidenskezelési, hibajegy-routing és churn-megelőzési mikroszolgáltatás prototípus")

# --- Oldalsáv ---
with st.sidebar:
    st.header("⚙️ Rendszerbeállítások")
    api_key = st.text_input("Gemini API Kulcs (opcionális)", type="password")
    if not api_key:
        api_key = os.environ.get("GEMINI_API_KEY", "")
        
    st.markdown("---")
    st.markdown("**Journey Fókuszpontok:**")
    st.markdown("- **Business-to-AI:** Természetes nyelv -> Strukturált üzleti entitások + LTV retention ajánlás")
    st.markdown("- **E2E Business-to-IT:** CRM integrációs séma, SLA prioritás, hibajegy audit log")

    st.markdown("---")
    st.subheader("Gyors tesztadatok")
    samples = {
        "1. Kritikus hálózati hiba & Churn": (
            "Három napja nincs optikai netem a 11. kerületben, a bridge módú router folyamatosan pirosan villog. "
            "Home office-ban dolgozom, nem tudok belépni a céges VPN-be! Ha a mai napon nem küldtök technikust, azonnal átmegyek "
            "a konkurenciához és viszem az 5 előfizetéses vállalati flottánkat is a jogi osztállyal!"
        ),
        "2. Számlázási anomália (e-Pack / Roaming)": (
            "Üdv! A legutóbbi számlámon megjelent 14 500 Ft roaming adatforgalmi díj, miközben az EU-n belül voltam Ausztriában, "
            "ahol a csomagom szerint díjmentes a roaming. Kérem a tétel sztornózását és a jóváírást a következő havi egyenlegemen."
        ),
        "3. Hardver / TV-Box konfiguráció": (
            "Sziasztok! Megérkezett az új 4K médiabox, de a stream adásoknál szaggat a kép és 20 perc után leáll a hang. "
            "Már újraindítottam kétszer, van valami szoftverfrissítési lépés, amit meg kell csinálni?"
        )
    }
    selected_sample = st.selectbox("Válassz teszt esetet:", ["Kézi bevitel"] + list(samples.keys()))

input_text = ""
if selected_sample != "Kézi bevitel":
    input_text = samples[selected_sample]

# --- Adatmodell és Fallback Feldolgozó Logika ---
def mock_enterprise_analysis(text: str) -> dict:
    text_lower = text.lower()
    
    category = "Általános ügyfélszolgálat"
    tech_stack = "N/A"
    priority = "P3 - Standard (48h)"
    churn_risk = "Alacsony"
    sla_hours = 48
    retention_action = "Standard ügyfélszolgálati tájékoztatás"

    if any(k in text_lower for k in ["optika", "router", "vpn", "netem", "internet", "box", "tv"]):
        category = "Műszaki & Hálózati Incidens"
        tech_stack = "Vezetékes Hálózat / HGW / IPTV"
        priority = "P2 - Magas (12h)"
        sla_hours = 12

    if any(k in text_lower for k in ["számla", "díj", "roaming", "jóváírás", "forint", "ft"]):
        category = "Pénzügy & Számlázási Reklamáció"
        tech_stack = "BSS / Billing Core"
        priority = "P3 - Standard (24h)"
        sla_hours = 24

    if any(k in text_lower for k in ["átmegyek", "konkurenci", "felmond", "flotta", "jog"]):
        churn_risk = "Kritikus (92%)"
        priority = "P1 - Vészhelyzet (2h)"
        sla_hours = 2
        retention_action = "Kiemelt ügyfélmegtartási menedzser bevonása + hűségkedvezmény jóváírás azonnal"
    elif "számla" in text_lower:
        churn_risk = "Közepes (45%)"
        retention_action = "Számla zárolása a vizsgálat idejére, díjmentes egyenleg-kompenzáció"

    deadline = (datetime.now() + timedelta(hours=sla_hours)).strftime("%Y-%m-%d %H:%M")

    return {
        "ticket_metadata": {
            "ticket_id": f"SRV-{hash(text) % 1000000:06d}",
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "target_tech_domain": tech_stack,
            "priority": priority,
            "sla_deadline": deadline,
            "sentiment": "Erősen Frusztrált" if "!" in text or "azonnal" in text_lower else "Semleges/Érdeklődő"
        },
        "business_intelligence": {
            "churn_probability": churn_risk,
            "customer_ltv_impact": "Magas értékű B2B/B2C ügyfél",
            "recommended_retention_strategy": retention_action
        },
        "it_routing": {
            "assigned_queue": "Tier-2 Incident Response" if "P1" in priority else "Billing & Front-Office",
            "auto_trigger_technician": True if ("optika" in text_lower or "netem" in text_lower) and "P1" in priority else False
        },
        "agent_response_draft": (
            "Tisztelt Előfizetőnk!\n\n"
            f"Kiemelt prioritással rögzítettük bejelentését rendszerünkben. Megállapítottuk, hogy az ügy {category.lower()} jellegű fennakadást érint. "
            f"Mivel szolgáltatásunk stabilitása és az Ön elégedettsége elsődleges célunk, incidensmenedzsmentünk {deadline}-ig garantálja az ügy kivizsgálását és kezelését. "
            f"Ügyfélszámláján a folyamat lezárásáig automatikusan intézkedünk az egyeztetett jóváírásokról.\n\n"
            "Üdvözlettel:\nKiemelt Ügyféltámogatási Osztály"
        )
    }

def analyze_with_llm(text: str, key: str) -> dict:
    from google import genai
    client = genai.Client(api_key=key)
    
    system_instruction = (
        "Telekommunikációs és felhőszolgáltatási E2E Business-to-IT rendszerelemző vagy. "
        "A beérkező ügyfélpanaszt elemezd és kötelezően tiszta JSON formátumban válaszolj, Markdown jelölések nélkül! "
        "A JSON struktúra mezői:\n"
        "{\n"
        '  "ticket_metadata": {"ticket_id": str, "timestamp": str, "category": str, "target_tech_domain": str, "priority": str, "sla_deadline": str, "sentiment": str},\n'
        '  "business_intelligence": {"churn_probability": str, "customer_ltv_impact": str, "recommended_retention_strategy": str},\n'
        '  "it_routing": {"assigned_queue": str, "auto_trigger_technician": bool},\n'
        '  "agent_response_draft": str\n'
        "}"
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"Elemezd ezt az előfizetői hibajegyet:\n{text}",
        config={"system_instruction": system_instruction}
    )
    
    clean_text = response.text.replace("```json", "").replace("```", "").strip()
    return json.loads(clean_text)

# --- Felhasználói Felület ---
col_in, col_action = st.columns([3, 1])
with col_in:
    user_ticket = st.text_area("Beérkező ügyfélmegkeresés / Ticket Payload:", value=input_text, height=180)
with col_action:
    st.write("### Munkafolyamat")
    st.write("1. NLP & Szemantikai elemzés")
    st.write("2. SLA & Prioritási mátrix")
    st.write("3. Churn predikció & Retention")
    process_btn = st.button("⚡ E2E Pipeline Indítása", type="primary", use_container_width=True)

if process_btn:
    if not user_ticket.strip():
        st.warning("Kérlek, adj meg egy feldolgozandó szöveget!")
    else:
        with st.spinner("Pipeline futtatása: Döntési logika és IT routing folyamatban..."):
            try:
                if api_key:
                    result = analyze_with_llm(user_ticket, api_key)
                else:
                    result = mock_enterprise_analysis(user_ticket)
            except Exception as e:
                st.warning(f"Külső API hiba történt ({e}), lokális szabályalapú fallback aktiválva.")
                result = mock_enterprise_analysis(user_ticket)

            st.success("✅ E2E Feldolgozás befejezve: CRM és Ticketing entitások sikeresen generálva.")

            tab_overview, tab_bi, tab_it, tab_json = st.tabs([
                "📋 Üzleti Összefoglaló (Operations)", 
                "💡 Üzleti Intelligencia & Churn", 
                "⚙️ IT Routing & Backend Dispatch", 
                "💾 Strukturált JSON Payload (CRM)"
            ])

            meta = result.get("ticket_metadata", {})
            bi = result.get("business_intelligence", {})
            routing = result.get("it_routing", {})

            with tab_overview:
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Ticket ID", meta.get("ticket_id", "N/A"))
                c2.metric("Prioritási Szint", meta.get("priority", "N/A"))
                c3.metric("SLA Határidő", meta.get("sla_deadline", "N/A"))
                c4.metric("Hangvétel", meta.get("sentiment", "N/A"))

                st.markdown("#### Ügyfélszolgálati Választervezet (Human-in-the-Loop)")
                st.text_area(
                    "Operátor által ellenőrizhető és jóváhagyható válasz:",
                    value=result.get("agent_response_draft", ""),
                    height=160
                )

            with tab_bi:
                b1, b2 = st.columns(2)
                with b1:
                    st.metric("Lemorzsolódási Kockázat (Churn Risk)", bi.get("churn_probability", "N/A"))
                    st.write(f"**Ügyfélérték hatás:** {bi.get('customer_ltv_impact', 'N/A')}")
                with b2:
                    st.markdown("**Javasolt Megtartási Stratégia:**")
                    st.info(bi.get("recommended_retention_strategy", "N/A"))

            with tab_it:
                i1, i2 = st.columns(2)
                i1.metric("Kijelölt IT / Support Queue", routing.get("assigned_queue", "N/A"))
                i2.metric("Érintett Rendszer / Réteg", meta.get("target_tech_domain", "N/A"))
                if routing.get("auto_trigger_technician"):
                    st.error("⚠️ Automata technikus-kiszállási igény generálva a terepi karbantartó alrendszer felé!")
                else:
                    st.info("ℹ️ Távdiagnosztika és központi hibajegy-kezelés elindítva.")

            with tab_json:
                st.caption("REST API-n keresztül továbbítható JSON entitás (ServiceNow / Jira / Salesforce integrációhoz):")
                st.json(result)