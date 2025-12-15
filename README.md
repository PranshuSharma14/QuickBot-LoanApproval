# Agentic AI Loan Sales Assistant - NBFC Backend

A complete web-based Agentic AI Loan Sales Assistant for an Indian Non-Banking Financial Company (NBFC) built with Python FastAPI and multi-agent architecture.

## 🎯 Business Goal

Increase personal loan sales through a web chatbot that behaves like a human loan sales executive and completes the entire loan journey in one chat session.

## 🏗️ Architecture

**Agentic AI System** - Not a simple chatbot, but a sophisticated multi-agent system:

- **Master Agent**: Orchestrates conversation flow and manages context
- **Sales Agent**: Collects loan requirements and negotiates like a human sales executive  
- **Verification Agent**: Validates KYC using dummy CRM API
- **Underwriting Agent**: Performs credit evaluation and loan approval logic
- **Sanction Letter Agent**: Generates PDF sanction letters upon approval

## 🔥 Key Features

- ✅ Complete loan journey in one chat session
- ✅ Human-like conversation flow with persuasive sales techniques
- ✅ Automated credit evaluation and instant decision making
- ✅ PDF sanction letter generation
- ✅ Intelligent handling of edge cases (rejections, salary verification)
- ✅ RESTful APIs for all external service integrations

## 🛡️ Compliance & Privacy

- **Synthetic Data Only**: Uses 10 dummy customers with fake information
- **No Real Data**: No real customer information or actual credit scores
- **RBI Compliance**: Simulated approach for regulatory compliance
- **Mock APIs**: All external integrations are dummy/mock implementations

## 📊 Loan Processing Workflow

```
1. User opens chatbot
2. Master Agent greets and starts conversation  
3. Sales Agent collects and negotiates loan details
4. Verification Agent validates KYC via dummy CRM
5. Underwriting Agent evaluates eligibility:
   • Credit score < 700 → Reject
   • Loan ≤ pre-approved limit → Approve  
   • Loan ≤ 2× limit → Request salary slip
   • EMI > 50% salary → Reject, otherwise approve
6. Generate PDF sanction letter if approved
7. Complete conversation gracefully
```

## 🔧 Tech Stack

- **Backend**: Python 3.8+ with FastAPI
- **Database**: SQLite with dummy customer data
- **PDF Generation**: ReportLab for professional sanction letters
- **Data Validation**: Pydantic models
- **Server**: Uvicorn ASGI server

## 📁 Project Structure

```
NBFC/
├── app/
│   ├── agents/           # AI agent implementations
│   │   ├── base_agent.py
│   │   ├── master_agent.py
│   │   ├── sales_agent.py
│   │   ├── verification_agent.py
│   │   └── underwriting_agent.py
│   ├── api/              # FastAPI route handlers
│   │   ├── chat.py
│   │   └── dummy_apis.py
│   ├── database/         # Database models and setup
│   │   └── database.py
│   ├── models/           # Pydantic schemas
│   │   └── schemas.py
│   ├── services/         # Business logic services
│   │   ├── dummy_services.py
│   │   └── pdf_service.py
│   └── utils/            # Utility functions
├── uploads/              # Uploaded salary slips
├── generated/            # Generated sanction letters
├── main.py               # FastAPI application entry point
└── requirements.txt      # Python dependencies
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Quick Start

1. **Clone and navigate to project**
   ```bash
   cd NBFC
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

4. **Access the application**
   - API Server: http://127.0.0.1:8000
   - API Documentation: http://127.0.0.1:8000/docs
   - Health Check: http://127.0.0.1:8000

## 🌐 API Endpoints

### Core Chat API
- `POST /api/chat` - Main chat interface (handled by Master Agent)

### Dummy External APIs
- `POST /api/crm/verify` - Customer verification (dummy CRM)
- `GET /api/credit-score/{phone}` - Credit score lookup (mock credit bureau)
- `GET /api/offer/preapproved/{phone}` - Pre-approved offers (mock offer engine)
- `POST /api/upload/salary-slip` - Salary slip upload and processing

