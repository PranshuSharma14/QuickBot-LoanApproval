# Agentic AI Loan Sales Assistant - NBFC

This project implements a complete web-based Agentic AI Loan Sales Assistant for an Indian Non-Banking Financial Company (NBFC).

## Project Overview
- **Backend**: Python FastAPI with agent orchestration
- **Frontend**: React + Tailwind CSS (to be implemented)
- **Database**: SQLite with dummy customer data
- **Architecture**: Multi-agent system with Master Agent controlling Worker Agents

## Agents Implementation
1. **Master Agent**: Manages conversation flow and orchestrates other agents
2. **Sales Agent**: Collects loan requirements and negotiates terms
3. **Verification Agent**: Validates KYC using dummy CRM API
4. **Underwriting Agent**: Credit evaluation and loan approval logic
5. **Sanction Letter Agent**: Generates PDF sanction letters

## Compliance & Privacy
- Uses synthetic customer data only
- No real customer information or credit scores
- RBI compliance through simulated data approach
- All APIs are mock/dummy implementations

## Key Features
- Complete loan journey in one chat session
- Human-like conversation flow
- Automated credit evaluation
- PDF sanction letter generation
- Edge case handling (rejections, salary slip verification)

## Tech Stack
- Python 3.8+
- FastAPI
- SQLite
- ReportLab (PDF generation)
- Pydantic (data validation)
- Uvicorn (ASGI server)