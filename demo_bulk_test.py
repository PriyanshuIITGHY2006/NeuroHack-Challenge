"""
Bulk Message Generator for MemoryOS Demo
Simulates long conversations to demonstrate 1,000+ turn capability
"""

import requests
import time
import random

# Demo message templates
FILLER_MESSAGES = [
    "What's the weather like?",
    "Tell me a fun fact",
    "How do I make coffee?",
    "What's the capital of France?",
    "Explain quantum physics briefly",
    "Recommend a good book",
    "What's 2+2?",
    "Tell me a joke",
    "What's the latest in AI?",
    "How does blockchain work?",
    "What's the meaning of life?",
    "Explain machine learning",
    "What's the best programming language?",
    "How do I learn Python?",
    "What's cloud computing?",
    "Tell me about neural networks",
    "What's the difference between AI and ML?",
    "How do I stay productive?",
    "What's a good workout routine?",
    "Recommend a movie"
]

def send_message(message, backend_url="http://localhost:8000/chat"):
    """Send a single message to the backend"""
    try:
        response = requests.post(
            backend_url,
            json={"message": message},
            timeout=30
        )
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

def bulk_insert(num_messages=50, delay=0.5, backend_url="http://localhost:8000/chat"):
    """
    Insert multiple messages to simulate conversation drift
    
    Args:
        num_messages: Number of messages to send
        delay: Delay between messages (seconds)
        backend_url: Backend API endpoint
    """
    print(f"🚀 Starting bulk insert: {num_messages} messages")
    print(f"⏱️  Delay: {delay}s between messages")
    print("-" * 50)
    
    for i in range(num_messages):
        message = random.choice(FILLER_MESSAGES)
        print(f"Turn {i+1}/{num_messages}: {message[:50]}...")
        
        result = send_message(message, backend_url)
        
        if result:
            print(f"  ✅ Response received")
        else:
            print(f"  ❌ Failed")
        
        time.sleep(delay)
    
    print("-" * 50)
    print(f"✅ Bulk insert complete! Sent {num_messages} messages")

def run_memory_stress_test(backend_url="http://localhost:8000/chat"):
    """
    Complete stress test scenario for demo
    """
    print("=" * 60)
    print("🧠 MEMORYOS STRESS TEST")
    print("=" * 60)
    
    # Phase 1: Set up initial memories
    print("\n📝 Phase 1: Setting up initial memories...")
    
    initial_messages = [
        "Hi! My name is Alex Chen. I work at TechCorp as a Software Engineer.",
        "My boss is Sarah Johnson. She's the VP of Engineering.",
        "I prefer meetings after 11 AM because I'm not a morning person.",
        "In 2025, I attended the AI Summit in San Francisco.",
        "My favorite programming language is Python."
    ]
    
    for msg in initial_messages:
        print(f"  Sending: {msg[:60]}...")
        send_message(msg, backend_url)
        time.sleep(0.5)
    
    print("  ✅ Initial memories set")
    
    # Phase 2: Insert filler messages
    print("\n🔄 Phase 2: Inserting 50 filler messages (conversation drift)...")
    bulk_insert(num_messages=50, delay=0.3, backend_url=backend_url)
    
    # Phase 3: Test recall
    print("\n🎯 Phase 3: Testing memory recall...")
    
    test_queries = [
        ("What's my boss's name?", "Sarah Johnson"),
        ("What time do I prefer meetings?", "11 AM"),
        ("What conferences did I attend in 2025?", "AI Summit"),
        ("What's my favorite programming language?", "Python"),
        ("Where do I work?", "TechCorp")
    ]
    
    correct = 0
    total = len(test_queries)
    
    for query, expected_keyword in test_queries:
        print(f"\n  Query: {query}")
        result = send_message(query, backend_url)
        
        if result and expected_keyword.lower() in result.get("response", "").lower():
            print(f"  ✅ CORRECT - Found '{expected_keyword}'")
            correct += 1
        else:
            print(f"  ❌ FAILED - Expected '{expected_keyword}'")
            if result:
                print(f"     Got: {result.get('response', '')[:100]}...")
    
    # Results
    print("\n" + "=" * 60)
    print(f"📊 STRESS TEST RESULTS")
    print("=" * 60)
    print(f"Total turns simulated: ~55 turns")
    print(f"Memory recall accuracy: {correct}/{total} ({(correct/total)*100:.1f}%)")
    print(f"Longest recall gap: ~50 turns")
    
    if correct == total:
        print("\n🎉 PERFECT SCORE! All memories recalled correctly!")
    elif correct >= total * 0.8:
        print("\n✅ EXCELLENT! Strong memory performance!")
    else:
        print("\n⚠️  NEEDS IMPROVEMENT - Check threshold settings")
    
    print("=" * 60)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="MemoryOS Bulk Testing Tool")
    parser.add_argument("--mode", choices=["bulk", "stress"], default="stress",
                        help="Test mode: 'bulk' for simple insert, 'stress' for full test")
    parser.add_argument("--messages", type=int, default=50,
                        help="Number of messages for bulk insert")
    parser.add_argument("--delay", type=float, default=0.5,
                        help="Delay between messages (seconds)")
    parser.add_argument("--url", default="http://localhost:8000/chat",
                        help="Backend URL")
    
    args = parser.parse_args()
    
    if args.mode == "bulk":
        bulk_insert(args.messages, args.delay, args.url)
    else:
        run_memory_stress_test(args.url)