### Utility Endpoints
- `GET /api/dummy-data/customers` - List all dummy customers for testing
- `GET /` - Health check and API status

## 🧪 Testing the System

### Dummy Customer Data
Use these phone numbers for testing (all are pre-loaded):

| Phone | Name | Monthly Salary | Expected Credit Score |
|-------|------|---------------|----------------------|
| 9876543210 | Rajesh Kumar | ₹75,000 | 750-850 (Excellent) |
| 9876543211 | Priya Sharma | ₹45,000 | 700-749 (Good) |
| 9876543212 | Amit Patel | ₹95,000 | 750-850 (Excellent) |
| 9876543213 | Sneha Reddy | ₹35,000 | 650-699 (Fair) |
| 9876543214 | Vikram Singh | ₹120,000 | 750-850 (Excellent) |

### Test Scenarios

**1. Instant Approval Flow**
```json
POST /api/chat
{
  "message": "I need a loan of 200000 for 24 months for personal use",
  "phone": "9876543210"
}
```

**2. Salary Slip Required Flow**  
```json
POST /api/chat
{
  "message": "I need 800000 rupees for 36 months for home improvement", 
  "phone": "9876543212"
}
```

**3. Credit Score Rejection**
```json
POST /api/chat
{
  "message": "I want 300000 loan for 12 months",
  "phone": "9876543213" 
}
```

## 🎭 Agent Behavior Examples

### Sales Agent Negotiation
- Persuades customers on loan amount and tenure
- Suggests optimal EMI structures  
- Handles objections professionally
- Uses sales techniques like urgency and benefit highlighting

### Master Agent Orchestration
- Maintains conversation context across agents
- Smooth handoffs between different stages
- Intelligent routing based on conversation state
- Graceful error handling and recovery

### Underwriting Agent Intelligence
- Real-time credit evaluation
- Dynamic interest rate calculation
- Risk-based decision making
- Alternative suggestions for rejections

## 📄 Document Generation

The system generates professional PDF sanction letters with:
- Company letterhead and compliance details
- Customer and loan information
- Terms and conditions
- Required documents checklist
- Digital signature placeholders

## 🔍 Edge Cases Handled

- **Low Credit Score**: Polite rejection with improvement suggestions
- **High Loan Amount**: Smart negotiation for realistic amounts
- **Salary Verification**: Seamless salary slip upload flow
- **EMI Affordability**: Income-based EMI calculations
- **Invalid Inputs**: Graceful error handling with helpful guidance

## 🛠️ Development Notes

### Adding New Agents
1. Inherit from `BaseAgent` class
2. Implement `process()` method
3. Register with `MasterAgent`
4. Add to conversation flow logic

### Customizing Underwriting Rules  
Modify `UnderwritingAgent._evaluate_loan()` method to:
- Change credit score thresholds
- Adjust pre-approval multipliers
- Update EMI-to-income ratios
- Add new decision criteria

### Database Modifications
- Update `database.py` models for schema changes
- Modify `dummy_services.py` for new business logic
- Add migrations for production deployment

## 🚨 Important Disclaimers

1. **Demo Purpose Only**: This is a demonstration system with synthetic data
2. **No Real Transactions**: No actual loans are processed or money disbursed  
3. **Fake Customer Data**: All customer information is computer-generated
4. **Mock Credit Scores**: Credit scores are simulated, not from real bureaus
5. **Educational Use**: Intended for learning AI agent architecture and NBFC workflows

## 🤝 Contributing

This is a demonstration project showcasing agentic AI architecture for financial services. Feel free to:
- Extend the agent capabilities
- Add new loan products
- Improve conversation flows
- Enhance security features

## 📞 Support

For questions about the implementation or agentic AI concepts, please refer to the code comments and documentation within the source files.

---

**Built with ❤️ for demonstrating Agentic AI in Indian Financial Services**