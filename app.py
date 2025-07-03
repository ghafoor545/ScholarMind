import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load API key
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

st.set_page_config(page_title="ScholarMind – AI Co-Author", layout="centered")
st.title("📚 ScholarMind – AI Co-Author for Academic Research")

# --- Session Variables ---
if "final_topic" not in st.session_state:
    st.session_state.final_topic = None
if "topic_stage" not in st.session_state:
    st.session_state.topic_stage = "selecting"
if "trending_topics" not in st.session_state:
    st.session_state.trending_topics = []
if "subtopics" not in st.session_state:
    st.session_state.subtopics = []
if "subtopic_round" not in st.session_state:
    st.session_state.subtopic_round = 1
if "show_subtopic_section" not in st.session_state:
    st.session_state.show_subtopic_section = False

# --- Get New Trending Topics ---
def get_trending_topics():
    prompt = "Give me 5 currently trending and high-impact academic research topics. Numbered list. Long sentence-style titles. Do NOT include any explanation."
    response = model.generate_content(prompt).text
    topics = [line.split(". ", 1)[1] for line in response.strip().split("\n") if ". " in line]
    return [topic for topic in topics if topic.strip() != ""]

if not st.session_state.trending_topics:
    st.session_state.trending_topics = get_trending_topics()

# --- Step 1: Trending Topic ---
st.markdown("### 🔥 Trending Topics (Pick One)")
spaced_topics = [f"{topic}\n" for topic in st.session_state.trending_topics]
selected_trending = st.radio("Choose a topic:", spaced_topics, index=None, format_func=lambda x: x.strip())

# --- Step 2: Custom Topic ---
st.markdown("### ✍️ Or Enter Your Own Topic")
custom_topic = st.text_input("Enter your own research topic (optional):").strip()

# --- Confirm Topic ---
if st.button("✅ Confirm Topic"):
    if custom_topic:
        st.session_state.final_topic = custom_topic
        st.session_state.topic_stage = "confirm"
    elif selected_trending:
        st.session_state.final_topic = selected_trending.strip()
        st.session_state.trending_topics = get_trending_topics()
        st.session_state.topic_stage = "confirm"
    else:
        st.warning("⚠️ Please select a trending topic or enter your own.")

# --- Step 3: Subtopic or Proceed ---
if st.session_state.topic_stage == "confirm" and st.session_state.final_topic:
    st.success(f"✅ Final Selected Topic: **{st.session_state.final_topic}**")

    choice = st.radio("🔄 Do you want to generate subtopics?", ["Choose One", "Generate Subtopics", "Proceed with Main Topic"])

    if choice == "Generate Subtopics":
        if not st.session_state.show_subtopic_section:
            st.session_state.show_subtopic_section = True
            st.session_state.subtopic_round = 1
            sub_prompt = f"Suggest 5 subtopics for: '{st.session_state.final_topic}'. Numbered list only."
            sub_resp = model.generate_content(sub_prompt).text
            st.session_state.subtopics = [line.split(". ", 1)[1] for line in sub_resp.strip().split("\n") if ". " in line]

        if st.session_state.show_subtopic_section:
            st.markdown(f"### 🔽 Subtopic Round {st.session_state.subtopic_round}")
            chosen_sub = st.radio("Select a subtopic:", st.session_state.subtopics, key=f"subtopic_round_{st.session_state.subtopic_round}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("➕ More Subtopics", key=f"more_{st.session_state.subtopic_round}"):
                    st.session_state.subtopic_round += 1
                    sub_prompt = f"Suggest 5 new subtopics for: '{st.session_state.final_topic}', different from earlier. Numbered only."
                    sub_resp = model.generate_content(sub_prompt).text
                    new_subtopics = [line.split(". ", 1)[1] for line in sub_resp.strip().split("\n") if ". " in line]

                    if new_subtopics != st.session_state.subtopics:
                        st.session_state.subtopics = new_subtopics
                    else:
                        st.warning("⚠️ Same subtopics again. Trying again...")

                    st.rerun()

            with col2:
                if st.button("✅ Confirm this Subtopic", key=f"confirm_{st.session_state.subtopic_round}"):
                    st.session_state.final_topic = chosen_sub
                    st.session_state.topic_stage = "generate"
                    st.session_state.show_subtopic_section = False

    elif choice == "Proceed with Main Topic":
        st.session_state.topic_stage = "generate"

# --- Final Output Section ---
if st.session_state.topic_stage == "generate":
    topic = st.session_state.final_topic
    st.markdown("---")
    st.markdown(f"### 🧠 Final Research Topic: **{topic}**")

    # 1. Research Questions
    st.subheader("🔍 Research Questions")
    q_prompt = f"Suggest 3 research questions on the topic: '{topic}'"
    q_response = model.generate_content(q_prompt)
    st.markdown(q_response.text)

    # 2. Literature Review
    st.subheader("📚 Literature Review")
    literature_prompt = f"""
You are an academic researcher. Write a detailed academic literature review (400–500 words) on the topic: "{topic}".

📅 Structure:
- Mention exactly 5 relevant academic papers
- Start each paper on a new line (e.g., "Paper 1:", "Paper 2:", etc.)
- Summarize each paper in 2–3 lines: include key contribution, author(s), and year if known
- After describing all 5, summarize the overall findings, highlight contradictions, and identify research gaps
- Conclude with future research directions
"""
    lit_response = model.generate_content(literature_prompt)
    st.markdown(lit_response.text)

    # 3. Future Directions
    st.subheader("🔮 Future Research Directions")
    future_prompt = f"List 5 future research directions for: '{topic}' in bullet points"
    future_response = model.generate_content(future_prompt)
    st.markdown(future_response.text)

    # 4. References
    st.subheader("📎 Structured APA References")
    references_prompt = f"""
You are an academic assistant. Provide 5 APA-style references for peer-reviewed research papers related to the topic "{topic}".

📅 Structure:
- Format each reference in APA 7 style
- Include author(s), year, title, journal, volume(issue), pages, and DOI (if available)
- List each reference on a new line with numbering (1. 2. 3.)
"""
    cite_response = model.generate_content(references_prompt)
    st.markdown(cite_response.text)

    # 5. Academic Abstract
    st.subheader("🧠 Academic Abstract")
    abstract_prompt = f"Write a formal academic abstract (150-200 words) for the research topic: '{topic}'"
    abstract_response = model.generate_content(abstract_prompt)
    st.markdown(abstract_response.text)

    # 6. Main Body Breakdown
    st.subheader("📜 Detailed Topic Breakdown")
    main_analysis_prompt = f"""
I want you to act as an elite research analyst with deep experience in synthesizing complex information into clear, concise insights.

Your task is to conduct a comprehensive research breakdown on the following topic:

{topic}

Here's how I want you to proceed:
1. Start with a brief, plain-English overview of the topic.
2. Break the topic into 3–5 major sub-topics or components.
3. For each sub-topic, provide:
   - A short definition or explanation
   - Key facts, trends, or recent developments
   - Any major debates or differing perspectives
4. Include notable data, statistics, or real-world examples where relevant.
5. Recommend 3–5 high-quality resources for further reading.
6. End with a “Smart Summary” — 5 bullet points that provide an executive-style briefing.
"""
    analysis_response = model.generate_content(main_analysis_prompt)
    st.markdown(analysis_response.text)
