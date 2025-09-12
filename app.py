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
from user_preferences import learning_preferences_survey, get_user_preferences, create_user_profile_summary

# Page configuration
st.set_page_config(
    page_title="🎓 AI Learning Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configure MathJax for LaTeX rendering
st.markdown("""
<script>
    window.MathJax = {
        tex: {
            inlineMath: [['$', '$']],
            displayMath: [['$$', '$$']],
            processEscapes: true,
            processEnvironments: true,
            packages: ['base', 'ams', 'noerrors', 'noundefined', 'autoload', 'physics'],
            macros: {
                // Improved fraction macro
                "frac": ["\\frac{#1}{#2}", 2],
                // Vector notation
                "vec": ["\\boldsymbol{\\mathbf{#1}}", 1],
                // Derivative
                "dv": ["\\frac{d#1}{d#2}", 2],
                // Partial derivative
                "pdv": ["\\frac{\\partial #1}{\\partial #2}", 2]
            }
        },
        options: {
            ignoreHtmlClass: 'tex2jax_ignore',
            processHtmlClass: 'tex2jax_process',
            renderActions: {
                findScript: [10, function (doc) {
                    document.querySelectorAll('script[type^="math/tex"]').forEach(function(node) {
                        var display = !!node.type.match(/; *mode=display/);
                        var math = new doc.options.MathItem(node.textContent, doc.inputJax[0], display);
                        var text = document.createTextNode('');
                        node.parentNode.replaceChild(text, node);
                        math.start = {node: text, delim: '', n: 0};
                        math.end = {node: text, delim: '', n: 0};
                        doc.math.push(math);
                    });
                }, '']
            }
        },
        svg: {
            fontCache: 'global',
            scale: 1.1,
            minScale: 0.5
        },
        loader: {
            load: ['[tex]/physics']
        },
        startup: {
            typeset: true
        }
    };
</script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
""", unsafe_allow_html=True)

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
    if 'survey_data' not in st.session_state:
        st.session_state.survey_data = {}
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
    
    # Hint system session state
    if 'show_hint_popup' not in st.session_state:
        st.session_state.show_hint_popup = False
    if 'hint_chat_history' not in st.session_state:
        st.session_state.hint_chat_history = []
    if 'current_hint_question' not in st.session_state:
        st.session_state.current_hint_question = None
    if 'hint_level' not in st.session_state:
        st.session_state.hint_level = 0

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
                st.session_state.current_page = "preferences_survey"
                st.rerun()
            else:
                st.error("⚠️ Please provide both your name and OpenAI API key.")

def preferences_survey_page():
    """Learning preferences survey page"""
    st.title(f"👋 Welcome {st.session_state.student_name}!")
    st.subheader("🎯 Let's Personalize Your Learning Experience")
    
    learning_preferences_survey()
    
    # Add a "Continue" button if preferences have been saved
    if st.session_state.get('survey_data'):
        if st.button("▶️ Continue to Class Selection", type="primary"):
            st.session_state.current_page = "class_selection"
            st.rerun()

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
    
    # Custom CSS for red buttons
    st.markdown("""
    <style>
    .stButton > button[kind="primary"] {
        background-color: #ff4b4b !important;
        color: white !important;
        border: none !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #ff3030 !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create two columns for the main button and popup button
    col1, col2 = st.columns([3, 1])
    
    with col1:
        generate_explanation = st.button("🎯 Generate Explanation", type="primary")
    
    with col2:
        open_qa_popup = st.button("🤖 AI Assistant", type="primary", help="Ask questions about this topic in a popup")
    
    # Handle explanation generation
    if generate_explanation:
        with st.spinner("🤖 AI is preparing your personalized lesson..."):
            ai_assistant = AIAssistant(st.session_state.api_key)
            
            # Get user preferences if available
            user_preferences = get_user_preferences()
            
            # Check if current subject requires LaTeX formatting
            is_math_science = st.session_state.selected_subject.lower() in [
                'mathematics', 'math', 'maths', 
                'physical science', 'physics', 'science', 'physical sciences'
            ]
            
            # Show that personalization and LaTeX formatting are being applied
            if user_preferences:
                st.info("🎯 Applying your learning preferences to create a personalized explanation...")
            if is_math_science:
                st.info("📐 Enabling LaTeX formatting for mathematical and scientific notation...")
            
            # Generate the explanation
            explanation = ai_assistant.generate_topic_explanation(
                topic=st.session_state.selected_topic,
                subject=st.session_state.selected_subject,
                class_level=st.session_state.selected_class,
                user_preferences=user_preferences
            )
            
            if is_math_science:
                # Add LaTeX formatting guide and validation section
                latex_guide = """
### 📐 Mathematical & Scientific Notation Guide

This lesson uses LaTeX formatting for precise mathematical and scientific notation:

- **Display Equations**: Centered, larger formulas use double dollar signs:
  $$formula$$

- **Inline Math**: Mathematical expressions within text use single dollar signs:
  $formula$

- **Units & Dimensions**: All units are properly formatted:
  - $m/s^2$ for acceleration
  - $kg$ for mass
  - $N$ for force
  - $J$ for energy
  - $W$ for power

- **Common Notation**:
  - Fractions: $$\\frac{numerator}{denominator}$$
  - Powers: $x^2$, $y^3$
  - Square roots: $$\\sqrt{x}$$
  - Greek letters: $\\alpha$, $\\beta$, $\\theta$
  - Vectors: $$\\vec{F}$$
  - Derivatives: $$\\frac{d}{dx}$$
  - Integrals: $$\\int_{a}^{b}$$

---
"""
                # Add the LaTeX guide after the main content
                explanation = f"{explanation}\n\n{latex_guide}"
            
            # Store explanation in session state
            st.session_state.current_explanation = explanation
            
            # Show success messages
            if user_preferences:
                st.success("✅ Explanation personalized based on your learning preferences!")
            if is_math_science:
                st.success("📐 LaTeX formatting enabled for mathematical and scientific notation!")
            
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
        
        # Check if current subject requires LaTeX formatting
        is_math_science = st.session_state.selected_subject.lower() in [
            'mathematics', 'math', 'maths', 
            'physical science', 'physics', 'science', 'physical sciences'
        ]
        
        if is_math_science:
            # Add enhanced LaTeX styling
            st.markdown("""
            <style>
                /* Enhanced LaTeX/MathJax styling */
                .math-content {
                    background-color: #f8f9fa;
                    padding: 15px;
                    border-radius: 8px;
                    margin: 10px 0;
                }
                
                /* Display equations */
                .katex-display {
                    margin: 1.5em 0 !important;
                    padding: 10px !important;
                    background-color: #f0f8ff !important;
                    border-radius: 8px !important;
                    border-left: 4px solid #0066cc !important;
                    overflow-x: auto !important;
                }
                
                /* Enhanced fraction display */
                .katex-display .mfrac {
                    margin: 0 0.2em !important;
                }
                
                .katex-display .mfrac .frac-line {
                    border-color: #0066cc !important;
                }
                
                .katex-display .mfrac .mspace {
                    margin-top: 0.1em !important;
                    margin-bottom: 0.1em !important;
                }
                
                /* Better spacing for numerators and denominators */
                .katex .mfrac .mspace {
                    margin-top: 0.1em !important;
                    margin-bottom: 0.1em !important;
                }
                
                /* Inline math */
                .katex {
                    font-size: 1.1em !important;
                    color: #0066cc !important;
                }
                
                /* Better fraction sizing for inline math */
                .katex .mfrac {
                    vertical-align: -0.5em !important;
                }
                
                /* Improved fraction line */
                .katex .frac-line {
                    min-height: 1px !important;
                    border-bottom-width: 1px !important;
                }
                
                /* Step-by-step solutions */
                .math-step {
                    background-color: #e9ecef;
                    padding: 10px;
                    margin: 5px 0;
                    border-radius: 5px;
                    border-left: 3px solid #6c757d;
                }
                
                /* Scientific units */
                .math-units {
                    color: #28a745;
                    font-style: italic;
                }
                
                /* Important formulas */
                .important-formula {
                    background-color: #fff3cd;
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 8px;
                    border-left: 4px solid #ffc107;
                }
            </style>
            """, unsafe_allow_html=True)
            
            # Add LaTeX rendering info with examples
            st.info("""
            💡 **Mathematical & Scientific Notation**:
            - Display equations are centered and boxed (e.g., $$F = ma$$)
            - Inline math is highlighted (e.g., $E = mc^2$)
            - Units are properly formatted (e.g., $m/s^2$, $kg$)
            - Step-by-step solutions are clearly structured
            """)
        
        # Create a container for the content with proper styling
        with st.container():
            if is_math_science:
                st.markdown('<div class="math-content">', unsafe_allow_html=True)
                st.markdown(st.session_state.current_explanation, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Force MathJax to re-render
                st.markdown("""
                <script>
                    if (window.MathJax) {
                        window.MathJax.typesetPromise && window.MathJax.typesetPromise();
                    }
                </script>
                """, unsafe_allow_html=True)
            else:
                # Standard rendering for non-math subjects
                st.markdown(st.session_state.current_explanation, unsafe_allow_html=True)
    
    # Handle Q&A popup
    if open_qa_popup:
        st.session_state.show_qa_popup = True
    
    # Initialize popup state if not exists
    if 'show_qa_popup' not in st.session_state:
        st.session_state.show_qa_popup = False
    
    # Show Q&A popup dialog
    if st.session_state.show_qa_popup:
        show_qa_popup_dialog()

@st.dialog("🤖 AI Assistant", width="large")
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

@st.dialog("💡 AI Tutor - Question Hint", width="large")
def show_hint_popup_dialog():
    """Popup dialog for interactive hints about the current quiz question"""
    
    # Initialize hint chat history if not exists
    if 'hint_chat_history' not in st.session_state:
        st.session_state.hint_chat_history = []
    
    question = st.session_state.current_hint_question
    
    # Display current question info
    st.markdown("**📝 Question:**")
    st.markdown(f"*{question['question']}*")
    st.markdown("---")
    
    # Display hint chat history in a container with max height
    chat_container = st.container(height=300)
    with chat_container:
        if not st.session_state.hint_chat_history:
            # Generate initial hint using AI based on the specific question
            with st.spinner("🤔 Generating your first hint..."):
                ai_assistant = AIAssistant(st.session_state.api_key)
                
                # Generate first hint for this specific question
                first_hint = ai_assistant.generate_interactive_hint(
                    question=question,
                    student_input="",  # Empty for first hint
                    hint_level=1,  # First hint level
                    subject=st.session_state.selected_subject,
                    class_level=st.session_state.selected_class,
                    topic=st.session_state.selected_topic
                )
                
                st.session_state.hint_chat_history.append({"role": "assistant", "content": first_hint})
                st.session_state.hint_level = 1  # Set initial hint level
            
            # Display the first hint
            with st.chat_message("assistant"):
                st.markdown(first_hint)
        else:
            for message in st.session_state.hint_chat_history:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
    
    # Chat input for hints
    hint_prompt = st.chat_input("Share your thoughts or ask for the next hint...", key="hint_chat_input")
    
    if hint_prompt:
        # Add user message to hint chat history
        st.session_state.hint_chat_history.append({"role": "user", "content": hint_prompt})
        
        # Generate AI hint response
        with st.spinner("🤔 Generating next hint..."):
            ai_assistant = AIAssistant(st.session_state.api_key)
            
            # Increment hint level for next progressive hint
            st.session_state.hint_level += 1
            
            response = ai_assistant.generate_interactive_hint(
                question=question,
                student_input=hint_prompt,
                hint_level=st.session_state.hint_level,
                subject=st.session_state.selected_subject,
                class_level=st.session_state.selected_class,
                topic=st.session_state.selected_topic
            )
            
            # Add assistant response to hint chat history
            st.session_state.hint_chat_history.append({"role": "assistant", "content": response})
        
        st.rerun()
    
    # Control buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🗑️ Clear Hints", use_container_width=True):
            st.session_state.hint_chat_history = []
            st.session_state.hint_level = 0
            st.rerun()
    
    with col2:
        if st.button("🎯 Show Answer", use_container_width=True):
            # Show the complete answer as final hint
            final_hint = f"""🎯 **Complete Answer:**

**Correct Answer:** {question['correct_answer']}

**Explanation:** {question.get('explanation', 'This is the correct answer for this question.')}

**Concept Focus:** {question.get('concept_focus', 'Understanding the key concept in this question.')}

Now that you know the answer, make sure you understand the reasoning behind it! 🧠"""
            
            st.session_state.hint_chat_history.append({"role": "assistant", "content": final_hint})
            st.rerun()
    
    with col3:
        if st.button("❌ Close", use_container_width=True):
            st.session_state.show_hint_popup = False
            st.rerun()

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
    
    # Question with hint button
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.markdown(f"**{question['question']}**")
    
    with col2:
        if st.button("💡 Hint", use_container_width=True):
            st.session_state.show_hint_popup = True
            st.session_state.current_hint_question = question
            st.session_state.hint_level = 0
            st.session_state.hint_chat_history = []
            st.rerun()
    
    # Answer options
    selected_answer = st.radio(
        "Select your answer:", 
        question['options'], 
        key=f"adaptive_q_{stats['total_questions']}"
    )
    
    # Submit button only
    if st.button("✅ Submit Answer", type="primary", use_container_width=True):
        submit_adaptive_answer(selected_answer, question)
    
    # Show hint popup if requested
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
            with st.spinner("📄 Generating PDF report..."):
                try:
                    pdf_data = history.generate_pdf_report(st.session_state.student_name)
                    
                    st.download_button(
                        label="📥 Download PDF Report",
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
    elif st.session_state.current_page == "preferences_survey":
        preferences_survey_page()
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