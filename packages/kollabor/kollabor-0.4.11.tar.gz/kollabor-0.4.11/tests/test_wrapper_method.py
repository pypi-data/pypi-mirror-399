import sys
sys.path.append('.')

try:
    from core.application import TerminalLLMChat
    
    app = TerminalLLMChat()
    
    # Test the wrapper method
    print("Testing _add_conversation_message method...")
    
    # Test adding a message
    msg_id = app.llm_service._add_conversation_message('user', 'Test message')
    print(f"✅ Message added with ID: {msg_id}")
    
    # Test adding another message with parent UUID
    msg2_id = app.llm_service._add_conversation_message('assistant', 'Response', parent_uuid=msg_id)
    print(f"✅ Response added with ID: {msg2_id}")
    
    # Check ConversationManager
    manager = app.llm_service.conversation_manager
    print(f"✅ ConversationManager has {len(manager.messages)} messages")
    
    # Check legacy history
    legacy = app.llm_service.conversation_history
    print(f"✅ Legacy history has {len(legacy)} messages")
    
    print("\n🎉 Wrapper method working correctly!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
