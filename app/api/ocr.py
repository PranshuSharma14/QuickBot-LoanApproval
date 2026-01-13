"""
OCR API Endpoints for Document Text Extraction
Extracts Aadhaar and PAN numbers from uploaded documents
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
import os
import re
import logging
import tempfile
import shutil

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ocr", tags=["OCR"])

# Try to import OCR libraries
try:
    from PIL import Image
    import pytesseract
    HAS_TESSERACT = True
    logger.info("✅ Tesseract OCR available")
except ImportError:
    HAS_TESSERACT = False
    logger.warning("⚠️ Tesseract OCR not available - using pattern simulation")

try:
    import pdf2image
    HAS_PDF2IMAGE = True
except ImportError:
    HAS_PDF2IMAGE = False
    logger.warning("⚠️ pdf2image not available - PDF OCR will be limited")


def extract_aadhaar_from_text(text: str) -> str:
    """Extract Aadhaar number from text using regex"""
    # Aadhaar format: 12 digits, often in groups of 4
    # Pattern: XXXX XXXX XXXX or XXXX-XXXX-XXXX or XXXXXXXXXXXX
    patterns = [
        r'\b(\d{4}[\s-]?\d{4}[\s-]?\d{4})\b',  # With spaces or dashes
        r'\b(\d{12})\b',  # Continuous 12 digits
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            # Clean and validate
            clean = re.sub(r'[\s-]', '', match)
            if len(clean) == 12 and clean.isdigit():
                # Basic Aadhaar validation: shouldn't start with 0 or 1
                if clean[0] not in ['0', '1']:
                    return clean
    
    return None


def extract_pan_from_text(text: str) -> str:
    """Extract PAN number from text using regex"""
    # PAN format: AAAAA1234A (5 letters, 4 digits, 1 letter)
    pattern = r'\b([A-Z]{5}[0-9]{4}[A-Z]{1})\b'
    
    # Search in uppercase version of text
    matches = re.findall(pattern, text.upper())
    
    for match in matches:
        # Validate PAN structure
        # 4th character indicates type: C=Company, P=Person, H=HUF, F=Firm, etc.
        if match[3] in ['A', 'B', 'C', 'F', 'G', 'H', 'J', 'L', 'P', 'T']:
            return match
    
    return None


def simulate_ocr_extraction(document_type: str, filename: str) -> dict:
    """
    Simulate OCR extraction when actual OCR is not available.
    In production, this would use actual OCR libraries.
    """
    # For demo purposes, we'll return a message indicating OCR is not available
    # In a real scenario, you would process the actual document
    return {
        "success": False,
        "message": "OCR library not available. Please enter the number manually.",
        "extracted_number": None,
        "confidence": 0
    }


async def perform_ocr_on_image(image_path: str) -> str:
    """Perform OCR on an image file"""
    if not HAS_TESSERACT:
        return ""
    
    try:
        image = Image.open(image_path)
        # Use Tesseract with Indian language support if available
        text = pytesseract.image_to_string(image, lang='eng')
        return text
    except Exception as e:
        logger.error(f"OCR error: {e}")
        return ""


async def perform_ocr_on_pdf(pdf_path: str) -> str:
    """Perform OCR on a PDF file"""
    if not HAS_PDF2IMAGE or not HAS_TESSERACT:
        return ""
    
    try:
        # Convert PDF to images
        images = pdf2image.convert_from_path(pdf_path)
        
        # OCR each page
        full_text = ""
        for image in images:
            text = pytesseract.image_to_string(image, lang='eng')
            full_text += text + "\n"
        
        return full_text
    except Exception as e:
        logger.error(f"PDF OCR error: {e}")
        return ""


@router.post("/extract")
async def extract_document_number(
    file: UploadFile = File(...),
    document_type: str = Form(...)
):
    """
    Extract Aadhaar or PAN number from uploaded document.
    
    Args:
        file: Uploaded document (PDF, JPG, PNG)
        document_type: 'aadhaar' or 'pan'
    
    Returns:
        Extracted number if found
    """
    if document_type not in ['aadhaar', 'pan']:
        raise HTTPException(status_code=400, detail="Invalid document type. Use 'aadhaar' or 'pan'")
    
    # Validate file type
    allowed_types = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png']
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type. Upload PDF, JPG, or PNG")
    
    # Check if OCR is available
    if not HAS_TESSERACT:
        return JSONResponse(content={
            "success": False,
            "message": "OCR service not available. Please enter the number manually.",
            "extracted_number": None,
            "confidence": 0,
            "document_type": document_type
        })
    
    # Save file temporarily
    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, file.filename)
    
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Perform OCR based on file type
        if file.content_type == 'application/pdf':
            text = await perform_ocr_on_pdf(temp_path)
        else:
            text = await perform_ocr_on_image(temp_path)
        
        if not text:
            return JSONResponse(content={
                "success": False,
                "message": "Could not extract text from document. Please enter manually.",
                "extracted_number": None,
                "confidence": 0,
                "document_type": document_type
            })
        
        # Extract the number based on document type
        if document_type == 'aadhaar':
            extracted = extract_aadhaar_from_text(text)
        else:
            extracted = extract_pan_from_text(text)
        
        if extracted:
            return JSONResponse(content={
                "success": True,
                "message": f"{document_type.upper()} number extracted successfully",
                "extracted_number": extracted,
                "confidence": 0.85,
                "document_type": document_type
            })
        else:
            return JSONResponse(content={
                "success": False,
                "message": f"Could not find valid {document_type.upper()} number in document. Please enter manually.",
                "extracted_number": None,
                "confidence": 0,
                "document_type": document_type
            })
    
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        return JSONResponse(content={
            "success": False,
            "message": "Error processing document. Please enter the number manually.",
            "extracted_number": None,
            "confidence": 0,
            "document_type": document_type
        })
    
    finally:
        # Cleanup temp files
        try:
            shutil.rmtree(temp_dir)
        except:
            pass


@router.get("/status")
async def ocr_status():
    """Check OCR service availability"""
    return {
        "tesseract_available": HAS_TESSERACT,
        "pdf_support": HAS_PDF2IMAGE,
        "status": "ready" if HAS_TESSERACT else "limited"
    }
