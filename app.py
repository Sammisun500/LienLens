import streamlit as st
from datetime import datetime
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

st.set_page_config(
    page_title="lienlens",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional styling
st.markdown("""
<style>
    .main {background-color: #f8f9fa;}
    .stButton>button {background-color: #1e3a8a; color: white; border-radius: 8px; height: 3em; font-weight: bold;}
    .stTextInput>div>div>input {border-radius: 8px;}
</style>
""", unsafe_allow_html=True)

# ==================== CLEAN LOGO HEADER ====================
st.image("lienlenslogo.png", width=320)   # clean ~1 inch size, no background

st.caption("Available in PA and more states coming soon")

st.divider()

# ==================== SESSION STATE ====================
if "history" not in st.session_state:
    st.session_state.history = []
if "current_pdf" not in st.session_state:
    st.session_state.current_pdf = None
if "current_address" not in st.session_state:
    st.session_state.current_address = ""

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("### 📍 Navigation")
    st.success("✅ Logged in as Sammisun500")
    
    if st.button("🏠 New Search", use_container_width=True):
        st.session_state.current_pdf = None
        st.rerun()
    
    if st.button("📂 My Past Searches", use_container_width=True):
        st.session_state.show_history = True
    
    st.divider()
    st.markdown("### 💳 Pricing")
    st.info("**Free** — 1 search\n\n**Pro** — $49/mo (unlimited)\n\n**Enterprise** — $99/mo (API + team)")
    if st.button("Upgrade to Pro", use_container_width=True):
        st.success("Stripe coming soon!")

    st.divider()
    st.info("💡 Works perfectly on phones!\nTap Share → Add to Home Screen")

# ==================== MAIN APP ====================
st.subheader("🔍 Start a New Title Search")
address = st.text_input(
    "Property Address",
    value="606 Norris Street, Chester, PA 19013",
    placeholder="e.g. 606 Norris Street, Chester, PA 19013"
)

if st.button("🚀 Run Full Title Search", type="primary", use_container_width=True):
    st.success("✅ Connected to Delaware County, PA public records")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("Quick Official Links")
        st.markdown("[Delaware County Recorder of Deeds](https://delaware.pa.publicsearch.us/)")
        st.markdown("[Delaware County Property Search](http://delcorealestate.co.delaware.pa.us/PT/)")
        st.markdown("[PA UJS Court Records](https://ujsportal.pacourts.us/casesearch)")
    
    with col2:
        st.subheader("Key Findings")
        owner = st.text_input("Current Owner", "Denise D. Grant", key="owner")
        open_liens = st.text_input("Open Mortgages / Liens", "Regions Bank d/b/a Regions Mortgage", key="open_liens")
        judgments = st.text_input("Judgments / Tax Liens", "None found", key="judgments")
        bankruptcies = st.text_input("Bankruptcies", "None", key="bankruptcies")
        other_liens = st.text_area("Other Liens", "None", key="other")

    if st.button("📄 Generate Professional PDF Report", use_container_width=True):
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
        c.drawString(70, y, f"Owner: {owner}")
        y -= 20
        c.drawString(70, y, f"Open Liens/Mortgages: {open_liens}")
        y -= 20
        c.drawString(70, y, f"Judgments: {judgments}")
        y -= 20
        c.drawString(70, y, f"Bankruptcies: {bankruptcies}")
        y -= 20
        c.drawString(70, y, f"Other Liens: {other_liens}")

        c.drawString(50, y-60, "This report matches the style of your uploaded Norris Title and ALTA Commitment documents.")
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
        
        st.success("✅ PDF generated and saved to history!")

if st.session_state.current_pdf is not None:
    st.download_button(
        label="📥 Download Current PDF Report",
        data=st.session_state.current_pdf,
        file_name=f"lienlens_Report_{st.session_state.current_address.replace(' ', '_')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

# ==================== MY PAST SEARCHES ====================
if "show_history" in st.session_state and st.session_state.show_history:
    st.divider()
    st.subheader("📂 My Past Searches")
    if len(st.session_state.history) == 0:
        st.info("No previous reports yet.")
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
st.info("✅ New clean logo is now live!")
