#!/usr/bin/env python3
"""
Test script for AI message classification functionality
"""

import sys
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from app.services.ai_service import MessageClassifier, EnhancedAIService
from app.models.schemas import AIRequest

def test_message_classification():
    """Test the message classification functionality"""

    # Test messages
    test_messages = [
        "What projects have you worked on?",
        "Show me your experience with Python",
        "Find certificates related to AWS",
        "Tell me about your work experience",
        "Update my portfolio information",
        "Hello, how are you?",
        "Search for React projects",
        "What technologies do you use?",
        "Display my certificates",
        "Can you help me with something?"
    ]

    print("🧠 Testing Message Classification")
    print("=" * 50)

    classifier = MessageClassifier()
    ai_service = EnhancedAIService()

    for i, message in enumerate(test_messages, 1):
        print(f"\n📝 Test {i}: '{message}'")

        # Test classification
        classification = classifier.classify_message(message)
        print(f"   Type: {classification.message_type}")
        print(f"   Intent: {classification.intent}")
        print(f"   Confidence: {classification.confidence:.2f}")
        print(f"   Keywords: {classification.keywords}")

        # Test full AI processing
        ai_request = AIRequest(message=message)
        ai_response = ai_service.process_request(ai_request)
        print(f"   AI Response: {ai_response.response[:100]}...")

    print("\n✅ Message classification testing completed!")

if __name__ == "__main__":
    test_message_classification()
