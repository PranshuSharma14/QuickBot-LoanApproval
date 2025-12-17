"""
AI Helper - Intelligent message understanding and response generation using OpenAI
"""

import os
import re
import json
from typing import Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# Set your OpenAI API key as environment variable or replace with your key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

class AIHelper:
    """AI-powered helper for intelligent conversation handling"""
    
    def __init__(self):
        self.api_key = OPENAI_API_KEY
        self.use_ai = bool(self.api_key)
        
        if self.use_ai:
            try:
                import openai
                self.client = openai.OpenAI(api_key=self.api_key)
                logger.info("OpenAI integration enabled")
            except ImportError:
                logger.warning("OpenAI package not installed. Install with: pip install openai")
                self.use_ai = False
            except Exception as e:
                logger.warning(f"OpenAI initialization failed: {e}")
                self.use_ai = False
        else:
            logger.info("OpenAI API key not set. Using rule-based responses.")
    
    def extract_loan_amount(self, message: str) -> Optional[int]:
        """
        Extract loan amount from natural language using AI or regex
        Examples: "I need 5 lakhs", "50000 rupees", "5L loan"
        """
        
        # Try AI extraction first if available
        if self.use_ai:
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": """You are a financial assistant extracting loan amounts from user messages.

Handle typos and variations:
- 'laksh', 'laks', 'lac' → lakh (100,000)
- 'crore', 'cror', 'cr' → crore (10,000,000)
- '44 laksh' = 44 lakh = 4,400,000
- '5L', '5 l', '5lac' = 5 lakh = 500,000

Return ONLY the numeric amount in rupees (INR). Examples:
- '44 laksh' → 4400000
- 'i need 5 lakh' → 500000
- '2.5 crore' → 25000000
- 'fifty thousand' → 50000

If no amount found, return 'NONE'."""},
                        {"role": "user", "content": message}
                    ],
                    temperature=0,
                    max_tokens=50
                )
                
                result = response.choices[0].message.content.strip()
                if result != "NONE":
                    # Extract numbers from AI response
                    amount = re.sub(r'[^\d]', '', result)
                    if amount:
                        return int(amount)
            except Exception as e:
                logger.debug(f"AI extraction failed, falling back to regex: {e}")
        
        # Fallback: Rule-based extraction
        message_lower = message.lower()
        
        # Pattern 1: "X lakhs" or "X lakh" (including typos like laksh, laks, lac)
        lakh_pattern = r'(\d+(?:\.\d+)?)\s*(?:lakhs?|lacs?|laksh?|laks?|l\b)'
        lakh_match = re.search(lakh_pattern, message_lower)
        if lakh_match:
            return int(float(lakh_match.group(1)) * 100000)
        
        # Pattern 2: "X crores" or "X crore"
        crore_pattern = r'(\d+(?:\.\d+)?)\s*(?:crores?|cr\b)'
        crore_match = re.search(crore_pattern, message_lower)
        if crore_match:
            return int(float(crore_match.group(1)) * 10000000)
        
        # Pattern 3: Direct numbers (₹50000, 50000, 50k, 50K)
        if 'k' in message_lower or 'K' in message:
            k_pattern = r'(\d+)\s*k'
            k_match = re.search(k_pattern, message_lower)
            if k_match:
                return int(k_match.group(1)) * 1000
        
        # Pattern 4: Plain numbers between 10,000 and 50,00,000
        number_pattern = r'\b(\d{5,8})\b'
        number_match = re.search(number_pattern, message)
        if number_match:
            amount = int(number_match.group(1))
            if 10000 <= amount <= 50000000:
                return amount
        
        return None
    
    def extract_tenure(self, message: str) -> Optional[int]:
        """
        Extract loan tenure from natural language
        Examples: "2 years", "24 months", "3 yrs"
        """
        
        if self.use_ai:
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "Extract loan tenure from user message. Convert to months. Return only the number of months. If no tenure found, return 'NONE'."},
                        {"role": "user", "content": message}
                    ],
                    temperature=0,
                    max_tokens=20
                )
                
                result = response.choices[0].message.content.strip()
                if result != "NONE":
                    months = re.sub(r'[^\d]', '', result)
                    if months:
                        return int(months)
            except Exception as e:
                logger.debug(f"AI tenure extraction failed: {e}")
        
        # Fallback: Rule-based
        message_lower = message.lower()
        
        # Years
        year_pattern = r'(\d+)\s*(?:years?|yrs?|y\b)'
        year_match = re.search(year_pattern, message_lower)
        if year_match:
            return int(year_match.group(1)) * 12
        
        # Months
        month_pattern = r'(\d+)\s*(?:months?|mon|m\b)'
        month_match = re.search(month_pattern, message_lower)
        if month_match:
            return int(month_match.group(1))
        
        # Just a number (assume months if between 6-60)
        number_pattern = r'\b(\d+)\b'
        number_match = re.search(number_pattern, message)
        if number_match:
            num = int(number_match.group(1))
            if 6 <= num <= 60:
                return num
        
        return None
    
    def understand_intent(self, message: str, current_stage: str) -> Dict[str, Any]:
        """
        Understand user intent using AI
        Returns: {
            'intent': 'provide_amount' | 'ask_question' | 'greeting' | 'random' | etc,
            'confidence': float,
            'extracted_data': dict
        }
        """
        
        result = {
            'intent': 'unknown',
            'confidence': 0.5,
            'extracted_data': {},
            'is_random': False
        }
        
        # Check if message is gibberish/random
        if self._is_gibberish(message):
            result['intent'] = 'random_gibberish'
            result['is_random'] = True
            result['confidence'] = 0.9
            return result
        
        if self.use_ai:
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": f"""You are analyzing a user message in a loan application chatbot. Current stage: {current_stage}.
Classify the intent as one of:
- provide_loan_amount
- provide_tenure
- provide_phone
- provide_purpose
- ask_question
- greeting
- random_gibberish
- off_topic
- confirmation (yes/no)

