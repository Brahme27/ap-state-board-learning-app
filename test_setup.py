"""
Test script to verify the AI Learning App setup
Run this to check if all components are working correctly
"""

import sys
import importlib

def test_imports():
    """Test if all required modules can be imported"""
    required_modules = [
        'streamlit',
        'langchain',
        'langchain_openai', 
        'openai',
        'requests',
        'beautifulsoup4',
        'youtubesearchpython'
    ]
    
    print("🧪 Testing module imports...")
    print("=" * 40)
    
    all_good = True
    for module in required_modules:
        try:
            if module == 'beautifulsoup4':
                importlib.import_module('bs4')
                print(f"✅ {module} (bs4) - OK")
            elif module == 'youtubesearchpython':
                importlib.import_module('youtubesearchpython')
                print(f"✅ {module} - OK")
            else:
                importlib.import_module(module)
                print(f"✅ {module} - OK")
        except ImportError as e:
            print(f"❌ {module} - FAILED: {e}")
            all_good = False
    
    print("\n" + "=" * 40)
    if all_good:
        print("🎉 All modules imported successfully!")
        print("✅ Your setup is ready to run the AI Learning App!")
    else:
        print("⚠️  Some modules failed to import.")
        print("📝 Please check the installation instructions.")
    
    return all_good

def test_app_components():
    """Test if app components can be imported"""
    print("\n🔧 Testing app components...")
    print("=" * 40)
    
    try:
        from curriculum_data import get_curriculum_data
        curriculum = get_curriculum_data()
        print(f"✅ Curriculum data loaded - {len(curriculum)} classes available")
        
        from ai_assistant import AIAssistant
        print("✅ AI Assistant module - OK")
        
        from quiz_generator import QuizGenerator
        print("✅ Quiz Generator module - OK")
        
        from video_recommender import VideoRecommender
        print("✅ Video Recommender module - OK")
        
        from student_history import StudentHistory
        print("✅ Student History module - OK")
        
        print("\n🎯 All app components loaded successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Component test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🎓 AI-Powered Student Learning App - Setup Test")
    print("=" * 50)
    print(f"🐍 Python version: {sys.version}")
    print()
    
    # Test imports
    imports_ok = test_imports()
    
    # Test components if imports are OK
    if imports_ok:
        components_ok = test_app_components()
        
        if components_ok:
            print("\n🚀 SETUP COMPLETE!")
            print("=" * 50)
            print("✅ All tests passed!")
            print("🎯 You can now run the app using:")
            print("   • start_app.bat (Windows)")
            print("   • start_app.ps1 (PowerShell)")
            print("   • Or directly: .\\venv\\Scripts\\streamlit.exe run app.py")
            print("\n🔑 Don't forget to have your OpenAI API key ready!")
        else:
            print("\n❌ SETUP INCOMPLETE")
            print("Some components failed to load. Check the error messages above.")
    else:
        print("\n❌ SETUP INCOMPLETE")
        print("Some required modules are missing. Please install them using:")
        print("pip install -r requirements.txt")

if __name__ == "__main__":
    main()
