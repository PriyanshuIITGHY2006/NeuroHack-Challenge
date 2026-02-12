import streamlit as st
import requests
import json
from datetime import datetime
import time
import plotly.graph_objects as go
import plotly.express as px
from collections import defaultdict
import pandas as pd

# Page Configuration
st.set_page_config(
    layout="wide", 
    page_title="MemoryOS - Long-Form AI Memory System",
    page_icon="🧠",
    initial_sidebar_state="expanded"
)

# Enhanced CSS with Claude/Gemini-like styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .main {
        background: #0f0f23;
        padding: 0;
    }
    
    .main::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: radial-gradient(circle at 20% 50%, rgba(120, 119, 198, 0.15), transparent 50%),
                    radial-gradient(circle at 80% 80%, rgba(118, 75, 162, 0.15), transparent 50%);
        pointer-events: none;
        z-index: 0;
    }
    
    .stChatFloatingInputContainer {
        background: rgba(30, 30, 60, 0.4);
        backdrop-filter: blur(20px);
        border-radius: 16px;
        padding: 16px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .stChatMessage {
        background: linear-gradient(135deg, rgba(30, 30, 60, 0.8), rgba(40, 40, 80, 0.6));
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 24px;
        margin: 16px 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.1);
        animation: slideIn 0.4s ease-out;
        color: #e0e0e0;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.5;
        }
    }
    
    .typing-indicator {
        animation: pulse 1.5s ease-in-out infinite;
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    [data-testid="stSidebar"] * {
        color: #e0e0e0 !important;
    }
    
    h1 {
        background: linear-gradient(135deg, #7877c6 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800;
        font-size: 2.8rem;
        margin-bottom: 0.5rem;
    }
    
    h2, h3, h4 {
        color: #b8b8d4;
    }
    
    p {
        color: #e0e0e0;
    }
    
    .stChatInputContainer textarea {
        background: rgba(30, 30, 60, 0.6) !important;
        backdrop-filter: blur(10px);
        border-radius: 16px !important;
        border: 2px solid rgba(120, 119, 198, 0.3) !important;
        padding: 14px !important;
        color: #e0e0e0 !important;
        transition: all 0.3s ease;
    }
    
    .stChatInputContainer textarea:focus {
        border-color: rgba(120, 119, 198, 0.8) !important;
        box-shadow: 0 0 20px rgba(120, 119, 198, 0.3) !important;
    }
    
    .stButton button {
        background: linear-gradient(135deg, #7877c6 0%, #764ba2 100%);
        color: white;
        border-radius: 12px;
        border: none;
        padding: 12px 28px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(120, 119, 198, 0.3);
    }
    
    .stButton button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(120, 119, 198, 0.5);
        background: linear-gradient(135deg, #8887d7 0%, #8765b2 100%);
    }
    
    [data-testid="stMetricValue"] {
        color: #7877c6 !important;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #b8b8d4 !important;
        font-weight: 500 !important;
    }
    
    .streamlit-expanderHeader {
        background: linear-gradient(90deg, rgba(120, 119, 198, 0.3), rgba(118, 75, 162, 0.3));
        color: #e0e0e0 !important;
        border-radius: 12px;
        font-weight: 500;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .streamlit-expanderHeader:hover {
        background: linear-gradient(90deg, rgba(120, 119, 198, 0.5), rgba(118, 75, 162, 0.5));
    }
    
    .streamlit-expanderContent {
        background: rgba(20, 20, 40, 0.5);
        border-radius: 0 0 12px 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-top: none;
    }
    
    .stProgress > div > div {
        background: linear-gradient(90deg, #7877c6, #764ba2) !important;
    }
    
    .stProgress > div {
        background: rgba(20, 20, 40, 0.5) !important;
        border-radius: 10px;
    }
    
    .memory-badge {
        display: inline-block;
        background: rgba(120, 119, 198, 0.2);
        border: 1px solid rgba(120, 119, 198, 0.4);
        border-radius: 8px;
        padding: 4px 12px;
        margin: 4px;
        font-size: 0.85rem;
        color: #b8b8d4;
    }
    
    .confidence-high {
        color: #4ade80 !important;
    }
    
    .confidence-medium {
        color: #fbbf24 !important;
    }
    
    .confidence-low {
        color: #f87171 !important;
    }
    
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(20, 20, 40, 0.5);
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #7877c6, #764ba2);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #8887d7, #8765b2);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(30, 30, 60, 0.4);
        border-radius: 8px;
        color: #b8b8d4;
        padding: 8px 16px;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #7877c6 0%, #764ba2 100%);
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "turn_count" not in st.session_state:
    st.session_state.turn_count = 0
if "memory_analytics" not in st.session_state:
    st.session_state.memory_analytics = {
        "turns": [],
        "memories_recalled": [],
        "confidence_scores": []
    }

# Helper Functions
def typing_animation(text, delay=0.02):
    """Simulate typing effect like Claude/Gemini"""
    placeholder = st.empty()
    displayed_text = ""
    for char in text:
        displayed_text += char
        placeholder.markdown(displayed_text)
        time.sleep(delay)
    return placeholder

def get_confidence_color(distance):
    """Convert distance to confidence color"""
    if distance < 0.8:
        return "confidence-high", "🟢"
    elif distance < 1.2:
        return "confidence-medium", "🟡"
    else:
        return "confidence-low", "🔴"

def load_memory_state():
    """Load and parse memory state"""
    try:
        with open("database/user_state.json", "r") as f:
            return json.load(f)
    except:
        return {}

# Header with Turn Counter
col1, col2, col3 = st.columns([3, 1, 1])
with col1:
    st.title("🧠 MemoryOS")
    st.caption("Long-Form Memory System - Retaining Information Across 1,000+ Turns")
with col2:
    st.metric("Current Turn", st.session_state.turn_count, delta=None)
with col3:
    st.metric("Messages", len(st.session_state.messages))

st.divider()

# Sidebar with Enhanced Analytics
with st.sidebar:
    st.header("🎯 Memory Analytics")
    
    # Load state
    core_state = load_memory_state()
    
    # Key Metrics
    st.subheader("📊 System Stats")
    
    col1, col2 = st.columns(2)
    with col1:
        total_entities = len(core_state.get("entities", {}))
        st.metric("Entities", total_entities)
    with col2:
        total_events = len(core_state.get("events", []))
        st.metric("Events", total_events)
    
    # Memory Recall Rate
    if st.session_state.memory_analytics["turns"]:
        avg_recall = sum(st.session_state.memory_analytics["memories_recalled"]) / len(st.session_state.memory_analytics["memories_recalled"])
        st.metric("Avg Recall/Turn", f"{avg_recall:.1f}")
    
    st.divider()
    
    # Memory Timeline Chart
    st.subheader("📈 Memory Timeline")
    if st.session_state.memory_analytics["turns"]:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=st.session_state.memory_analytics["turns"],
            y=st.session_state.memory_analytics["memories_recalled"],
            mode='lines+markers',
            name='Memories Recalled',
            line=dict(color='#7877c6', width=2),
            marker=dict(size=6)
        ))
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(20,20,40,0.5)',
            font=dict(color='#e0e0e0'),
            height=200,
            margin=dict(l=0, r=0, t=20, b=0),
            xaxis_title="Turn",
            yaxis_title="Memories"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Start chatting to see memory analytics")
    
    st.divider()
    
    # User Profile Preview
    st.subheader("👤 User Profile")
    profile = core_state.get("user_profile", {})
    if profile:
        for key, value in profile.items():
            if value and key not in ["preferences", "goals"]:
                st.markdown(f"**{key.title()}:** {value}")
    else:
        st.caption("No profile data yet")
    
    st.divider()
    
    # Entity Network Preview
    st.subheader("🌐 Entity Network")
    entities = core_state.get("entities", {})
    if entities:
        entity_types = defaultdict(int)
        for entity in entities.values():
            rel = entity.get("relationship", "Unknown")
            entity_types[rel] += 1
        
        df = pd.DataFrame(list(entity_types.items()), columns=["Type", "Count"])
        fig = px.pie(df, values="Count", names="Type", hole=0.4)
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e0e0e0'),
            height=200,
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.caption("No entities tracked yet")
    
    st.divider()
    
    # Action Buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    with col2:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    
    # Export Demo Data
    if st.button("📥 Export Analytics", use_container_width=True):
        export_data = {
            "turn_count": st.session_state.turn_count,
            "total_messages": len(st.session_state.messages),
            "analytics": st.session_state.memory_analytics,
            "state": core_state
        }
        st.download_button(
            "Download JSON",
            json.dumps(export_data, indent=2),
            "memory_analytics.json",
            "application/json",
            use_container_width=True
        )
    
    st.divider()
    
    # Full State Viewer
    with st.expander("🔍 View Full Memory State"):
        st.json(core_state)

# Main Chat Interface with Tabs
tab1, tab2, tab3 = st.tabs(["💬 Chat", "🔍 Memory Search", "📊 Analytics Dashboard"])

with tab1:
    # Welcome Message
    if len(st.session_state.messages) == 0:
        st.info("👋 **Welcome to MemoryOS!** This system can remember information across 1,000+ conversation turns.")
        
        # Feature showcase
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("#### 🎯 Precise Recall")
            st.caption("Remembers Turn 1 info at Turn 1000")
        
        with col2:
            st.markdown("#### 🧮 Vector Search")
            st.caption("Semantic retrieval with confidence scoring")
        
        with col3:
            st.markdown("#### 📈 Analytics")
            st.caption("Track memory performance in real-time")
        
        with col4:
            st.markdown("#### 🔄 Adaptive")
            st.caption("Updates and refines over time")
        
        st.divider()
        
        # Demo suggestions
        st.markdown("### 💡 Try these demo scenarios:")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🏢 Professional Scenario", use_container_width=True):
                st.session_state.demo_prompt = "Hi! My name is Alex. I work as a software engineer at TechCorp. My boss is Sarah Chen."
        
        with col2:
            if st.button("🎓 Student Scenario", use_container_width=True):
                st.session_state.demo_prompt = "Hello! I'm a Computer Science student at MIT. I'm working on my thesis about neural networks."
        
        with col3:
            if st.button("🌍 Travel Scenario", use_container_width=True):
                st.session_state.demo_prompt = "Hey! I just moved to Tokyo from New York. I love sushi and prefer meetings after 2 PM JST."
        
        st.divider()
    
    # Display Chat Messages
    for idx, message in enumerate(st.session_state.messages):
        avatar = "👤" if message["role"] == "user" else "🤖"
        
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])
            
            # Show memory badges for assistant messages
            if message["role"] == "assistant":
                memories = message.get("memories", [])
                
                if memories:
                    st.markdown("---")
                    st.markdown("**🧠 Active Memories:**")
                    
                    cols = st.columns(3)
                    for i, mem in enumerate(memories[:6]):  # Show top 6
                        with cols[i % 3]:
                            # Extract info
                            mem_content = mem.get("content", "")[:50]
                            distance = mem.get("distance", 1.5)
                            origin = mem.get("origin_turn", 0)
                            
                            # Get confidence
                            conf_class, conf_icon = get_confidence_color(distance)
                            
                            st.markdown(f"""
                            <div class="memory-badge">
                                {conf_icon} Turn {origin}<br>
                                <small>{mem_content}...</small><br>
                                <small class="{conf_class}">Confidence: {1-distance:.2f}</small>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    if len(memories) > 6:
                        with st.expander(f"View all {len(memories)} memories"):
                            for mem in memories:
                                st.json(mem)
                
                # --- NEW: Raw Prompt Viewer (For History) ---
                if "debug_prompt" in message:
                    with st.expander("🛠️ View Raw Prompt"):
                        st.code(message["debug_prompt"], language="text")

    # Chat Input
    if prompt := st.chat_input("💭 Type your message... (or use demo buttons above)"):
        # Process user input
        st.session_state.turn_count += 1
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        
        # Call Backend with loading animation
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("🤔 Thinking..."):
                try:
                    response = requests.post(
                        "http://localhost:8000/chat",
                        json={"message": prompt},
                        timeout=30
                    )
                    data = response.json()
                    bot_reply = data["response"]
                    memories = data.get("active_memories", [])
                    # --- NEW: Get debug info ---
                    debug_prompt = data.get("debug_prompt", "No debug info")
                    
                    # Typing animation
                    typing_animation(bot_reply, delay=0.01)
                    
                    # Update analytics
                    st.session_state.memory_analytics["turns"].append(st.session_state.turn_count)
                    st.session_state.memory_analytics["memories_recalled"].append(len(memories))
                    if memories:
                        avg_distance = sum(m.get("distance", 1.5) for m in memories) / len(memories)
                        st.session_state.memory_analytics["confidence_scores"].append(1 - avg_distance)
                    
                    # Store message
                    message_data = {
                        "role": "assistant",
                        "content": bot_reply,
                        "memories": memories,
                        # --- NEW: Store debug info ---
                        "debug_prompt": debug_prompt,
                        "turn": st.session_state.turn_count
                    }
                    st.session_state.messages.append(message_data)
                    
                    # Show memories
                    if memories:
                        st.markdown("---")
                        st.markdown("**🧠 Active Memories:**")
                        
                        cols = st.columns(3)
                        for i, mem in enumerate(memories[:6]):
                            with cols[i % 3]:
                                mem_content = mem.get("content", "")[:50]
                                distance = mem.get("distance", 1.5)
                                origin = mem.get("origin_turn", 0)
                                conf_class, conf_icon = get_confidence_color(distance)
                                
                                st.markdown(f"""
                                <div class="memory-badge">
                                    {conf_icon} Turn {origin}<br>
                                    <small>{mem_content}...</small><br>
                                    <small class="{conf_class}">Confidence: {1-distance:.2f}</small>
                                </div>
                                """, unsafe_allow_html=True)
                    
                    # --- NEW: Raw Prompt Viewer (Immediate) ---
                    with st.expander("🛠️ View Raw Prompt (Debug)"):
                        st.code(debug_prompt, language="text")
                        st.caption(f"Prompt Character Count: {len(debug_prompt)}")
                    
                    st.rerun()
                    
                except requests.exceptions.ConnectionError:
                    st.error("❌ **Connection Error**: Backend not reachable at `http://localhost:8000`")
                    st.info("💡 Start the backend server with: `uvicorn main:app --reload`")
                except requests.exceptions.Timeout:
                    st.error("⏱️ Request timed out. Try again.")
                except Exception as e:
                    st.error(f"❌ **Error**: {str(e)}")
    
    # Handle demo prompts
    if "demo_prompt" in st.session_state and st.session_state.demo_prompt:
        # Trigger rerun to process demo prompt
        st.session_state.messages.append({"role": "user", "content": st.session_state.demo_prompt})
        st.session_state.demo_prompt = None
        st.rerun()

with tab2:
    st.header("🔍 Memory Search & Testing")
    st.markdown("Test the long-form memory retrieval system")
    
    search_query = st.text_input("Enter search query:", placeholder="e.g., What's my boss's name?")
    
    col1, col2 = st.columns(2)
    with col1:
        n_results = st.slider("Number of results", 1, 10, 3)
    with col2:
        threshold = st.slider("Distance threshold", 0.0, 2.0, 1.3, 0.1)
    
    if st.button("🔍 Search Memory", type="primary"):
        if search_query:
            with st.spinner("Searching..."):
                try:
                    # Simulate search (you'd call your actual archival search here)
                    st.success(f"Searching for: '{search_query}'")
                    st.info("⚠️ Connect this to your `archival_memory_search` API endpoint")
                    
                    # Mock results for demo
                    st.markdown("### Search Results:")
                    st.json({
                        "query": search_query,
                        "results_found": 3,
                        "threshold": threshold
                    })
                    
                except Exception as e:
                    st.error(f"Search failed: {e}")
        else:
            st.warning("Please enter a search query")
    
    st.divider()
    
    # Memory Browser
    st.subheader("📚 Memory Browser")
    core_state = load_memory_state()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🏢 Entities**")
        entities = core_state.get("entities", {})
        if entities:
            for name, data in list(entities.items())[:5]:
                with st.expander(f"👤 {data.get('name', name)}"):
                    st.json(data)
        else:
            st.caption("No entities yet")
    
    with col2:
        st.markdown("**📅 Events**")
        events = core_state.get("events", [])
        if events:
            for event in events[-5:]:
                with st.expander(f"📌 Turn {event.get('turn')}"):
                    st.json(event)
        else:
            st.caption("No events yet")

with tab3:
    st.header("📊 Analytics Dashboard")
    
    # Performance Metrics
    st.subheader("🎯 System Performance")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Turns",
            st.session_state.turn_count,
            delta=f"{(st.session_state.turn_count/1000)*100:.1f}% of 1K target"
        )
    
    with col2:
        if st.session_state.memory_analytics["memories_recalled"]:
            avg_recall = sum(st.session_state.memory_analytics["memories_recalled"]) / len(st.session_state.memory_analytics["memories_recalled"])
            st.metric("Avg Memory Recall", f"{avg_recall:.2f}", delta="per turn")
        else:
            st.metric("Avg Memory Recall", "0.00")
    
    with col3:
        if st.session_state.memory_analytics["confidence_scores"]:
            avg_conf = sum(st.session_state.memory_analytics["confidence_scores"]) / len(st.session_state.memory_analytics["confidence_scores"])
            st.metric("Avg Confidence", f"{avg_conf:.2%}", delta=None)
        else:
            st.metric("Avg Confidence", "0%")
    
    with col4:
        core_state = load_memory_state()
        total_memories = len(core_state.get("entities", {})) + len(core_state.get("events", []))
        st.metric("Total Memories", total_memories)
    
    st.divider()
    
    # Detailed Charts
    if st.session_state.memory_analytics["turns"]:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Memory Recall Over Time")
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=st.session_state.memory_analytics["turns"],
                y=st.session_state.memory_analytics["memories_recalled"],
                mode='lines+markers',
                fill='tozeroy',
                line=dict(color='#7877c6', width=2),
                marker=dict(size=8)
            ))
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(20,20,40,0.5)',
                font=dict(color='#e0e0e0'),
                height=300,
                xaxis_title="Turn Number",
                yaxis_title="Memories Recalled"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("🎯 Confidence Score Trend")
            if st.session_state.memory_analytics["confidence_scores"]:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=st.session_state.memory_analytics["turns"][:len(st.session_state.memory_analytics["confidence_scores"])],
                    y=st.session_state.memory_analytics["confidence_scores"],
                    mode='lines+markers',
                    fill='tozeroy',
                    line=dict(color='#4ade80', width=2),
                    marker=dict(size=8)
                ))
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(20,20,40,0.5)',
                    font=dict(color='#e0e0e0'),
                    height=300,
                    xaxis_title="Turn Number",
                    yaxis_title="Confidence Score"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No confidence data yet")
    else:
        st.info("Start chatting to generate analytics")
    
    st.divider()
    
    # Memory Heatmap
    st.subheader("🔥 Memory Usage Heatmap")
    core_state = load_memory_state()
    events = core_state.get("events", [])
    
    if events:
        # Group events by date
        from collections import Counter
        dates = [e.get("date", "Unknown") for e in events]
        date_counts = Counter(dates)
        
        df = pd.DataFrame(list(date_counts.items()), columns=["Date", "Events"])
        
        fig = px.bar(df, x="Date", y="Events", color="Events",
                     color_continuous_scale="Purples")
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(20,20,40,0.5)',
            font=dict(color='#e0e0e0'),
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No event data yet")

# Footer
st.divider()
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.caption(f"MemoryOS v2.0 • Long-Form Memory System • {datetime.now().year}")
with col2:
    st.caption(f"🎯 Goal: 1,000+ turns")
with col3:
    st.caption(f"✅ Current: {st.session_state.turn_count} turns")