"""PassiveLiveness API - Cloud-ready deployment for passive liveness detection.

DEPLOYMENT NOTES:
- Accepts multipart/form-data with key 'file' (image JPG/PNG)
- Returns JSON with prediction, spoof_score, confidence, risk_level, etc.
- Supports Render.com, AWS, GCP, Azure cloud platforms
- Environment variables: GEMINI_API_KEY (optional for AI explanations)
- Port: 10000 (or PORT environment variable)
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import time
from datetime import datetime
import logging
import os
from model import LivenessAnalyzer

# Load environment variables from .env file (optional, for local development)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, use system environment variables

# Configure logging - production-safe
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def generate_ai_explanation(prediction: str, spoof_score: float) -> str:
    """Generate AI-powered explanation using Google Gemini API.
    
    PRODUCTION NOTES:
    - Requires GEMINI_API_KEY environment variable
    - Falls back gracefully if API unavailable
    - Returns None if API key not configured (UI will hide section)
    - Timeout: 10 seconds to prevent hanging
    
    Args:
        prediction: "REAL", "SPOOF", or "UNCERTAIN"
        spoof_score: Probability score (0-1)
    
    Returns:
        str: AI-generated explanation, or None if unavailable
    """
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.debug("GEMINI_API_KEY not configured, skipping AI explanation")
            return None
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""Analyze this liveness detection result and provide a professional, concise explanation:
        
Prediction: {prediction}
Spoof Score: {spoof_score:.3f}

Explain the image authenticity, mention artifacts if spoofed, recommend actions if uncertain. Keep it security-focused and non-overconfident. Max 100 words."""
        
        response = model.generate_content(prompt, request_options={"timeout": 10})
        explanation = response.text.strip() if response.text else None
        
        if explanation:
            logger.debug(f"Gemini explanation generated: {explanation[:80]}...")
        
        return explanation
        
    except Exception as e:
        logger.warning(f"Gemini API unavailable: {type(e).__name__}: {str(e)[:100]}")
        return None


# Initialize FastAPI app
app = FastAPI(
    title="PassiveLiveness API",
    description="Image-based Passive Liveness & Spoof Detection System",
    version="1.0.0"
)

# CORS Configuration - Allow frontend to call the API
# PRODUCTION SECURITY: Restrict to specific frontend domains
# Get allowed origins from environment variable, default to all ("*") if not set
cors_allowed_origins = os.getenv("CORS_ALLOWED_ORIGINS", "*").split(",")
cors_allowed_origins = [origin.strip() for origin in cors_allowed_origins if origin.strip()]

if not cors_allowed_origins:
    cors_allowed_origins = ["*"]  # Fallback to all origins if empty

logger.info(f"CORS allowed origins: {cors_allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_allowed_origins,  # In production, restrict to specific frontend domains
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Global analyzer instance
analyzer = None

@app.on_event("startup")
async def startup_event():
    """Initialize the analyzer on startup.
    
    DEPLOYMENT: This runs once when the server starts.
    Loads model.pth and prepares the detection pipeline.
    """
    global analyzer
    try:
        logger.info("Starting PassiveLiveness API...")
        logger.info("Initializing LivenessAnalyzer...")
        analyzer = LivenessAnalyzer()
        logger.info("✓ LivenessAnalyzer initialized successfully")
        logger.info("✓ Model loaded and ready for analysis")
    except Exception as e:
        logger.critical(f"Failed to initialize analyzer: {e}", exc_info=True)
        raise


@app.get("/health", tags=["Health"])
async def health_check():
    """System health check endpoint for deployment monitoring.
    
    Returns:
        status: "healthy" or "unhealthy"
        timestamp: ISO format server time
        version: API version
        model_loaded: Whether model initialized successfully
    
    DEPLOYMENT: Use this endpoint to monitor API health on cloud platforms.
    """
    try:
        health_status = {
            "status": "healthy" if analyzer is not None else "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "model_loaded": analyzer is not None
        }
        return health_status
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=False)
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "error": str(e)
        }


