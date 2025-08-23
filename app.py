"""
AI-Powered Student Learning App
Designed for AP State Board Syllabus (Classes 1-10)
Updated with Continuous Adaptive Quiz System
"""

import streamlit as st
import os
import json
from datetime import datetime
from typing import Dict, List, Any
import random

# Import custom modules
from curriculum_data import get_curriculum_data
from ai_assistant import AIAssistant
from quiz_generator import QuizGenerator
from video_recommender import VideoRecommender
from student_history import StudentHistory

# Page configuration
st.set_page_config(
    page_title="🎓 AI Learning Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_session_state():
    """Initialize session state variables"""
    if 'api_key' not in st.session_state:
        st.session_state.api_key = ""
    if 'student_name' not in st.session_state:
        st.session_state.student_name = ""
    if 'selected_class' not in st.session_state:
        st.session_state.selected_class = None
    if 'selected_subject' not in st.session_state:
        st.session_state.selected_subject = None
    if 'selected_chapter' not in st.session_state:
        st.session_state.selected_chapter = None
    if 'selected_topic' not in st.session_state:
        st.session_state.selected_topic = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "authentication"
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'quiz_questions' not in st.session_state:
        st.session_state.quiz_questions = []
    if 'quiz_score' not in st.session_state:
        st.session_state.quiz_score = 0
    if 'current_question_index' not in st.session_state:
        st.session_state.current_question_index = 0
    if 'student_history' not in st.session_state:
        st.session_state.student_history = StudentHistory()
    
    # Additional session state for quiz functionality
    if 'continuous_quiz_active' not in st.session_state:
        st.session_state.continuous_quiz_active = False
    if 'continuous_quiz_difficulty' not in st.session_state:
        st.session_state.continuous_quiz_difficulty = "easy"
    if 'continuous_quiz_stats' not in st.session_state:
        st.session_state.continuous_quiz_stats = {
            'total_questions': 0,
            'correct_answers': 0,
            'consecutive_correct': 0,
            'consecutive_wrong': 0,
            'question_history': [],
            'last_wrong_concept': None
        }
    if 'current_adaptive_question' not in st.session_state:
        st.session_state.current_adaptive_question = None
    if 'show_feedback' not in st.session_state:
        st.session_state.show_feedback = False
    if 'last_answer_correct' not in st.session_state:
        st.session_state.last_answer_correct = None
    if 'last_question' not in st.session_state:
        st.session_state.last_question = None
    if 'last_selected_answer' not in st.session_state:
        st.session_state.last_selected_answer = None
    
    # Hint system session state
    if 'show_hint_popup' not in st.session_state:
        st.session_state.show_hint_popup = False
    if 'hint_chat_history' not in st.session_state:
        st.session_state.hint_chat_history = []
    if 'hint_level' not in st.session_state:
        st.session_state.hint_level = 0
    if 'hint_question_data' not in st.session_state:
        st.session_state.hint_question_data = None
    
    # Final quiz session state
    if 'final_quiz_active' not in st.session_state:
        st.session_state.final_quiz_active = False
    if 'final_quiz_questions' not in st.session_state:
        st.session_state.final_quiz_questions = []
    if 'final_quiz_answers' not in st.session_state:
        st.session_state.final_quiz_answers = {}
    if 'final_quiz_submitted' not in st.session_state:
        st.session_state.final_quiz_submitted = False
    if 'final_quiz_score' not in st.session_state:
        st.session_state.final_quiz_score = 0
    if 'final_quiz_detailed_results' not in st.session_state:
        st.session_state.final_quiz_detailed_results = []
    
    # Popup Q&A session state
    if 'show_qa_popup' not in st.session_state:
        st.session_state.show_qa_popup = False
    if 'popup_chat_history' not in st.session_state:
        st.session_state.popup_chat_history = []
    
    # Topic explanation session state
    if 'current_explanation' not in st.session_state:
        st.session_state.current_explanation = None

def authentication_page():
    """Authentication page for API key and student details"""
    st.title("🎓 Welcome to AI Learning Assistant")
    st.subheader("🏛️ AP State Board Syllabus Learning Platform")
    
    with st.form("auth_form"):
        st.markdown("### 🔐 Authentication")
        
        col1, col2 = st.columns(2)
        
        with col1:
            student_name = st.text_input("👤 Student Name", placeholder="Enter your name")
        
        with col2:
            api_key = st.text_input("🔑 OpenAI API Key", type="password", 
                                  placeholder="sk-...")
        
        st.markdown("---")
        st.markdown("**📝 Note:** Your API key is kept secure and only used for generating educational content.")
        
        submit_button = st.form_submit_button("🚀 Start Learning Journey")
        
        if submit_button:
            if student_name.strip() and api_key.strip():
                st.session_state.student_name = student_name.strip()
                st.session_state.api_key = api_key.strip()
                st.session_state.current_page = "class_selection"
                st.rerun()
            else:
                st.error("⚠️ Please provide both your name and OpenAI API key.")

def class_selection_page():
    """Class selection page"""
    st.title(f"👋 Welcome {st.session_state.student_name}!")
    st.subheader("📚 Select Your Class")
    
    curriculum = get_curriculum_data()
    
    col1, col2, col3 = st.columns(3)
    
    classes = list(curriculum.keys())
    
    for i, class_name in enumerate(classes):
        col = [col1, col2, col3][i % 3]
        
        with col:
            if st.button(f"📖 {class_name}", key=f"class_{i}", use_container_width=True):
                st.session_state.selected_class = class_name
                st.session_state.current_page = "subject_selection"
                st.rerun()

def subject_selection_page():
    """Subject selection page"""
    st.title(f"📚 {st.session_state.selected_class}")
    st.subheader("🎯 Choose Your Subject")
    
    curriculum = get_curriculum_data()
    subjects = curriculum[st.session_state.selected_class]
    
    col1, col2 = st.columns(2)
    
    for i, subject in enumerate(subjects.keys()):
        col = col1 if i % 2 == 0 else col2
        
        with col:
            if st.button(f"📘 {subject}", key=f"subject_{i}", use_container_width=True):
                st.session_state.selected_subject = subject
                st.session_state.current_page = "chapter_selection"
                st.rerun()
    
    if st.button("⬅️ Back to Class Selection"):
        st.session_state.current_page = "class_selection"
        st.session_state.selected_class = None
        st.rerun()

def chapter_selection_page():
    """Chapter selection page"""
    st.title(f"📖 {st.session_state.selected_class} - {st.session_state.selected_subject}")
    st.subheader("📑 Select Chapter")
    
    curriculum = get_curriculum_data()
    chapters = curriculum[st.session_state.selected_class][st.session_state.selected_subject]
    
    for i, chapter in enumerate(chapters.keys()):
        if st.button(f"📄 {chapter}", key=f"chapter_{i}", use_container_width=True):
            st.session_state.selected_chapter = chapter
            st.session_state.current_page = "topic_selection"
            st.rerun()
    
    if st.button("⬅️ Back to Subject Selection"):
        st.session_state.current_page = "subject_selection"
        st.session_state.selected_subject = None
        st.rerun()

def topic_selection_page():
    """Topic selection page"""
    st.title(f"📚 {st.session_state.selected_subject} - {st.session_state.selected_chapter}")
    st.subheader("🎯 Choose Your Topic")
    
    curriculum = get_curriculum_data()
    topics = curriculum[st.session_state.selected_class][st.session_state.selected_subject][st.session_state.selected_chapter]
    
    for i, topic in enumerate(topics):
        if st.button(f"📝 {topic}", key=f"topic_{i}", use_container_width=True):
            st.session_state.selected_topic = topic
            st.session_state.current_page = "learning_hub"
            # Reset chat history for new topic
            st.session_state.chat_history = []
            # Reset explanation for new topic
            st.session_state.current_explanation = None
            # Reset continuous quiz state for new topic
            if 'continuous_quiz_active' in st.session_state:
                st.session_state.continuous_quiz_active = False
                st.session_state.continuous_quiz_stats = {
                    'total_questions': 0,
                    'correct_answers': 0,
                    'consecutive_correct': 0,
                    'consecutive_wrong': 0,
                    'question_history': [],
                    'last_wrong_concept': None
                }
                st.session_state.current_adaptive_question = None
                st.session_state.show_feedback = False
            st.rerun()
    
    if st.button("⬅️ Back to Chapter Selection"):
        st.session_state.current_page = "chapter_selection"
        st.session_state.selected_chapter = None
        st.rerun()

def learning_hub_page():
    """Main learning hub with all features"""
    st.title(f"🎓 Learning: {st.session_state.selected_topic}")
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("### 🧭 Learning Menu")
        
        menu_option = st.radio(
            "Choose learning mode:",
            ["📖 Topic Explanation", "💬 Interactive Q&A", "🎥 Video Learning", 
             "🧩 Mini Quiz", "📝 Final Quiz", "📊 My Progress"]
        )
        
        st.markdown("---")
        if st.button("🏠 Back to Topics"):
            st.session_state.current_page = "topic_selection"
            st.session_state.selected_topic = None
            # Reset explanation when leaving topic
            st.session_state.current_explanation = None
            # Reset quiz states when leaving topic
            if 'continuous_quiz_active' in st.session_state:
                st.session_state.continuous_quiz_active = False
            st.rerun()
    
    # Main content area
    if menu_option == "📖 Topic Explanation":
        topic_explanation_section()
    elif menu_option == "💬 Interactive Q&A":
        interactive_qa_section()
    elif menu_option == "🎥 Video Learning":
        video_learning_section()
    elif menu_option == "🧩 Mini Quiz":
        mini_quiz_section()
    elif menu_option == "📝 Final Quiz":
        final_quiz_section()
    elif menu_option == "📊 My Progress":
        progress_section()

def topic_explanation_section():
    """Topic explanation section"""
    st.subheader("📖 Topic Explanation")
    
    # Create two columns for the main button and popup button
    col1, col2 = st.columns([3, 1])
    
    with col1:
        generate_explanation = st.button("🎯 Generate Explanation", type="primary")
    
    with col2:
        open_qa_popup = st.button("💬 Quick Q&A", help="Ask questions about this topic in a popup")
    
    # Handle explanation generation
    if generate_explanation:
        with st.spinner("🤖 AI is preparing your lesson..."):
            ai_assistant = AIAssistant(st.session_state.api_key)
            
            explanation = ai_assistant.generate_topic_explanation(
                topic=st.session_state.selected_topic,
                subject=st.session_state.selected_subject,
                class_level=st.session_state.selected_class
            )
            
            # Store explanation in session state
            st.session_state.current_explanation = explanation
            
            # Record this study session
            st.session_state.student_history.add_topic_studied(
                st.session_state.selected_class,
                st.session_state.selected_subject,
                st.session_state.selected_chapter,
                st.session_state.selected_topic
            )
    
    # Display explanation if it exists
    if st.session_state.current_explanation:
        st.markdown("### 📚 Lesson Content")
        st.markdown(st.session_state.current_explanation)
    
    # Handle Q&A popup
    if open_qa_popup:
        st.session_state.show_qa_popup = True
    
    # Initialize popup state if not exists
    if 'show_qa_popup' not in st.session_state:
        st.session_state.show_qa_popup = False
    
    # Show Q&A popup dialog
    if st.session_state.show_qa_popup:
        show_qa_popup_dialog()

@st.dialog("💬 Quick Q&A")
def show_qa_popup_dialog():
    """Popup dialog for interactive Q&A about the current topic"""
    
    # Initialize popup chat history if not exists
    if 'popup_chat_history' not in st.session_state:
        st.session_state.popup_chat_history = []
    
    # Display current topic info
    topic_title = st.session_state.get('selected_topic', 'Unknown Topic')
    subject_info = st.session_state.get('selected_subject', 'Unknown Subject')
    class_info = st.session_state.get('selected_class', 'Unknown Class')
    
    st.markdown(f"**🎯 Current Topic:** {topic_title}")
    st.markdown(f"**📚 Subject:** {subject_info} ({class_info})")
    st.markdown("---")
    
    # Display popup chat history in a container with max height
    chat_container = st.container(height=300)
    with chat_container:
        if not st.session_state.popup_chat_history:
            st.info("👋 Ask me anything about this topic! I'm here to help you understand better.")
        else:
            for message in st.session_state.popup_chat_history:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
    
    # Chat input for popup
    popup_prompt = st.chat_input("Ask your question about the topic...", key="popup_chat_input")
    
    if popup_prompt:
        # Add user message to popup chat history
        st.session_state.popup_chat_history.append({"role": "user", "content": popup_prompt})
        
        # Generate AI response
        with st.spinner("🤔 Thinking..."):
            ai_assistant = AIAssistant(st.session_state.api_key)
            
            response = ai_assistant.answer_question(
                question=popup_prompt,
                topic=st.session_state.selected_topic,
                subject=st.session_state.selected_subject,
                class_level=st.session_state.selected_class
            )
            
            # Add assistant response to popup chat history
            st.session_state.popup_chat_history.append({"role": "assistant", "content": response})
            
            # Record this interaction
            st.session_state.student_history.add_chat_interaction(
                st.session_state.selected_topic,
                popup_prompt,
                response
            )
        
        st.rerun()
    
    # Close button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.popup_chat_history = []
            st.rerun()
    
    with col2:
        if st.button("📋 Copy to Main Chat", use_container_width=True):
            # Copy popup chat to main chat history
            st.session_state.chat_history.extend(st.session_state.popup_chat_history)
            st.session_state.popup_chat_history = []
            st.success("✅ Chat copied to main Q&A section!")
            st.rerun()
    
    with col3:
        if st.button("❌ Close", use_container_width=True):
            st.session_state.show_qa_popup = False
            st.rerun()

@st.dialog("💡 Interactive Hint System")
def show_hint_popup_dialog():
    """Interactive hint system popup for quiz questions"""
    
    if not st.session_state.hint_question_data:
        st.error("No question data available for hints.")
        return
    
    question = st.session_state.hint_question_data
    
    # Display question info
    st.markdown(f"**❓ Question:** {question['question']}")
    st.markdown(f"**📚 Subject:** {st.session_state.selected_subject}")
    st.markdown(f"**🎯 Topic:** {st.session_state.selected_topic}")
    st.markdown("---")
    
    # Initialize hint system if first time
    if not st.session_state.hint_chat_history:
        # Add initial tutor message
        initial_message = f"""👋 Hi! I'm your tutor for this question. 

**My goal:** Help you solve this step by step, WITHOUT giving away the full answer immediately!

**How I work:**
🔍 I'll give you progressive hints
💭 Wait for your response before the next hint  
📝 Guide you through the problem-solving process
✨ Only show the complete solution if you really need it

**Ready to start?** Tell me what you think about this question or ask for your first hint!"""
        
        st.session_state.hint_chat_history.append({
            "role": "assistant", 
            "content": initial_message
        })
    
    # Display hint chat history in a container with max height
    chat_container = st.container(height=400)
    with chat_container:
        for message in st.session_state.hint_chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Chat input for hints
    hint_prompt = st.chat_input("Ask for a hint or share your thoughts...", key="hint_chat_input")
    
    if hint_prompt:
        # Add user message to hint chat history
        st.session_state.hint_chat_history.append({"role": "user", "content": hint_prompt})
        
        # Generate AI hint response
        with st.spinner("🤔 Thinking of the perfect hint..."):
            ai_assistant = AIAssistant(st.session_state.api_key)
            
            # Create specialized hint prompt
            hint_response = generate_interactive_hint(
                ai_assistant,
                question,
                hint_prompt,
                st.session_state.hint_chat_history,
                st.session_state.hint_level
            )
            
            # Add assistant response to hint chat history
            st.session_state.hint_chat_history.append({"role": "assistant", "content": hint_response})
            
            # Increment hint level
            st.session_state.hint_level += 1
        
        st.rerun()
    
    # Control buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🔄 Reset Hints", use_container_width=True):
            st.session_state.hint_chat_history = []
            st.session_state.hint_level = 0
            st.rerun()
    
    with col2:
        if st.button("🏳️ Show Solution", use_container_width=True):
            # Add full solution to chat
            solution_message = f"""🏁 **Complete Solution:**

**Answer:** {question['correct_answer']}

**Explanation:** {question.get('explanation', 'Solution explanation not available.')}

**Concept Focus:** {question.get('concept_focus', 'Key concept practice')}

You can now go back to the quiz and submit your answer! 🎯"""
            
            st.session_state.hint_chat_history.append({
                "role": "assistant", 
                "content": solution_message
            })
            st.rerun()
    
    with col3:
        if st.button("❌ Close Hints", use_container_width=True):
            st.session_state.show_hint_popup = False
            st.rerun()

def generate_interactive_hint(ai_assistant, question, student_input, chat_history, hint_level):
    """Generate an interactive hint based on student input and progression"""
    
    try:
        response = ai_assistant.generate_interactive_hint(
            question=question,
            student_input=student_input,
            hint_level=hint_level,
            subject=st.session_state.selected_subject,
            class_level=st.session_state.selected_class,
            topic=st.session_state.selected_topic
        )
        return response
    except Exception as e:
        return f"🚫 Sorry, I couldn't generate a hint right now. Error: {str(e)}"

def interactive_qa_section():
    """Interactive Q&A chat section"""
    st.subheader("💬 Interactive Q&A Chat")
    st.markdown("Ask any questions about the topic and get instant AI-powered answers!")
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask your question about the topic..."):
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                ai_assistant = AIAssistant(st.session_state.api_key)
                
                response = ai_assistant.answer_question(
                    question=prompt,
                    topic=st.session_state.selected_topic,
                    subject=st.session_state.selected_subject,
                    class_level=st.session_state.selected_class
                )
                
                st.markdown(response)
                
                # Add assistant response to chat history
                st.session_state.chat_history.append({"role": "assistant", "content": response})

def video_learning_section():
    """Video learning section - Shows SINGLE most relevant video"""
    st.subheader("🎥 Video Learning")
    st.markdown("Get the **most relevant educational video** for your current topic!")
    
    # Show current topic context
    st.info(f"📚 **Current Topic:** {st.session_state.selected_topic} ({st.session_state.selected_subject})")
    
    # Single button to find the best video
    if st.button("🎯 Find Best Educational Video", type="primary", use_container_width=True):
        with st.spinner("🔍 Finding the most relevant educational video for you..."):
            try:
                video_recommender = VideoRecommender()
                
                # Get the single best video
                best_video = video_recommender.get_best_educational_video(
                    topic=st.session_state.selected_topic,
                    subject=st.session_state.selected_subject,
                    class_level=st.session_state.selected_class
                )
                
                if best_video:
                    st.session_state['best_video'] = best_video
                    st.success("✅ Found the perfect educational video for you!")
                    st.rerun()
                else:
                    st.error("❌ Could not find educational video. Please check your internet connection.")
                    
            except Exception as e:
                st.error(f"⚠️ Error finding video: {str(e)}")
                
                # Create manual fallback
                topic = st.session_state.selected_topic
                subject = st.session_state.selected_subject
                search_query = f"{topic} {subject} tutorial explanation"
                search_url = f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}"
                
                fallback_video = {
                    'title': f"{topic} - {subject} Educational Tutorial",
                    'url': search_url,
                    'duration': "Educational Content",
                    'views': "Find Best Match",
                    'channel': "YouTube Search",
                    'thumbnail': '',
                    'description': f"Search for the best educational videos about {topic} in {subject}"
                }
                
                st.session_state['best_video'] = fallback_video
                st.info("🔄 Created targeted video search for you!")
                st.rerun()
    
    # Display the best video if found
    if 'best_video' in st.session_state and st.session_state['best_video']:
        video = st.session_state['best_video']
        
        st.markdown("---")
        st.markdown("### 🏆 **Most Relevant Educational Video**")
        
        # Create attractive video display
        with st.container():
            # Video thumbnail and details
            col1, col2 = st.columns([1, 2])
            
            with col1:
                if video.get('thumbnail') and video['thumbnail'].startswith('http'):
                    try:
                        st.image(video['thumbnail'], width=200)
                    except:
                        st.markdown("🎥", help="Educational Video")
                else:
                    # Create a nice video placeholder
                    st.markdown("""
                    <div style='background: linear-gradient(45deg, #FF6B6B, #4ECDC4); 
                                height: 150px; width: 200px; border-radius: 10px; 
                                display: flex; align-items: center; justify-content: center; 
                                color: white; font-size: 30px; margin: 10px 0;'>
                        🎥
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"#### 📹 {video['title']}")
                st.markdown(f"**📺 Channel:** {video.get('channel', 'Educational')}")
                st.markdown(f"**⏱️ Duration:** {video.get('duration', 'Educational Content')}")
                st.markdown(f"**👀 Views:** {video.get('views', 'Educational')}")
                
                if video.get('description'):
                    st.markdown(f"**📄 About:** {video['description'][:100]}...")
        
        # Big prominent watch button
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("▶️ **WATCH THIS VIDEO**", type="primary", use_container_width=True):
                # Record video view in history
                st.session_state.student_history.add_video_view(
                    st.session_state.selected_topic,
                    video['title'],
                    video['url']
                )
                
                # Show video link prominently
                st.success("🔗 **Click the link below to watch the video:**")
                st.markdown(f"""
                <div style='background-color: #e1f5fe; padding: 20px; border-radius: 10px; text-align: center; margin: 10px 0;'>
                    <h3>🎥 Ready to Watch!</h3>
                    <a href='{video['url']}' target='_blank' style='background-color: #ff4444; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 18px;'>
                        ▶️ OPEN VIDEO IN YOUTUBE
                    </a>
                    <p style='margin-top: 15px; color: #666;'>Click the red button above to open the video in a new tab</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Also show as regular link for backup
                st.markdown(f"**Backup Link:** [🎥 {video['title']}]({video['url']})")
        
        # Clear video button
        st.markdown("---")
        if st.button("🗑️ Find Different Video"):
            if 'best_video' in st.session_state:
                del st.session_state['best_video']
            st.rerun()
    
    else:
        # Show helpful guidance when no video is selected
        st.markdown("### 🎯 **How Video Learning Works**")
        
        with st.container():
            st.markdown("""
            1. **🔍 Smart Search** - AI finds the most relevant educational video for your topic
            2. **🏆 Best Match** - Only shows you the highest quality educational content  
            3. **▶️ Direct Access** - Click to watch the video on YouTube
            4. **📊 Progress Tracking** - Your video views are recorded in your learning history
            """)
        
        # Show what topic will be searched
        st.markdown("---")
        st.markdown("### 🎬 **Ready to Find Video For:**")
        
        info_col1, info_col2 = st.columns(2)
        with info_col1:
            st.info(f"**📖 Topic:** {st.session_state.selected_topic}")
        with info_col2:
            st.info(f"**📚 Subject:** {st.session_state.selected_subject}")
        
        st.markdown("**Click the button above to find your perfect educational video!** 🚀")

def mini_quiz_section():
    """Continuous Adaptive Mini Quiz section"""
    st.subheader("🧩 Mini Quiz (Continuous Adaptive)")
    st.markdown("**Keep practicing until you feel confident!** The AI will adapt questions based on your performance.")
    
    # Initialize session state for continuous quiz
    if 'continuous_quiz_active' not in st.session_state:
        st.session_state.continuous_quiz_active = False
        st.session_state.continuous_quiz_difficulty = "easy"
        st.session_state.continuous_quiz_stats = {
            'total_questions': 0,
            'correct_answers': 0,
            'consecutive_correct': 0,
            'consecutive_wrong': 0,
            'question_history': [],
            'last_wrong_concept': None
        }
        st.session_state.current_adaptive_question = None
        st.session_state.show_feedback = False
        st.session_state.last_answer_correct = None
        st.session_state.last_question = None
        st.session_state.last_selected_answer = None
    
    # Display current stats
    if st.session_state.continuous_quiz_active:
        stats = st.session_state.continuous_quiz_stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Questions Answered", stats['total_questions'])
        with col2:
            accuracy = (stats['correct_answers'] / max(stats['total_questions'], 1)) * 100
            st.metric("Accuracy", f"{accuracy:.1f}%")
        with col3:
            st.metric("Current Level", st.session_state.continuous_quiz_difficulty.title())
        with col4:
            st.metric("Streak", f"✅{stats['consecutive_correct']} / ❌{stats['consecutive_wrong']}")
    
    # Start/Continue Quiz Section
    if not st.session_state.continuous_quiz_active:
        # Quiz start section
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if st.button("🚀 Start Continuous Quiz", type="primary", use_container_width=True):
                st.session_state.continuous_quiz_active = True
                st.session_state.show_feedback = False
                st.rerun()
        
        with col2:
            st.markdown("**📚 How it works:**")
            st.markdown("• Answer questions continuously")
            st.markdown("• Get instant feedback")
            st.markdown("• Questions adapt to your level")
            st.markdown("• Move to Final Quiz when ready")
        
    else:
        # Active quiz section
        conduct_continuous_adaptive_quiz()

def conduct_continuous_adaptive_quiz():
    """Conduct the continuous adaptive quiz"""
    
    # Generate new question if needed
    if st.session_state.current_adaptive_question is None and not st.session_state.show_feedback:
        generate_next_adaptive_question()
    
    # Show feedback if answer was just submitted
    if st.session_state.show_feedback:
        display_answer_feedback()
    
    # Show current question if available and no feedback is showing
    elif st.session_state.current_adaptive_question is not None:
        display_current_adaptive_question()
    
    # Always show control buttons
    display_quiz_controls()

def generate_next_adaptive_question():
    """Generate the next adaptive question based on performance"""
    
    with st.spinner(f"🎯 Generating {st.session_state.continuous_quiz_difficulty} question..."):
        try:
            quiz_generator = QuizGenerator(st.session_state.api_key)
            stats = st.session_state.continuous_quiz_stats
            
            # Generate next question
            question = quiz_generator.generate_next_adaptive_question(
                topic=st.session_state.selected_topic,
                subject=st.session_state.selected_subject,
                class_level=st.session_state.selected_class,
                difficulty=st.session_state.continuous_quiz_difficulty,
                previous_wrong_answer=stats.get('last_wrong_concept'),
                question_history=stats.get('question_history', [])
            )
            
            if question:
                st.session_state.current_adaptive_question = question
                # Add to question history
                stats['question_history'].append(question['question'])
                # Keep only last 10 questions in history
                if len(stats['question_history']) > 10:
                    stats['question_history'] = stats['question_history'][-10:]
            else:
                st.error("❌ Could not generate question. Please try again.")
                
        except Exception as e:
            st.error(f"⚠️ Error generating question: {str(e)}")

def display_current_adaptive_question():
    """Display the current adaptive question"""
    
    question = st.session_state.current_adaptive_question
    stats = st.session_state.continuous_quiz_stats
    
    st.markdown("---")
    st.markdown(f"### 📝 Question #{stats['total_questions'] + 1}")
    st.markdown(f"**Difficulty Level:** {st.session_state.continuous_quiz_difficulty.title()}")
    st.markdown("")
    st.markdown(f"**{question['question']}**")
    
    # Answer options
    selected_answer = st.radio(
        "Select your answer:", 
        question['options'], 
        key=f"adaptive_q_{stats['total_questions']}"
    )
    
    # Submit button and Hint button
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("✅ Submit Answer", type="primary"):
            submit_adaptive_answer(selected_answer, question)
    
    with col2:
        if st.button("💡 Get Hint", help="Get interactive hints to solve this question step by step"):
            # Initialize hint system for this question
            st.session_state.show_hint_popup = True
            st.session_state.hint_question_data = question
            st.session_state.hint_chat_history = []
            st.session_state.hint_level = 0
            st.rerun()
    
    # Show hint popup if active
    if st.session_state.show_hint_popup:
        show_hint_popup_dialog()

def submit_adaptive_answer(selected_answer: str, question: Dict):
    """Process the submitted answer"""
    
    stats = st.session_state.continuous_quiz_stats
    is_correct = selected_answer == question['correct_answer']
    
    # Update stats
    stats['total_questions'] += 1
    if is_correct:
        stats['correct_answers'] += 1
        stats['consecutive_correct'] += 1
        stats['consecutive_wrong'] = 0
        stats['last_wrong_concept'] = None
    else:
        stats['consecutive_correct'] = 0
        stats['consecutive_wrong'] += 1
        stats['last_wrong_concept'] = question.get('concept_focus', question['question'])
    
    # Store answer results for feedback
    st.session_state.last_answer_correct = is_correct
    st.session_state.last_question = question
    st.session_state.last_selected_answer = selected_answer
    
    # Update difficulty based on performance
    quiz_generator = QuizGenerator(st.session_state.api_key)
    new_difficulty = quiz_generator.determine_next_difficulty(
        current_difficulty=st.session_state.continuous_quiz_difficulty,
        is_correct=is_correct,
        consecutive_correct=stats['consecutive_correct'],
        consecutive_wrong=stats['consecutive_wrong']
    )
    st.session_state.continuous_quiz_difficulty = new_difficulty
    
    # Show feedback
    st.session_state.show_feedback = True
    st.session_state.current_adaptive_question = None
    
    st.rerun()

def display_answer_feedback():
    """Display feedback for the last answer"""
    
    is_correct = st.session_state.last_answer_correct
    question = st.session_state.last_question
    selected_answer = st.session_state.last_selected_answer
    stats = st.session_state.continuous_quiz_stats
    
    st.markdown("---")
    
    # Show feedback
    if is_correct:
        st.success("🎉 **Correct!** Well done!")
        if stats['consecutive_correct'] >= 2:
            st.info(f"🔥 Great streak! You've got {stats['consecutive_correct']} correct in a row!")
    else:
        st.error("❌ **Incorrect.**")
        st.markdown(f"**Your answer:** {selected_answer}")
        st.markdown(f"**Correct answer:** {question['correct_answer']}")
    
    # Show explanation
    if question.get('explanation'):
        with st.expander("💡 Explanation"):
            st.markdown(question['explanation'])
    
    # Show difficulty change notification
    if stats['consecutive_correct'] >= 2 and st.session_state.continuous_quiz_difficulty != "easy":
        st.info(f"🎯 **Level Up!** Moving to {st.session_state.continuous_quiz_difficulty} questions!")
    elif stats['consecutive_wrong'] >= 2 and st.session_state.continuous_quiz_difficulty != "hard":
        st.info(f"📚 **Adjusting difficulty** to help you learn better!")
    
    # Continue button
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("➡️ Next Question", type="primary"):
            st.session_state.show_feedback = False
            st.rerun()
    
    with col2:
        if not is_correct:
            if st.button("🔄 More Practice on This Concept"):
                # Force a related question on the same concept
                stats['last_wrong_concept'] = question.get('concept_focus', question['question'])
                st.session_state.show_feedback = False
                st.rerun()

def display_quiz_controls():
    """Display quiz control buttons"""
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🏁 I'm Ready for Final Quiz!"):
            st.session_state.continuous_quiz_active = False
            st.session_state.current_adaptive_question = None
            st.session_state.show_feedback = False
            
            # Show final quiz recommendation
            stats = st.session_state.continuous_quiz_stats
            if stats['total_questions'] >= 5:
                accuracy = (stats['correct_answers'] / stats['total_questions']) * 100
                if accuracy >= 70:
                    st.success("🎉 Great job! You're ready for the Final Quiz!")
                    st.info("💡 **Tip:** Click on 'Final Quiz' in the sidebar to take the comprehensive test.")
                else:
                    st.warning("📚 Consider practicing a bit more before taking the Final Quiz.")
                    st.info(f"Current accuracy: {accuracy:.1f}% - Try to get above 70% for better preparation!")
            else:
                st.info("💡 **Tip:** Answer at least 5 questions before moving to the Final Quiz for better preparation!")
            
            st.rerun()
    
    with col2:
        if st.button("🔄 Restart Quiz"):
            # Reset all quiz state
            st.session_state.continuous_quiz_active = False
            st.session_state.continuous_quiz_stats = {
                'total_questions': 0,
                'correct_answers': 0,
                'consecutive_correct': 0,
                'consecutive_wrong': 0,
                'question_history': [],
                'last_wrong_concept': None
            }
            st.session_state.continuous_quiz_difficulty = "easy"
            st.session_state.current_adaptive_question = None
            st.session_state.show_feedback = False
            st.rerun()
    
    with col3:
        if st.button("🏠 Back to Learning Hub"):
            st.session_state.continuous_quiz_active = False
            st.session_state.current_adaptive_question = None
            st.session_state.show_feedback = False
            st.rerun()

def final_quiz_section():
    """Final comprehensive quiz section"""
    st.subheader("📝 Final Comprehensive Quiz")
    st.markdown("Test your complete understanding with a 10-question comprehensive quiz!")
    
    # Initialize final quiz state
    if 'final_quiz_active' not in st.session_state:
        st.session_state.final_quiz_active = False
        st.session_state.final_quiz_questions = []
        st.session_state.final_quiz_answers = {}
        st.session_state.final_quiz_submitted = False
        st.session_state.final_quiz_score = 0
    
    if not st.session_state.final_quiz_active:
        # Quiz start section
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 🎯 **Ready for the Final Challenge?**")
            st.markdown("""
            **What you'll get:**
            - 10 comprehensive questions
            - Mix of easy, medium, and hard difficulty
            - Covers all aspects of the topic
            - Detailed feedback and explanations
            - Performance analytics
            """)
            
            if st.button("🚀 Start Final Quiz", type="primary", use_container_width=True):
                generate_final_quiz()
        
        with col2:
            # Show preparation tips
            st.markdown("### 💡 **Preparation Tips**")
            st.markdown("""
            ✅ Review topic explanation  
            ✅ Complete mini quiz practice  
            ✅ Watch educational videos  
            ✅ Aim for 70%+ score  
            ✅ Take your time to think  
            """)
    
    elif not st.session_state.final_quiz_submitted:
        # Active quiz
        conduct_final_quiz()
    
    else:
        # Show results
        display_final_quiz_results()

def generate_final_quiz():
    """Generate final quiz questions"""
    with st.spinner("🎯 Generating comprehensive final quiz..."):
        try:
            quiz_generator = QuizGenerator(st.session_state.api_key)
            
            questions = quiz_generator.generate_final_quiz(
                topic=st.session_state.selected_topic,
                subject=st.session_state.selected_subject,
                class_level=st.session_state.selected_class
            )
            
            if questions and len(questions) > 0:
                st.session_state.final_quiz_questions = questions
                st.session_state.final_quiz_active = True
                st.session_state.final_quiz_answers = {}
                st.session_state.final_quiz_submitted = False
                st.success("✅ Final quiz generated successfully!")
                st.rerun()
            else:
                st.error("❌ Could not generate quiz questions. Please try again.")
                
        except Exception as e:
            st.error(f"⚠️ Error generating final quiz: {str(e)}")

def conduct_final_quiz():
    """Display and conduct final quiz"""
    questions = st.session_state.final_quiz_questions
    
    st.markdown("### 📝 **Final Comprehensive Quiz**")
    st.markdown(f"**Topic:** {st.session_state.selected_topic}")
    st.markdown("**Instructions:** Answer all 10 questions and submit when ready.")
    
    st.markdown("---")
    
    # Display all questions
    for i, question in enumerate(questions):
        st.markdown(f"#### Question {i+1}")
        st.markdown(f"**{question['question']}**")
        
        # Answer options
        answer_key = f"final_q_{i}"
        selected_answer = st.radio(
            "Select your answer:",
            question['options'],
            key=answer_key,
            index=None
        )
        
        # Store answer
        if selected_answer:
            st.session_state.final_quiz_answers[i] = selected_answer
        
        st.markdown("---")
    
    # Submit button
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        answered_count = len(st.session_state.final_quiz_answers)
        total_questions = len(questions)
        
        if answered_count == total_questions:
            if st.button("✅ Submit Final Quiz", type="primary", use_container_width=True):
                calculate_final_quiz_score()
        else:
            st.warning(f"⚠️ Please answer all questions ({answered_count}/{total_questions} completed)")
            st.button("✅ Submit Final Quiz", disabled=True, use_container_width=True)

def calculate_final_quiz_score():
    """Calculate and store final quiz score"""
    questions = st.session_state.final_quiz_questions
    answers = st.session_state.final_quiz_answers
    
    correct_count = 0
    detailed_results = []
    
    for i, question in enumerate(questions):
        user_answer = answers.get(i, "")
        correct_answer = question['correct_answer']
        is_correct = user_answer == correct_answer
        
        if is_correct:
            correct_count += 1
        
        detailed_results.append({
            'question': question['question'],
            'user_answer': user_answer,
            'correct_answer': correct_answer,
            'is_correct': is_correct,
            'explanation': question.get('explanation', ''),
            'difficulty': question.get('difficulty', 'medium')
        })
    
    # Calculate score
    total_questions = len(questions)
    score_percentage = (correct_count / total_questions) * 100
    
    # Store results
    st.session_state.final_quiz_score = score_percentage
    st.session_state.final_quiz_detailed_results = detailed_results
    st.session_state.final_quiz_submitted = True
    
    # Record in history
    st.session_state.student_history.add_quiz_attempt(
        topic=st.session_state.selected_topic,
        quiz_type="Final Quiz",
        score=score_percentage,
        total_questions=total_questions,
        correct_answers=correct_count
    )
    
    st.rerun()

def display_final_quiz_results():
    """Display final quiz results and feedback"""
    score = st.session_state.final_quiz_score
    results = st.session_state.final_quiz_detailed_results
    
    st.markdown("### 🎊 **Final Quiz Results**")
    
    # Score display
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Your Score", f"{score:.1f}%")
    
    with col2:
        correct_count = sum(1 for r in results if r['is_correct'])
        st.metric("Correct Answers", f"{correct_count}/{len(results)}")
    
    with col3:
        if score >= 80:
            grade = "Excellent! 🏆"
            color = "success"
        elif score >= 70:
            grade = "Good! 👍"
            color = "success"
        elif score >= 60:
            grade = "Fair 📚"
            color = "warning"
        else:
            grade = "Needs Improvement 📖"
            color = "error"
        
        if color == "success":
            st.success(grade)
        elif color == "warning":
            st.warning(grade)
        else:
            st.error(grade)
    
    # Performance feedback
    st.markdown("---")
    
    if score >= 80:
        st.success("🎉 **Outstanding Performance!** You have excellent mastery of this topic!")
    elif score >= 70:
        st.success("👏 **Good Job!** You have a solid understanding of this topic!")
    elif score >= 60:
        st.warning("📚 **Fair Performance.** Consider reviewing the topic and practicing more.")
    else:
        st.error("📖 **Needs Improvement.** Please review the topic materials and try the mini quiz for more practice.")
    
    # Detailed results
    st.markdown("### 📊 **Detailed Results**")
    
    for i, result in enumerate(results):
        with st.expander(f"Question {i+1} - {'✅ Correct' if result['is_correct'] else '❌ Incorrect'}"):
            st.markdown(f"**Question:** {result['question']}")
            st.markdown(f"**Your Answer:** {result['user_answer']}")
            st.markdown(f"**Correct Answer:** {result['correct_answer']}")
            
            if result['explanation']:
                st.markdown(f"**Explanation:** {result['explanation']}")
            
            st.markdown(f"**Difficulty:** {result['difficulty'].title()}")
    
    # Action buttons
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Retake Final Quiz"):
            st.session_state.final_quiz_active = False
            st.session_state.final_quiz_submitted = False
            st.session_state.final_quiz_questions = []
            st.session_state.final_quiz_answers = {}
            st.rerun()
    
    with col2:
        if st.button("🧩 Practice More (Mini Quiz)"):
            # Switch to mini quiz
            st.session_state.final_quiz_active = False
            st.session_state.final_quiz_submitted = False
            st.rerun()
    
    with col3:
        if st.button("🏠 Back to Learning Hub"):
            st.session_state.final_quiz_active = False
            st.session_state.final_quiz_submitted = False
            st.rerun()

def progress_section():
    """Student progress tracking section"""
    st.subheader("📊 My Learning Progress")
    
    history = st.session_state.student_history
    
    # Overview stats
    st.markdown("### 📈 **Overview**")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        topics_studied = len(history.topics_studied)
        st.metric("Topics Studied", topics_studied)
    
    with col2:
        quizzes_taken = len(history.quiz_attempts)
        st.metric("Quizzes Taken", quizzes_taken)
    
    with col3:
        videos_watched = len(history.video_views)
        st.metric("Videos Watched", videos_watched)
    
    with col4:
        if quizzes_taken > 0:
            avg_score = sum(q['score'] for q in history.quiz_attempts) / quizzes_taken
            st.metric("Average Score", f"{avg_score:.1f}%")
        else:
            st.metric("Average Score", "N/A")
    
    # Recent activity
    st.markdown("### 🕒 **Recent Activity**")
    
    if history.topics_studied:
        st.markdown("**Topics Studied:**")
        for topic_data in history.topics_studied[-5:]:  # Last 5 topics
            timestamp = topic_data['timestamp'].strftime("%Y-%m-%d %H:%M")
            st.markdown(f"• {topic_data['topic']} ({topic_data['subject']}) - {timestamp}")
    
    if history.quiz_attempts:
        st.markdown("**Recent Quiz Attempts:**")
        for quiz_data in history.quiz_attempts[-5:]:  # Last 5 quizzes
            timestamp = quiz_data['timestamp'].strftime("%Y-%m-%d %H:%M")
            st.markdown(f"• {quiz_data['topic']} - {quiz_data['score']:.1f}% - {timestamp}")
    
    # Export data buttons
    st.markdown("---")
    st.markdown("### 📥 **Export Learning Reports**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Generate PDF Report", type="primary", use_container_width=True):
            with st.spinner("� Generating PDF report..."):
                try:
                    pdf_data = history.generate_pdf_report(st.session_state.student_name)
                    
                    st.download_button(
                        label="�📥 Download PDF Report",
                        data=pdf_data,
                        file_name=f"learning_report_{st.session_state.student_name}_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                    st.success("✅ PDF report generated successfully!")
                    
                except Exception as e:
                    st.error(f"❌ Error generating PDF: {str(e)}")
    
    with col2:
        if st.button("📊 Export JSON Data", use_container_width=True):
            export_data = {
                'student_name': st.session_state.student_name,
                'topics_studied': [
                    {
                        'topic': t['topic'],
                        'subject': t['subject'],
                        'chapter': t['chapter'],
                        'class': t['class'],
                        'timestamp': t['timestamp'].isoformat()
                    }
                    for t in history.topics_studied
                ],
                'quiz_attempts': [
                    {
                        'topic': q['topic'],
                        'quiz_type': q['quiz_type'],
                        'score': q['score'],
                        'total_questions': q['total_questions'],
                        'correct_answers': q['correct_answers'],
                        'timestamp': q['timestamp'].isoformat()
                    }
                    for q in history.quiz_attempts
                ],
                'video_views': [
                    {
                        'topic': v['topic'],
                        'video_title': v['video_title'],
                        'timestamp': v['timestamp'].isoformat()
                    }
                    for v in history.video_views
                ]
            }
            
            json_data = json.dumps(export_data, indent=2)
            st.download_button(
                label="📥 Download JSON Data",
                data=json_data,
                file_name=f"learning_data_{st.session_state.student_name}_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json",
                use_container_width=True
            )

def main():
    """Main application function"""
    
    # Initialize session state
    initialize_session_state()
    
    # Display appropriate page based on current state
    if st.session_state.current_page == "authentication":
        authentication_page()
    elif st.session_state.current_page == "class_selection":
        class_selection_page()
    elif st.session_state.current_page == "subject_selection":
        subject_selection_page()
    elif st.session_state.current_page == "chapter_selection":
        chapter_selection_page()
    elif st.session_state.current_page == "topic_selection":
        topic_selection_page()
    elif st.session_state.current_page == "learning_hub":
        learning_hub_page()

if __name__ == "__main__":
    main()