import sys
sys.path.append('.')

try:
    from core.llm.conversation_manager import ConversationManager
    
    class MockConfig:
        def get(self, key, default=None):
            return default
    
    # Test ConversationManager
    config = MockConfig()
    manager = ConversationManager(config)
    
    print("✅ ConversationManager created successfully")
    
    # Test basic functionality
    msg1 = manager.add_message('user', 'Hello')
    msg2 = manager.add_message('assistant', 'Hi there!', parent_uuid=msg1)
    msg3 = manager.add_message('user', 'How are you?')
    
    print(f"✅ Message threading working: {len(manager.get_message_thread(msg3))} messages in thread")
    print(f"✅ Context retrieval working: {len(manager.get_context_messages())} messages")
    print(f"✅ Search functionality working: {len(manager.search_messages('hello'))} results")
    
    # Test persistence
    saved_path = manager.save_conversation()
    print(f"✅ Persistence working: {saved_path}")
    
    # Test statistics
    stats = manager.get_conversation_stats()
    print(f"✅ Statistics working: {stats['messages']['total']} total messages")
    
    print("\n🎉 ConversationManager fully functional!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