@app.post("/analyze", tags=["Analysis"])
async def analyze_image(file: UploadFile = File(...)):
    """Analyze image for passive liveness/spoof detection.
    
    DEPLOYMENT:
    - Accepts: multipart/form-data with key 'file'
    - Supported: JPEG, PNG images
    - Returns: JSON with prediction, scores, and explanations
    - Timeout: ~30 seconds per image
    
    Args:
        file: Image file (JPG or PNG)
    
    Returns:
        JSON with:
        - prediction: "REAL" or "SPOOF" or "UNCERTAIN" or "ERROR"
        - spoof_score: Probability score (0-1)
        - confidence: Confidence percentage
        - explanations: List of human-readable reasons
        - ai_explanation: AI-generated explanation from Gemini (if available)
        - image_hash: SHA256 hash of image
    
    Example usage:
        curl -X POST -F "file=@image.jpg" http://localhost:10000/analyze
    """
    # Check if analyzer is initialized
    if analyzer is None:
        logger.error("Analyzer not initialized")
        raise HTTPException(status_code=500, detail="System not ready. Analyzer not initialized.")
    
    try:
        # Input validation
        if file.filename is None:
            logger.warning("Received request without filename")
            raise HTTPException(status_code=400, detail="No filename provided")
        
        content_type = file.content_type or "unknown"
        if content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
            logger.warning(f"Unsupported content type: {content_type}")
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {content_type}. Only JPEG and PNG allowed."
            )
        
        # Read and validate file
        logger.info(f"Processing image: {file.filename}")
        start_time = time.time()
        
        image_bytes = await file.read()
        
        if len(image_bytes) == 0:
            logger.warning("Received empty file")
            raise HTTPException(status_code=400, detail="Empty file provided")
        
        # Run analysis
        result = analyzer.analyze(image_bytes)
        
        # Generate AI explanation when API is available
        ai_explanation = generate_ai_explanation(result['prediction'], result['spoof_score'])
        if ai_explanation:
            result["ai_explanation"] = ai_explanation
        
        inference_time = time.time() - start_time
        
        # Add metadata to response
        result["filename"] = file.filename
        result["file_size_bytes"] = len(image_bytes)
        result["inference_time_seconds"] = round(inference_time, 3)
        result["timestamp"] = datetime.now().isoformat()
        
        logger.info(f"✓ Analysis complete: {result['prediction']} (confidence: {result['confidence']}%, score: {result['spoof_score']:.3f})")
        
        return JSONResponse(status_code=200, content=result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during analysis: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail="Internal server error - analysis failed. Check server logs for details."
        )


@app.get("/", tags=["Info"])
async def root():
    """API information endpoint"""
    return {
        "name": "PassiveLiveness API",
        "description": "Image-based Passive Liveness & Spoof Detection System",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "analyze": "/analyze",
            "docs": "/docs"
        }
    }


@app.get("/docs-custom", tags=["Info"])
async def custom_docs():
    """Custom documentation"""
    return {
        "title": "PassiveLiveness API Documentation",
        "endpoints": [
            {
                "method": "POST",
                "path": "/analyze",
                "description": "Analyze image for spoof detection",
                "parameters": {
                    "file": "Image file (JPG/PNG, max 10000x10000 pixels)"
                },
                "response": {
                    "prediction": "REAL or SPOOF or UNCERTAIN or ERROR",
                    "spoof_score": "0.0-1.0",
                    "confidence": "0-100%",
                    "explanations": "Array of reasons",
                    "ai_explanation": "AI-generated explanation from Gemini",
                    "image_hash": "SHA256 hash",
                    "inference_time_seconds": "Processing time"
                }
            },
            {
                "method": "GET",
                "path": "/health",
                "description": "Check system health",
                "response": {
                    "status": "System status",
                    "model_loaded": "True/False"
                }
            }
        ]
    }


# ============================================================================
# DEPLOYMENT CONFIGURATION
# ============================================================================
# For Render.com deployment:
# - Root directory: ./backend
# - Build command: pip install -r requirements.txt
# - Start command: uvicorn main:app --host 0.0.0.0 --port 10000
# - Environment: Set GEMINI_API_KEY in Render dashboard
#
# For other cloud platforms (AWS, GCP, Azure):
# - Ensure model.pth is included in deployment
# - Set PORT environment variable if needed
# - Configure CORS origins for security
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    # Use environment variable for port, default to 10000 for cloud
    port = int(os.getenv("PORT", 10000))
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable reload in production
        log_level="info"
    )
