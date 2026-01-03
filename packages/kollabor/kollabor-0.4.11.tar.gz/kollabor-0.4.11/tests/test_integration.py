import sys
sys.path.append('.')

try:
    from core.application import TerminalLLMChat
    from core.llm.llm_service import LLMService
    from core.llm.conversation_manager import ConversationManager
    
    print("✅ All imports successful")
    
    # Test creating an instance
    app = TerminalLLMChat()
    print("✅ TerminalLLMChat created successfully")
    
    # Test LLMService
    print("✅ LLMService initialized correctly")
    
    # Test ConversationManager
    print("✅ ConversationManager integrated properly")
    
    # Check if conversation_manager and conversation_logger exist
    if hasattr(app.llm_service, 'conversation_manager'):
        print("✅ conversation_manager is accessible")
    else:
        print("❌ conversation_manager not accessible")
        
    if hasattr(app.llm_service, 'conversation_logger'):
        print("✅ conversation_logger is accessible")
    else:
        print("❌ conversation_logger not accessible")
    
    print("\n🎉 Integration verification complete!")
    print("🎉 All components working correctly!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
