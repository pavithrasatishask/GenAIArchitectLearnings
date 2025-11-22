# app/streamlit_app.py
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
from rag.pipeline import answer_question
from kg.neo4j_client import query_graph_for_topic
from pyvis.network import Network
import tempfile

st.set_page_config(page_title="Tamil Grade 8 RAG Agent", layout="wide")

# CSS & styling for gradient, badges, dark/light (reuse from earlier design)
st.markdown("""
<style>
.main-title { font-size:34px; font-weight:800; background: linear-gradient(90deg,#2ecc71,#27ae60); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.card { background: white; padding: 14px; border-radius:10px; box-shadow: 0 4px 20px rgba(0,0,0,0.06); }
.user-msg { background:#eafaf0; padding:10px; border-radius:10px; }
.bot-msg { background:#fff; padding:10px; border-radius:10px; border:1px solid rgba(39,174,96,0.06); }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>📚 Tamil Grade 8 — RAG Assistant</h1>", unsafe_allow_html=True)
st.write("Ask anything from the 8th-standard Tamil book. OCR + vector search + KG powered answers (with citations).")

tab1, tab2, tab3 = st.tabs(["Chat", "Quick Search", "Knowledge Graph"])

# Chat tab
with tab1:
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    st.subheader("Chat")
    for msg in st.session_state.chat_history:
        role, text, ts, sources = msg
        if role == "user":
            st.markdown(f"<div class='user-msg'><strong>You</strong> • {ts}<div>{text}</div></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='bot-msg'><strong>Agent</strong> • {ts}<div>{text}</div></div>", unsafe_allow_html=True)
            if sources:
                st.write("**Sources:**")
                for s in sources:
                    st.write(f"- {s}")

    col1, col2 = st.columns([4,1])
    with col1:
        user_input = st.text_area("Enter your question in Tamil (or English)", key="chat_input", height=140)
    with col2:
        if st.button("Send"):
            if not user_input.strip():
                st.warning("Type a question first.")
            else:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.chat_history.append(("user", user_input, now, None))
                with st.spinner("Retrieving and generating answer..."):
                    try:
                        out = answer_question(user_input, top_k=5)
                        ans = out.get("answer")
                        sources = out.get("sources")
                    except Exception as e:
                        ans = f"Error: {e}"
                        sources = []
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.chat_history.append(("agent", ans, now, sources))
                st.experimental_rerun()

# Quick Search tab: show top k pages for a query
with tab2:
    st.subheader("Quick search pages")
    q = st.text_input("Search term (short phrase):", key="quick_search")
    if st.button("Search pages"):
        if not q.strip():
            st.warning("Enter a phrase.")
        else:
            from rag.retriever import retrieve
            with st.spinner("Searching..."):
                hits = retrieve(q, top_k=8)
            st.write("Top results:")
            for h in hits:
                st.markdown(f"**Page {h['page']}** — {h['content'][:300]}...")
                st.write(f"Source: {h['source']}")
                st.markdown("---")

# Knowledge Graph tab
with tab3:
    st.subheader("Knowledge Graph Visualizer")
    topic = st.text_input("Enter topic/chapter to visualize", key="kg_topic")
    if st.button("Visualize KG"):
        if not topic.strip():
            st.warning("Please enter a topic.")
        else:
            with st.spinner("Querying Neo4j..."):
                graph = query_graph_for_topic(topic, limit=200)
                if not graph["nodes"]:
                    st.info("No nodes found.")
                else:
                    net = Network(height="650px", width="100%", bgcolor="#ffffff", font_color="#222222")
                    net.barnes_hut()
                    color_map = {"Topic": "#2ecc71", "Page": "#2980b9", "Image": "#f39c12", "Node": "#95a5a6"}
                    for n in graph["nodes"]:
                        ntype = n.get("type", "Node")
                        color = color_map.get(ntype, "#95a5a6")
                        title = "<br>".join([f"<b>{k}</b>: {v}" for k, v in (n.get("props") or {}).items()])
                        net.add_node(n["id"], label=str(n["label"]), title=title, color=color)
                    for e in graph["edges"]:
                        net.add_edge(e["source"], e["target"], title=e.get("type", "rel"))
                    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
                    net.write_html(tmp.name)
                    html = open(tmp.name, "r", encoding="utf-8").read()
                    components.html(html, height=700, scrolling=True)
