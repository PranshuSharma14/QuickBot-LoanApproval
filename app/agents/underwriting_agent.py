"""
Underwriting Agent - Credit evaluation and loan approval logic
"""

from app.agents.base_agent import BaseAgent
from app.models.schemas import ConversationContext, ChatResponse, ChatStage, UnderwritingResult
from app.services.dummy_services import DummyServices
from app.models.schemas import LoanPurpose

INTEREST_RATE_BY_PURPOSE = {
    LoanPurpose.PERSONAL: 12.63,
    LoanPurpose.HOME_IMPROVEMENT: 9.2,
    LoanPurpose.EDUCATION: 8.3,
    LoanPurpose.MEDICAL: 9.0,
    LoanPurpose.BUSINESS: 15.0,
    LoanPurpose.WEDDING: 12.63,
    LoanPurpose.TRAVEL: 12.63,
    LoanPurpose.DEBT_CONSOLIDATION: 17.0,
}

class UnderwritingAgent(BaseAgent):
    """Agent responsible for credit evaluation and loan underwriting"""

    def __init__(self):
        super().__init__("Underwriting Agent")
        self.dummy_services = DummyServices()

    async def process(self, message: str, context: ConversationContext) -> ChatResponse:
        """Process underwriting and make loan decision"""

        if not context.customer_phone:
            return self._generate_response(
                session_id=context.session_id,
                message="Customer verification required before underwriting.",
                stage=ChatStage.VERIFICATION
            )

        # Fetch credit score
        credit_result = await self.dummy_services.get_credit_score(context.customer_phone)
        context.credit_score = credit_result.credit_score

        # Fetch pre-approved limit
        offer_result = await self.dummy_services.get_preapproved_offer(context.customer_phone)
        context.pre_approved_limit = offer_result.pre_approved_limit

        # Apply underwriting rules
        underwriting_result = await self._evaluate_loan(context, offer_result.interest_rate)
        context.underwriting_result = underwriting_result

        return await self._generate_decision_response(context, credit_result, offer_result)

    async def _evaluate_loan(self, context: ConversationContext, base_rate: float) -> UnderwritingResult:
        """Evaluate loan application based on credit rules"""

        loan_amount = context.loan_request.amount
        credit_score = context.credit_score
        pre_approved_limit = context.pre_approved_limit
        tenure = context.loan_request.tenure

        # Rule 1: Credit score < 700 → reject
        if credit_score < 700:
            return UnderwritingResult(
                approved=False,
                loan_amount=loan_amount,
                emi=0,
                interest_rate=base_rate,
                tenure=tenure,
                reason=f"Credit score ({credit_score}) is below our minimum requirement of 700.",
                requires_salary_slip=False
            )

        # Calculate EMI with base rate
        purpose = context.loan_request.purpose
        interest_rate = INTEREST_RATE_BY_PURPOSE.get(purpose, base_rate)
        monthly_rate = interest_rate / (12 * 100)

        emi = loan_amount * monthly_rate * ((1 + monthly_rate) ** tenure) / (((1 + monthly_rate) ** tenure) - 1)

        # Rule 2: Loan amount ≤ pre-approved limit → approve
        if loan_amount <= pre_approved_limit:
            return UnderwritingResult(
                approved=True,
                loan_amount=loan_amount,
                emi=emi,
                interest_rate=interest_rate,
                tenure=tenure,
                reason=f"Loan amount is within your pre-approved limit of ₹{pre_approved_limit:,.0f}.",
                requires_salary_slip=False
            )

        # Rule 3: Loan amount ≤ 2× pre-approved limit → request salary slip
        if loan_amount <= (2 * pre_approved_limit):
            return UnderwritingResult(
                approved=False,
                loan_amount=loan_amount,
                emi=emi,
                interest_rate=interest_rate,
                tenure=tenure,
                reason=f"Loan amount exceeds pre-approved limit. Salary slip verification required.",
                requires_salary_slip=True
            )

        # Rule 4: Loan amount > 2× pre-approved limit → reject
        return UnderwritingResult(
            approved=False,
            loan_amount=loan_amount,
            emi=emi,
            interest_rate=interest_rate,
            tenure=tenure,
            reason=f"Loan amount (₹{loan_amount:,.0f}) exceeds our maximum limit of ₹{2 * pre_approved_limit:,.0f} for your profile.",
            requires_salary_slip=False
        )

    async def _generate_decision_response(self, context: ConversationContext, credit_result, offer_result) -> ChatResponse:
        """Generate response based on underwriting decision"""

        result = context.underwriting_result
        customer_name = context.customer_data.get('name', 'Customer')

        # Format credit score message
        credit_message = f"📊 Credit Score: {credit_result.credit_score} ({credit_result.score_band})\n"
        credit_message += f"💰 Pre-approved Limit: ₹{context.pre_approved_limit:,.0f}\n"
        credit_message += f"💳 Interest Rate: {result.interest_rate}% p.a.\n\n"


        if result.approved:
            # Generate sanction letter immediately upon approval
            sanction_letter_path = None
            try:
                from app.services.pdf_service import PDFService
                pdf_service = PDFService()
                sanction_letter_path = await pdf_service.generate_sanction_letter(
                    customer_data=context.customer_data,
                    loan_details=result,
                    session_id=context.session_id
                )
                pdf_status = "✅ Sanction letter generated and ready for download!"
            except Exception as e:
                print(f"Error generating sanction letter: {e}")
                pdf_status = "⚠️ Sanction letter will be emailed to you shortly."

            # Update loan status in database
            try:
                from app.database.postgres_models import get_postgres_db
                from app.api.dashboard import update_loan_status_internal
                
                db = next(get_postgres_db())
                update_loan_status_internal(
                    db=db,
                    session_id=context.session_id,
                    phone=context.customer_phone,
                    status="approved",
                    loan_amount=float(result.loan_amount),
                    approved_amount=float(result.loan_amount),
                    interest_rate=float(result.interest_rate),
                    tenure_months=result.tenure,
                    emi_amount=float(result.emi),
                    credit_score=credit_result.credit_score,
                    sanction_letter_path=sanction_letter_path
                )
            except Exception as e:
                print(f"Error updating loan status in database: {e}")

            # Calculate comprehensive loan details
            total_repayment = result.emi * result.tenure
            total_interest = total_repayment - result.loan_amount
            processing_fee = result.loan_amount * 0.02  # 2% processing fee
            first_emi_date = "15th of next month"
            loan_account_number = f"QL{context.session_id[:8].upper()}"

            # Build metadata for celebration screen
            loan_metadata = {
                "customer_name": customer_name,
                "loan_amount": result.loan_amount,
                "tenure": result.tenure,
                "interest_rate": result.interest_rate,
                "emi": result.emi,
                "total_interest": total_interest,
                "total_repayment": total_repayment,
                "processing_fee": processing_fee,
                "loan_account_number": loan_account_number,
                "first_emi_date": first_emi_date,
                "credit_score": credit_result.credit_score,
                "score_band": credit_result.score_band,
                "pre_approved_limit": context.pre_approved_limit,
                "purpose": context.loan_request.purpose.value if context.loan_request.purpose else "personal",
                "approved": True
            }

            # Instant approval with comprehensive details
            return self._generate_response(
                session_id=context.session_id,
                message=f"🎉 **LOAN APPROVED - CONGRATULATIONS {customer_name.upper()}!** 🎉\n\n"
                       f"═══════════════════════════════════════\n"
                       f"📊 **CREDIT ASSESSMENT RESULTS**\n"
                       f"═══════════════════════════════════════\n"
                       f"{credit_message}"
                       f"**Approval Reason**: {result.reason}\n\n"
                       f"═══════════════════════════════════════\n"
                       f"💰 **LOAN SANCTION DETAILS**\n"
                       f"═══════════════════════════════════════\n"
                       f"✅ **Principal Amount**: ₹{result.loan_amount:,.0f}\n"
                       f"✅ **Loan Tenure**: {result.tenure} months ({result.tenure//12} years {result.tenure%12} months)\n"
                       f"✅ Loan Purpose: {context.loan_request.purpose.value.replace('_', ' ').title()}\n"
                       f"✅ **Interest Rate**: {result.interest_rate}% per annum (Reducing Balance)\n"
                       f"✅ **Monthly EMI**: ₹{result.emi:,.0f}\n"
                       f"✅ **Total Interest Payable**: ₹{total_interest:,.0f}\n"
                       f"✅ **Total Repayment Amount**: ₹{total_repayment:,.0f}\n"
                       f"✅ **Processing Fee**: ₹{processing_fee:,.0f} (2% of loan amount)\n"
                       f"✅ **First EMI Date**: {first_emi_date}\n"
                       f"✅ **Loan Account Number**: {loan_account_number}\n\n"
                       f"═══════════════════════════════════════\n"
                       f"📋 **TERMS & CONDITIONS**\n"
                       f"═══════════════════════════════════════\n"
                       f"• No prepayment charges after 6 months\n"
                       f"• Late payment charges: ₹500 per delay\n"
                       f"• Loan insurance: Optional (recommended)\n"
                       f"• Auto-debit facility: Mandatory\n"
                       f"• Loan validity: 30 days from sanction date\n\n"
                       f"═══════════════════════════════════════\n"
                       f"📄 **SANCTION LETTER STATUS**\n"
                       f"═══════════════════════════════════════\n"
                       f"{pdf_status}\n"
                       f"**Download**: Click 'Download Letter' button on right →\n\n"
                       f"═══════════════════════════════════════\n"
                       f"🚀 **NEXT STEPS FOR DISBURSEMENT**\n"
                       f"═══════════════════════════════════════\n"
                       f"1. **Download & Sign** your sanction letter\n"
                       f"2. **Upload Documents**: PAN, Aadhaar, Bank Statement (last 3 months)\n"
                       f"3. **E-Sign Agreement**: Digital signing via Aadhaar OTP\n"
                       f"4. **Bank Verification**: Penny drop verification\n"
                       f"5. **Funds Disbursement**: Within 24-48 hours to your account\n\n"
                       f"═══════════════════════════════════════\n"
                       f"📞 **SUPPORT & ASSISTANCE**\n"
                       f"═══════════════════════════════════════\n"
                       f"• Helpline: 1800-123-4567 (Toll-Free)\n"
                       f"• Email: support@quickloan.in\n"
                       f"• WhatsApp: +91-98765-43210\n\n"
                       f"Thank you for choosing QuickLoan! Your financial partner for life. 🙏",
                stage=ChatStage.COMPLETED,
                requires_input=False,
                final=True,
                metadata=loan_metadata
            )

        elif result.requires_salary_slip:
            # Salary slip required
            return self._generate_response(
                session_id=context.session_id,
                message=f"Good news {customer_name}! Your profile looks great! 📈\n\n"
                       f"{credit_message}"
                       f"**Requested Amount**: ₹{result.loan_amount:,.0f}\n"
                       f"**Estimated EMI**: ₹{result.emi:,.0f}\n\n"
                       f"To approve your higher loan amount, I need to verify your current salary. "
                       f"This is just a formality since you have an excellent credit score!\n\n"
                       f"Please upload your latest salary slip (last month's payslip):",
                stage=ChatStage.SALARY_SLIP,
                requires_input=True,
                file_upload=True
            )

        else:
            # Rejection
            rejection_suggestions = self._get_rejection_suggestions(result, context)

            # Update loan status in database to rejected
            try:
                from app.database.postgres_models import get_postgres_db
                from app.api.dashboard import update_loan_status_internal
                
                db = next(get_postgres_db())
                update_loan_status_internal(
                    db=db,
                    session_id=context.session_id,
                    phone=context.customer_phone,
                    status="rejected",
                    loan_amount=float(result.loan_amount) if result.loan_amount else None,
                    credit_score=context.credit_score,
                    rejection_reason=result.reason
                )
            except Exception as e:
                print(f"Error updating loan status in database: {e}")

            return self._generate_response(
                session_id=context.session_id,
                message=f"Thank you for your interest, {customer_name}. 🙏\n\n"
                       f"{credit_message}"
                       f"Unfortunately, we cannot approve your current loan request.\n\n"
                       f"**Reason**: {result.reason}\n\n"
                       f"{rejection_suggestions}\n\n"
                       f"We're always here to help you with your financial needs. "
                       f"Please feel free to reach out once you meet our criteria.",
                stage=ChatStage.REJECTED,
                requires_input=False,
                final=True
            )

    def _get_rejection_suggestions(self, result: UnderwritingResult, context: ConversationContext) -> str:
        """Generate helpful suggestions for rejected applications"""

        suggestions = "**Here's how you can improve your chances:**\n"

        if context.credit_score < 700:
            suggestions += "• ✨ Improve your credit score by paying bills on time\n"
            suggestions += "• ✨ Reduce credit card utilization below 30%\n"
            suggestions += "• ✨ Clear any pending dues or EMIs\n"
            suggestions += f"• ✨ Consider a smaller loan amount (up to ₹{context.pre_approved_limit:,.0f})\n"

        elif result.loan_amount > (2 * context.pre_approved_limit):
            suggestions += f"• ✨ Consider a loan amount up to ₹{2 * context.pre_approved_limit:,.0f}\n"
            suggestions += "• ✨ Build a longer relationship with us for higher limits\n"
            suggestions += "• ✨ Increase your income or add a co-applicant\n"

        suggestions += "• ✨ Try again after 3-6 months\n"
        suggestions += "• ✨ Consider our other financial products"

        return suggestions

    async def process_salary_verification(self, context: ConversationContext, salary: float) -> ChatResponse:
        """Process salary slip verification and make final decision"""

        result = context.underwriting_result

        # Rule: EMI should not exceed 50% of salary
        max_allowed_emi = salary * 0.5

        if result.emi <= max_allowed_emi:
            # Approve after salary verification
            result.approved = True
            result.reason = f"Approved after salary verification. EMI (₹{result.emi:,.0f}) is {(result.emi/salary*100):.1f}% of salary."

            # Generate sanction letter immediately upon approval
            sanction_letter_path = None
            try:
                from app.services.pdf_service import PDFService
                pdf_service = PDFService()
                sanction_letter_path = await pdf_service.generate_sanction_letter(
                    customer_data=context.customer_data,
                    loan_details=result,
                    session_id=context.session_id
                )
                pdf_status = "✅ Sanction letter generated and ready for download!"
            except Exception as e:
                print(f"Error generating sanction letter: {e}")
                pdf_status = "⚠️ Sanction letter will be emailed to you shortly."

            # Update loan status in database
            try:
                from app.database.postgres_models import get_postgres_db
                from app.api.dashboard import update_loan_status_internal
                
                db = next(get_postgres_db())
                update_loan_status_internal(
                    db=db,
                    session_id=context.session_id,
                    phone=context.customer_phone,
                    status="approved",
                    loan_amount=float(result.loan_amount),
                    approved_amount=float(result.loan_amount),
                    interest_rate=float(result.interest_rate),
                    tenure_months=result.tenure,
                    emi_amount=float(result.emi),
                    credit_score=context.credit_score,
                    sanction_letter_path=sanction_letter_path
                )
            except Exception as e:
                print(f"Error updating loan status in database: {e}")

            customer_name = context.customer_data.get('name', 'Customer')

            # Calculate comprehensive loan details
            total_repayment = result.emi * result.tenure
            total_interest = total_repayment - result.loan_amount
            processing_fee = result.loan_amount * 0.02
            disposable_income = salary - result.emi
            loan_account_number = f"QL{context.session_id[:8].upper()}"

            return self._generate_response(
                session_id=context.session_id,
                message=f"🎉 **LOAN APPROVED - CONGRATULATIONS {customer_name.upper()}!** 🎉\n\n"
                       f"═══════════════════════════════════════\n"
                       f"💼 **INCOME VERIFICATION SUCCESSFUL**\n"
                       f"═══════════════════════════════════════\n"
                       f"✅ **Monthly Salary**: ₹{salary:,.0f}\n"
                       f"✅ **EMI to Income Ratio**: {(result.emi/salary*100):.1f}% (Excellent!)\n"
                       f"✅ **Disposable Income**: ₹{disposable_income:,.0f} per month\n"
                       f"✅ **Verification Status**: Completed & Approved\n\n"
                       f"═══════════════════════════════════════\n"
                       f"💰 **LOAN SANCTION DETAILS**\n"
                       f"═══════════════════════════════════════\n"
                       f"✅ **Principal Amount**: ₹{result.loan_amount:,.0f}\n"
                       f"✅ **Loan Tenure**: {result.tenure} months ({result.tenure//12} years {result.tenure%12} months)\n"
                       f"✅ Loan Purpose: {context.loan_request.purpose.value.replace('_', ' ').title()}\n"
                       f"✅ **Interest Rate**: {result.interest_rate}% per annum (Reducing Balance)\n"
                       f"✅ **Monthly EMI**: ₹{result.emi:,.0f}\n"
                       f"✅ **Total Interest Payable**: ₹{total_interest:,.0f}\n"
                       f"✅ **Total Repayment Amount**: ₹{total_repayment:,.0f}\n"
                       f"✅ **Processing Fee**: ₹{processing_fee:,.0f} (2% of loan amount)\n"
                       f"✅ **First EMI Date**: 15th of next month\n"
                       f"✅ **Loan Account Number**: {loan_account_number}\n\n"
                       f"═══════════════════════════════════════\n"
                       f"📋 **TERMS & CONDITIONS**\n"
                       f"═══════════════════════════════════════\n"
                       f"• No prepayment charges after 6 months\n"
                       f"• Late payment charges: ₹500 per delay\n"
                       f"• Loan insurance: Optional (recommended)\n"
                       f"• Auto-debit facility: Mandatory\n"
                       f"• Loan validity: 30 days from sanction date\n\n"
                       f"═══════════════════════════════════════\n"
                       f"📄 **SANCTION LETTER STATUS**\n"
                       f"═══════════════════════════════════════\n"
                       f"{pdf_status}\n"
                       f"**Download**: Click 'Download Letter' button on right →\n\n"
                       f"═══════════════════════════════════════\n"
                       f"🚀 **NEXT STEPS FOR DISBURSEMENT**\n"
                       f"═══════════════════════════════════════\n"
                       f"1. **Download & Sign** your sanction letter\n"
                       f"2. **Upload Documents**: PAN, Aadhaar, Bank Statement (last 3 months)\n"
                       f"3. **E-Sign Agreement**: Digital signing via Aadhaar OTP\n"
                       f"4. **Bank Verification**: Penny drop verification\n"
                       f"5. **Funds Disbursement**: Within 24-48 hours to your account\n\n"
                       f"═══════════════════════════════════════\n"
                       f"📞 **SUPPORT & ASSISTANCE**\n"
                       f"═══════════════════════════════════════\n"
                       f"• Helpline: 1800-123-4567 (Toll-Free)\n"
                       f"• Email: support@quickloan.in\n"
                       f"• WhatsApp: +91-98765-43210\n\n"
                       f"Thank you for choosing QuickLoan! Your financial partner for life. 🙏",
                stage=ChatStage.COMPLETED,
                requires_input=False,
                final=True
            )
        else:
            # Reject due to high EMI
            result.approved = False
            result.reason = f"EMI (₹{result.emi:,.0f}) exceeds 50% of salary (₹{salary:,.0f}). Maximum allowed EMI is ₹{max_allowed_emi:,.0f}."

            # Suggest lower amount
            max_loan_amount = (max_allowed_emi * (((1 + (result.interest_rate / (12 * 100))) ** result.tenure) - 1)) / ((result.interest_rate / (12 * 100)) * ((1 + (result.interest_rate / (12 * 100))) ** result.tenure))

            customer_name = context.customer_data.get('name', 'Customer')

            # Update loan status in database to rejected
            try:
                from app.database.postgres_models import get_postgres_db
                from app.api.dashboard import update_loan_status_internal
                
                db = next(get_postgres_db())
                update_loan_status_internal(
                    db=db,
                    session_id=context.session_id,
                    phone=context.customer_phone,
                    status="rejected",
                    loan_amount=float(result.loan_amount) if result.loan_amount else None,
                    credit_score=context.credit_score,
                    rejection_reason=result.reason
                )
            except Exception as e:
                print(f"Error updating loan status in database: {e}")

            return self._generate_response(
                session_id=context.session_id,
                message=f"Thank you for providing your salary details, {customer_name}.\n\n"
                       f"**Salary Verification**: ₹{salary:,.0f} per month ✅\n\n"
                       f"Unfortunately, the requested EMI (₹{result.emi:,.0f}) would be {(result.emi/salary*100):.1f}% "
                       f"of your salary, which exceeds our policy limit of 50%.\n\n"
                       f"**Alternative Suggestion:**\n"
                       f"I can approve a loan of ₹{max_loan_amount:,.0f} with EMI ₹{max_allowed_emi:,.0f}\n\n"
                       f"Would you like to proceed with this amount, or would you prefer to "
                       f"consider a longer tenure to reduce the EMI?",
                stage=ChatStage.COMPLETED,
                requires_input=False,
                final=True
            )