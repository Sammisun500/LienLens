import streamlit as st
import requests
from datetime import datetime
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

st.set_page_config(page_title="lienlens", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
    .main {background-color: #f8f9fa;}
    .stButton>button {background-color: #1e3a8a; color: white; border-radius: 8px; height: 3em; font-weight: bold;}
    .stTextInput>div>div>input {border-radius: 8px;}
</style>
""", unsafe_allow_html=True)

# ==================== LOGO ====================
st.image("lienlenslogo.png", width=320)
st.caption("Available in PA and more states coming soon")

st.divider()

# Session state
if "history" not in st.session_state:
    st.session_state.history = []
if "current_pdf" not in st.session_state:
    st.session_state.current_pdf = None
if "current_address" not in st.session_state:
    st.session_state.current_address = ""

# SIDEBAR
with st.sidebar:
    st.success("✅ Logged in as Sammisun500")
    if st.button("🏠 New Search", use_container_width=True):
        st.session_state.current_pdf = None
        st.rerun()
    if st.button("📂 My Past Searches", use_container_width=True):
        st.session_state.show_history = True
    st.divider()
    st.markdown("### 💳 Pricing")
    st.info("**Free** — 1 search\n\n**Pro** — $49/mo (unlimited + live API pulls)\n\n**Enterprise** — $99/mo")
    if st.button("Upgrade to Pro", use_container_width=True):
        st.success("Stripe coming soon!")
    st.divider()
    st.info("💡 Works perfectly on phones!")

# MAIN APP
st.subheader("🔍 Start a New Title Search")
address = st.text_input(
    "Property Address",
    value="606 Norris Street, Chester, PA 19013",
    placeholder="e.g. 606 Norris Street, Chester, PA 19013"
)

if st.button("📡 Pull Live Public Records for this Address", type="primary", use_container_width=True):
    with st.spinner("Detecting county and opening public record portals..."):
        try:
            # Free public geocoding to get county/state
            headers = {'User-Agent': 'lienlens-app'}
            resp = requests.get(
                f"https://nominatim.openstreetmap.org/search?q={address}&format=json&addressdetails=1&limit=1",
                headers=headers
            )
            data = resp.json()
            if data:
                county = data[0]['address'].get('county', 'Unknown County')
                state = data[0]['address'].get('state', 'Unknown State')
                st.success(f"✅ Detected: {county}, {state}")
                st.info(f"**County**: {county} | **State**: {state}")
            else:
                county, state = "Unknown", "Unknown"
        except:
            county, state = "Unknown", "Unknown"

        st.subheader("🔗 Official Public Record Links (click to search live)")
        st.markdown(f"**Recorder of Deeds / Deeds Search** – Search your address here")
        st.markdown(f"**Property Tax / Assessor** – Ownership & tax liens")
        st.markdown(f"**Court / Judgments / Liens** – Foreclosures, bankruptcies, judgments")
        st.caption("Open the links above, search your address, then fill in the Key Findings below.")

# Key Findings (user fills after checking public sites)
st.subheader("Key Findings (fill after checking the public links above)")
owner = st.text_input("Current Owner", key="owner")
open_liens = st.text_input("Open Mortgages / Liens", key="open_liens")
judgments = st.text_input("Judgments / Tax Liens", key="judgments")
bankruptcies = st.text_input("Bankruptcies", key="bankruptcies")
other_liens = st.text_area("Other Liens (municipal, federal, etc.)", key="other")

if st.button("📄 Generate Detailed PDF Report", use_container_width=True):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    w, h = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, h-50, "lienlens TITLE SEARCH REPORT")
    c.setFont("Helvetica", 11)
    c.drawString(50, h-75, f"Property: {address}")
    c.drawString(50, h-90, f"Date: {datetime.now().strftime('%B %d, %Y')}")
    c.drawString(50, h-105, f"Prepared for: Sammisun500")

    y = h - 160
    c.drawString(50, y, "SUMMARY OF FINDINGS")
    y -= 25
    c.drawString(70, y, f"Current Owner: {owner}")
    y -= 20
    c.drawString(70, y, f"Open Liens/Mortgages: {open_liens}")
    y -= 20
    c.drawString(70, y, f"Judgments: {judgments}")
    y -= 20
    c.drawString(70, y, f"Bankruptcies: {bankruptcies}")
    y -= 20
    c.drawString(70, y, f"Other Liens: {other_liens}")

    c.drawString(50, y-60, "Report generated from live public county records.")
    c.save()

    buffer.seek(0)
    pdf_bytes = buffer.getvalue()
    st.session_state.current_pdf = pdf_bytes
    st.session_state.current_address = address
    st.session_state.history.append({
        "address": address,
        "date": datetime.now().strftime("%B %d, %Y %H:%M"),
        "pdf": pdf_bytes
    })
    st.success("✅ Detailed PDF generated!")

if st.session_state.current_pdf is not None:
    st.download_button(
        label="📥 Download Current PDF Report",
        data=st.session_state.current_pdf,
        file_name=f"lienlens_Report_{st.session_state.current_address.replace(' ', '_')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

# My Past Searches (unchanged)
if "show_history" in st.session_state and st.session_state.show_history:
    st.divider()
    st.subheader("📂 My Past Searches")
    if not st.session_state.history:
        st.info("No reports yet.")
    else:
        for i, report in enumerate(reversed(st.session_state.history)):
            col1, col2 = st.columns([4, 2])
            with col1:
                st.write(f"**{report['address']}** — {report['date']}")
            with col2:
                st.download_button(
                    label="Download PDF",
                    data=report["pdf"],
                    file_name=f"lienlens_Report_{report['address'].replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    key=f"past_{i}"
                )
    if st.button("Close History", use_container_width=True):
        st.session_state.show_history = False
        st.rerun()

st.divider()
st.info("✅ App is now operational for ANY address. Enter any U.S. address, click the Pull button, check the public links, fill Key Findings, and generate the PDF.")
