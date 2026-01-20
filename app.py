import streamlit as st
import requests
import pandas as pd
import json

st.set_page_config(page_title="The 12th Man", page_icon="🏏", layout="wide", initial_sidebar_state="expanded")

API_URL = "[http://127.0.0.1:8000/api/calculate](http://127.0.0.1:8000/api/calculate)"

st.markdown("""
    <style>
        @import url('[https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap](https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap)');
        html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
        .block-container { padding-top: 1rem !important; }
        .main-header {
            background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
            padding: 2rem; border-radius: 15px; color: white; text-align: center; margin-bottom: 2rem;
        }
        .winner-card {
            background: linear-gradient(135deg, #FFD700 0%, #FF8C00 100%);
            color: black; padding: 20px; border-radius: 15px; text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.image("[https://cdn-icons-png.flaticon.com/512/1055/1055670.png](https://cdn-icons-png.flaticon.com/512/1055/1055670.png)", width=80)
    st.markdown("### ⚙️ Match Setup")
    match_url = st.text_input("🔗 Scorecard URL")
    commentary_url = st.text_input("🔗 Commentary URL")
    uploaded_files = st.file_uploader("📸 Screenshots", type=["jpg", "png"], accept_multiple_files=True)

st.markdown('<div class="main-header"><h1>🏏 The 12th Man</h1><p>Powered by Google Vertex AI (Gemini + Gemma)</p></div>', unsafe_allow_html=True)

if st.button("🚀 Calculate Results", type="primary"):
    if not match_url or not commentary_url or not uploaded_files:
        st.warning("⚠️ Missing Inputs.")
    else:
        try:
            with st.status("📡 Connecting to Google Cloud API...", expanded=True) as status:
                files_payload = [("files", (f.name, f.getvalue(), f.type)) for f in uploaded_files]
                payload = {"match_url": match_url, "commentary_url": commentary_url}
                
                response = requests.post(API_URL, data=payload, files=files_payload)
                response.raise_for_status()
                data = response.json().get("data", {})
                status.update(label="✅ Success!", state="complete", expanded=True)

                # --- RESULTS ---
                st.divider()
                winner = data.get("winner", "Unknown")
                score = data.get("winner_score", 0)
                pot = data.get("total_pot", 0.0)
                sarcasm = data.get("sarcastic_summary", "")

                c1, c2, c3 = st.columns([1, 2, 1])
                with c1: st.metric("💰 Total Pot", f"£{pot:.2f}")
                with c2: 
                    st.markdown(f"""
                    <div class="winner-card">
                        <h3>🏆 WINNER</h3>
                        <h1 style="margin:0; font-size: 3rem;">{winner}</h1>
                        <p style="margin:0; font-size: 1.2rem;">{score} Runs</p>
                        <hr style="border-top:1px solid rgba(0,0,0,0.2);">
                        <p style="font-style: italic;">"{sarcasm}"</p>
                    </div>""", unsafe_allow_html=True)
                with c3: st.metric("➗ Formula", "Diff / 5")

                # --- INSIGHTS ---
                st.divider()
                ca, cb = st.columns(2)
                with ca: st.info(f"**📈 Analyst:**\n\n{data.get('analysis')}")
                with cb: 
                    fc = data.get("forecast", {})
                    st.success(f"**🔥 Hot Pick:** {fc.get('hot_pick')} ({fc.get('reason')})")

                # --- TABLE ---
                st.markdown("### 📊 Breakdown")
                mappings = data.get("player_mappings", {})
                scores = data.get("detailed_scores", {})
                rows = []
                for p, codes in mappings.items():
                    r = {"Player": p}
                    tot = 0
                    for i, c in enumerate(codes, 1):
                        val = scores.get(c, 0)
                        r[f"Code {i}"] = f"{c} ({val})"
                        tot += val
                    r["Total Runs"] = tot
                    rows.append(r)
                
                if rows:
                    df = pd.DataFrame(rows)
                    cols = ["Player", "Total Runs"] + [c for c in df.columns if c.startswith("Code")]
                    existing = [c for c in cols if c in df.columns]
                    def highlight(s): return ['background-color: #d4edda' if v == winner else '' for v in s]
                    st.dataframe(df[existing].style.apply(highlight, subset=['Player']), use_container_width=True, hide_index=True)

                # --- PAYMENTS ---
                settlements = data.get("settlements", {})
                if settlements:
                    st.markdown("### 💸 Payments")
                    df_pay = pd.DataFrame(list(settlements.items()), columns=["Player", "Amount Due"])
                    df_pay["Amount Due"] = df_pay["Amount Due"].map("£{:.2f}".format)
                    col_pay, _ = st.columns([1, 1])
                    with col_pay: st.dataframe(df_pay, use_container_width=True, hide_index=True)

        except Exception as e:
            st.error(f"Error: {e}")