Return ONLY a JSON with: {{"intent": "...", "confidence": 0.0-1.0, "reasoning": "..."}}"""},
                        {"role": "user", "content": message}
                    ],
                    temperature=0.3,
                    max_tokens=100
                )
                
                ai_result = response.choices[0].message.content.strip()
                parsed = json.loads(ai_result)
                result.update(parsed)
                
            except Exception as e:
                logger.debug(f"AI intent understanding failed: {e}")
        
        # Fallback rule-based intent detection
        message_lower = message.lower()
        
        # Greeting detection
        greetings = ['hi', 'hello', 'hey', 'good morning', 'good evening', 'namaste']
        if any(g in message_lower for g in greetings) and len(message.split()) <= 3:
            result['intent'] = 'greeting'
            result['confidence'] = 0.9
        
        # Question detection
        question_words = ['what', 'how', 'when', 'where', 'why', 'which', 'can', 'should']
        if any(q in message_lower for q in question_words) or '?' in message:
            result['intent'] = 'ask_question'
            result['confidence'] = 0.8
        
        # Confirmation detection
        if message_lower in ['yes', 'yeah', 'yep', 'ok', 'okay', 'sure', 'no', 'nope', 'nah']:
            result['intent'] = 'confirmation'
            result['confidence'] = 0.95
        
        # Try to extract data
        amount = self.extract_loan_amount(message)
        if amount:
            result['extracted_data']['amount'] = amount
            result['intent'] = 'provide_loan_amount'
            result['confidence'] = 0.85
        
        tenure = self.extract_tenure(message)
        if tenure:
            result['extracted_data']['tenure'] = tenure
            result['intent'] = 'provide_tenure'
            result['confidence'] = 0.85
        
        # Phone number detection
        phone_pattern = r'\b\d{10}\b'
        if re.search(phone_pattern, message):
            result['extracted_data']['phone'] = re.search(phone_pattern, message).group()
            result['intent'] = 'provide_phone'
            result['confidence'] = 0.9
        
        return result
    
    def _is_gibberish(self, message: str) -> bool:
        """Detect if message is random gibberish"""
        
        # Very short random strings
        if len(message) < 3:
            return True
        
        # No vowels (likely random keyboard mashing)
        vowels = set('aeiouAEIOU')
        if not any(c in vowels for c in message):
            return True
        
        # Too many consonants in a row
        consonant_pattern = r'[bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ]{5,}'
        if re.search(consonant_pattern, message):
            return True
        
        # Check if it's a real word or name (basic check)
        words = message.split()
        if len(words) == 1 and len(message) > 3:
            # Single word that's not in common dictionary
            common_words = ['loan', 'amount', 'need', 'want', 'get', 'apply', 'money', 'rupees']
            if not any(word in message.lower() for word in common_words):
                # Could be gibberish
                return True
        
        return False
    
    def generate_contextual_response(
        self, 
        message: str, 
        intent_analysis: Dict[str, Any],
        current_stage: str,
        context_info: Dict[str, Any]
    ) -> str:
        """
        Generate intelligent contextual response
        """
        
        # Handle random/gibberish messages
        if intent_analysis.get('is_random') or intent_analysis['intent'] == 'random_gibberish':
            return self._handle_random_message(current_stage)
        
        # Handle greetings
        if intent_analysis['intent'] == 'greeting':
            return "Hello! 👋 Welcome to QuickLoan! I'm here to help you get a personal loan quickly. How much loan amount do you need?"
        
        # Handle questions
        if intent_analysis['intent'] == 'ask_question':
            return self._handle_question(message, current_stage)
        
        # Handle off-topic
        if intent_analysis['intent'] == 'off_topic':
            return f"I understand you're interested in that, but I'm specifically here to help you with your loan application. {self._get_stage_prompt(current_stage)}"
        
        # Default: Guide back to the flow
        return self._get_stage_prompt(current_stage)
    
    def _handle_random_message(self, current_stage: str) -> str:
        """Handle random/gibberish messages intelligently"""
        
        responses = {
            'sales': "I didn't quite catch that! 😊 Let me help you - how much loan amount do you need? You can say something like '5 lakhs' or '50000'.",
            'verification': "Hmm, that doesn't look like a phone number! 😊 Could you please share your 10-digit mobile number? For example: 9876543210",
            'underwriting': "I'm processing your loan application. Please hold on for a moment...",
            'greeting': "I didn't understand that. Let me start over - I'm here to help you get a personal loan! How much loan amount do you need?"
        }
        
        return responses.get(current_stage, "I didn't understand that. Could you please rephrase?")
    
    def _handle_question(self, message: str, current_stage: str) -> str:
        """Handle user questions with AI or fallback responses"""
        
        if self.use_ai:
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": """You are a helpful loan assistant for QuickLoan India. Answer questions about:
- Loan amounts: ₹10,000 to ₹50,00,000
- Interest rates: 8.3% to 17% based on purpose
- Tenure: 6 to 60 months
- Minimal documentation needed
- Quick approval in minutes
Keep responses brief (2-3 sentences) and guide them to continue the application."""},
                        {"role": "user", "content": message}
                    ],
                    temperature=0.7,
                    max_tokens=150
                )
                
                return response.choices[0].message.content.strip()
            except Exception as e:
                logger.debug(f"AI question answering failed: {e}")
        
        # Fallback responses
        message_lower = message.lower()
        
        if 'interest' in message_lower or 'rate' in message_lower:
            return "Our interest rates range from 8.3% to 17% per annum depending on your loan purpose. Education loans have the lowest rates! 💰 Would you like to continue with your application?"
        
        if 'document' in message_lower:
            return "We need minimal documentation - just your ID proof and income proof. Very simple! 📄 Shall we continue with your loan application?"
        
        if 'eligibility' in message_lower or 'eligible' in message_lower:
            return "You're likely eligible if you have a stable income! Let's check - please share your loan requirement and I'll help you right away. 🎯"
        
        return "That's a great question! Let me help you get your loan first, and I can answer more questions as we go. How much loan amount do you need?"
    
    def _get_stage_prompt(self, stage: str) -> str:
        """Get the appropriate prompt for current stage"""
        
        prompts = {
            'greeting': "How much loan amount do you need?",
            'sales': "Could you please tell me how much loan amount you need? For example: '5 lakhs' or '50000'",
            'verification': "Please share your 10-digit mobile number to proceed.",
            'underwriting': "Please wait while I process your application...",
        }
        
        return prompts.get(stage, "How can I help you with your loan?")
