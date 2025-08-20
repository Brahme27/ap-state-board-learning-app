"""
AI-Powered Student Learning App
Designed for AP State Board Syllabus (Classes 1-10)
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
    
    if st.button("🎯 Generate Explanation", type="primary"):
        with st.spinner("🤖 AI is preparing your lesson..."):
            ai_assistant = AIAssistant(st.session_state.api_key)
            
            explanation = ai_assistant.generate_topic_explanation(
                topic=st.session_state.selected_topic,
                subject=st.session_state.selected_subject,
                class_level=st.session_state.selected_class
            )
            
            st.markdown("### 📚 Lesson Content")
            st.markdown(explanation)
            
            # Record this study session
            st.session_state.student_history.add_topic_studied(
                st.session_state.selected_class,
                st.session_state.selected_subject,
                st.session_state.selected_chapter,
                st.session_state.selected_topic
            )

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
    """Video learning section"""
    st.subheader("🎥 Video Learning")
    st.markdown("Watch curated educational videos to reinforce your learning!")
    
    if st.button("🔍 Find Educational Videos", type="primary"):
        with st.spinner("🎬 Searching for the best educational videos..."):
            video_recommender = VideoRecommender()
            
            videos = video_recommender.search_educational_videos(
                topic=st.session_state.selected_topic,
                subject=st.session_state.selected_subject,
                class_level=st.session_state.selected_class
            )
            
            if videos:
                st.markdown("### 📺 Recommended Videos")
                
                for i, video in enumerate(videos[:3]):  # Show top 3 videos
                    with st.container():
                        col1, col2 = st.columns([1, 2])
                        
                        with col1:
                            st.image(video.get('thumbnail', ''), width=200)
                        
                        with col2:
                            st.markdown(f"**{video['title']}**")
                            st.markdown(f"Duration: {video.get('duration', 'N/A')}")
                            st.markdown(f"Channel: {video.get('channel', 'N/A')}")
                            
                            if st.button(f"▶️ Watch Video {i+1}", key=f"video_{i}"):
                                st.markdown(f"[🔗 Open Video]({video['url']})")
                        
                        st.markdown("---")
            else:
                st.warning("😔 No videos found. Try a different topic or check your internet connection.")

def mini_quiz_section():
    """Adaptive mini quiz section"""
    st.subheader("🧩 Mini Quiz (Adaptive)")
    st.markdown("Test your understanding with adaptive difficulty!")
    
    if 'mini_quiz_started' not in st.session_state:
        st.session_state.mini_quiz_started = False
        st.session_state.mini_quiz_score = 0
        st.session_state.mini_quiz_difficulty = "easy"
        st.session_state.mini_quiz_questions = []
        st.session_state.mini_quiz_current = 0
    
    if not st.session_state.mini_quiz_started:
        if st.button("🚀 Start Mini Quiz", type="primary"):
            st.session_state.mini_quiz_started = True
            st.rerun()
    else:
        conduct_mini_quiz()

def conduct_mini_quiz():
    """Conduct the adaptive mini quiz"""
    quiz_generator = QuizGenerator(st.session_state.api_key)
    
    # Generate questions if not already generated
    if not st.session_state.mini_quiz_questions:
        with st.spinner(f"🎯 Generating {st.session_state.mini_quiz_difficulty} questions..."):
            questions = quiz_generator.generate_adaptive_quiz(
                topic=st.session_state.selected_topic,
                subject=st.session_state.selected_subject,
                class_level=st.session_state.selected_class,
                difficulty=st.session_state.mini_quiz_difficulty,
                num_questions=3
            )
            st.session_state.mini_quiz_questions = questions
    
    # Display current question
    if st.session_state.mini_quiz_current < len(st.session_state.mini_quiz_questions):
        current_q = st.session_state.mini_quiz_questions[st.session_state.mini_quiz_current]
        
        st.markdown(f"**Question {st.session_state.mini_quiz_current + 1}/3** ({st.session_state.mini_quiz_difficulty.title()})")
        st.markdown(f"**{current_q['question']}**")
        
        # Answer options
        selected_answer = st.radio("Select your answer:", current_q['options'], key=f"mini_q_{st.session_state.mini_quiz_current}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✅ Submit Answer"):
                if selected_answer == current_q['correct_answer']:
                    st.success("🎉 Correct!")
                    st.session_state.mini_quiz_score += 1
                else:
                    st.error(f"❌ Incorrect. The correct answer is: {current_q['correct_answer']}")
                
                st.session_state.mini_quiz_current += 1
                
                # Check if we need to adjust difficulty
                if st.session_state.mini_quiz_current == 3:
                    if st.session_state.mini_quiz_score >= 2:  # Good performance
                        if st.session_state.mini_quiz_difficulty == "easy":
                            st.session_state.mini_quiz_difficulty = "medium"
                            st.session_state.mini_quiz_questions = []
                            st.session_state.mini_quiz_current = 0
                            st.info("🎯 Great job! Moving to medium difficulty...")
                        elif st.session_state.mini_quiz_difficulty == "medium":
                            st.session_state.mini_quiz_difficulty = "hard"
                            st.session_state.mini_quiz_questions = []
                            st.session_state.mini_quiz_current = 0
                            st.info("🔥 Excellent! Moving to hard difficulty...")
                        else:
                            st.success("🏆 Outstanding! You've mastered this topic!")
                            st.session_state.mini_quiz_started = False
                    else:
                        st.info("📚 Keep practicing! You can try again.")
                        st.session_state.mini_quiz_started = False
                
                st.rerun()
        
        with col2:
            if st.button("🔄 Restart Quiz"):
                st.session_state.mini_quiz_started = False
                st.session_state.mini_quiz_questions = []
                st.rerun()

def final_quiz_section():
    """Final quiz section"""
    st.subheader("📝 Final Quiz")
    st.markdown("Take a comprehensive 10-question quiz to test your mastery!")
    
    if 'final_quiz_started' not in st.session_state:
        st.session_state.final_quiz_started = False
        st.session_state.final_quiz_questions = []
        st.session_state.final_quiz_current = 0
        st.session_state.final_quiz_score = 0
        st.session_state.final_quiz_answers = []
    
    if not st.session_state.final_quiz_started:
        if st.button("🎯 Start Final Quiz", type="primary"):
            with st.spinner("📝 Generating 10 unique questions..."):
                quiz_generator = QuizGenerator(st.session_state.api_key)
                
                questions = quiz_generator.generate_final_quiz(
                    topic=st.session_state.selected_topic,
                    subject=st.session_state.selected_subject,
                    class_level=st.session_state.selected_class
                )
                
                st.session_state.final_quiz_questions = questions
                st.session_state.final_quiz_started = True
                st.rerun()
    else:
        conduct_final_quiz()

def conduct_final_quiz():
    """Conduct the final quiz"""
    if st.session_state.final_quiz_current < len(st.session_state.final_quiz_questions):
        current_q = st.session_state.final_quiz_questions[st.session_state.final_quiz_current]
        
        st.markdown(f"**Question {st.session_state.final_quiz_current + 1}/10**")
        st.markdown(f"**{current_q['question']}**")
        
        selected_answer = st.radio("Select your answer:", current_q['options'], 
                                 key=f"final_q_{st.session_state.final_quiz_current}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("➡️ Next Question"):
                is_correct = selected_answer == current_q['correct_answer']
                
                st.session_state.final_quiz_answers.append({
                    'question': current_q['question'],
                    'selected': selected_answer,
                    'correct': current_q['correct_answer'],
                    'is_correct': is_correct
                })
                
                if is_correct:
                    st.session_state.final_quiz_score += 1
                
                st.session_state.final_quiz_current += 1
                st.rerun()
        
        with col2:
            if st.button("🔄 Restart Quiz"):
                st.session_state.final_quiz_started = False
                st.session_state.final_quiz_questions = []
                st.session_state.final_quiz_current = 0
                st.session_state.final_quiz_score = 0
                st.session_state.final_quiz_answers = []
                st.rerun()
    
    else:
        # Quiz completed - show results
        show_final_quiz_results()

def show_final_quiz_results():
    """Show final quiz results"""
    score_percentage = (st.session_state.final_quiz_score / 10) * 100
    
    st.markdown("## 🎊 Quiz Completed!")
    st.markdown(f"### Your Score: {st.session_state.final_quiz_score}/10 ({score_percentage:.1f}%)")
    
    # Performance feedback
    if score_percentage >= 80:
        st.success("🏆 Excellent! You have mastered this topic!")
    elif score_percentage >= 60:
        st.info("👍 Good job! Keep practicing to improve further.")
    else:
        st.warning("📚 Keep studying! Review the topic and try again.")
    
    # Record quiz result
    st.session_state.student_history.add_quiz_result(
        st.session_state.selected_class,
        st.session_state.selected_subject,
        st.session_state.selected_topic,
        st.session_state.final_quiz_score,
        10,
        "final"
    )
    
    # Show detailed results
    with st.expander("📊 Detailed Results"):
        for i, answer in enumerate(st.session_state.final_quiz_answers):
            if answer['is_correct']:
                st.success(f"Q{i+1}: ✅ Correct")
            else:
                st.error(f"Q{i+1}: ❌ Your answer: {answer['selected']} | Correct: {answer['correct']}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Retake Quiz"):
            st.session_state.final_quiz_started = False
            st.session_state.final_quiz_questions = []
            st.session_state.final_quiz_current = 0
            st.session_state.final_quiz_score = 0
            st.session_state.final_quiz_answers = []
            st.rerun()
    
    with col2:
        if st.button("📚 Study Another Topic"):
            st.session_state.current_page = "topic_selection"
            st.session_state.selected_topic = None
            # Reset quiz state
            st.session_state.final_quiz_started = False
            st.session_state.final_quiz_questions = []
            st.session_state.final_quiz_current = 0
            st.session_state.final_quiz_score = 0
            st.session_state.final_quiz_answers = []
            st.rerun()

def progress_section():
    """Student progress and history section"""
    st.subheader("📊 My Learning Progress")
    
    history = st.session_state.student_history
    
    # Stats overview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📚 Topics Studied", len(history.topics_studied))
    
    with col2:
        st.metric("📝 Quizzes Taken", len(history.quiz_results))
    
    with col3:
        if history.quiz_results:
            avg_score = sum(result['score'] for result in history.quiz_results) / len(history.quiz_results)
            st.metric("📈 Average Score", f"{avg_score:.1f}/10")
    
    # Download progress report
    if st.button("📥 Download Progress Report", type="primary"):
        report_content = history.generate_progress_report(st.session_state.student_name)
        st.download_button(
            label="💾 Save Report",
            data=report_content,
            file_name=f"{st.session_state.student_name}_learning_report_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain"
        )
    
    # Recent activities
    st.markdown("### 📈 Recent Activities")
    
    if history.topics_studied:
        st.markdown("**📚 Recently Studied:**")
        for topic in history.topics_studied[-5:]:  # Last 5 topics
            st.markdown(f"- {topic['topic']} ({topic['subject']} - {topic['class']})")
    
    if history.quiz_results:
        st.markdown("**📝 Recent Quiz Results:**")
        for result in history.quiz_results[-5:]:  # Last 5 quizzes
            score_pct = (result['score'] / result['total']) * 100
            st.markdown(f"- {result['topic']}: {result['score']}/{result['total']} ({score_pct:.1f}%)")

def main():
    """Main application function"""
    initialize_session_state()
    
    # Navigation based on current page
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
