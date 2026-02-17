"""
main.py — FastAPI application for Nexus-AI: Agentic Career Navigator
=====================================================================
All endpoints are thin wrappers around orchestrator_wrapper.py.
No business logic lives here.
"""

import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from db import db
from schemas import (
    OnboardRequest, OnboardResponse,
    ReadinessStartRequest, ReadinessQuestionsResponse,
    ReadinessEvaluateRequest, ReadinessResultResponse,
    ActionQuestionsRequest, ActionQuestionsResponse,
    ActionAssessRequest, ActionAssessResponse,
    RoadmapRegenerateRequest, RoadmapResponse,
    RerouteRequest, RerouteResponse,
    FeedbackRequest, FeedbackResponse,
    HandsOnChatRequest, HandsOnChatResponse,
    DashboardResponse,
)
import orchestrator_wrapper as ow


# ═══════════════════════════════════════════════════════════════════
#  APP STARTUP
# ═══════════════════════════════════════════════════════════════════

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("╔══════════════════════════════════════════╗")
    print("║   Nexus-AI Backend Starting...           ║")
    print("╚══════════════════════════════════════════╝")
    print(f"  MongoDB: {'✓ Connected' if db.available else '✗ Not available'}")
    print(f"  GROQ_API_KEY: {'✓ Set' if os.getenv('GROQ_API_KEY') else '✗ MISSING'}")
    yield
    print("Nexus-AI Backend shutting down.")


app = FastAPI(
    title="Nexus-AI: Agentic Career Navigator",
    description="Production API wrapping the CLI-based career navigation agents.",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS for Next.js frontend
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url, "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ═══════════════════════════════════════════════════════════════════
#  HEALTH CHECK
# ═══════════════════════════════════════════════════════════════════

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "mongo": db.available,
        "groq_key_set": bool(os.getenv("GROQ_API_KEY")),
    }


# ═══════════════════════════════════════════════════════════════════
#  1. ONBOARDING
#  POST /api/onboard
#  Creates user document + triggers market intel generation.
# ═══════════════════════════════════════════════════════════════════

@app.post("/api/onboard", response_model=OnboardResponse)
async def onboard(body: OnboardRequest):
    try:
        result = ow.onboard_user(body.model_dump())
        
        # Ensure response includes all required fields
        exists_flag = result.get("exists", False)
        user_id = result["user_id"]
        profile = result["profile"]
        
        # Sanitize profile: remove sentinel values before returning
        if profile.get("target_role") == "__email_check__":
            profile["target_role"] = ""
        
        return OnboardResponse(
            user_id=user_id,
            message="Existing user found" if exists_flag else "User created successfully",
            profile=profile,
            exists=exists_flag,  # EXPLICIT - must be included!
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════
#  2a. READINESS — GENERATE QUESTIONS
#  POST /api/readiness/start
#  GPT generates 10 questions; cached in memory only.
# ═══════════════════════════════════════════════════════════════════

@app.post("/api/readiness/start", response_model=ReadinessQuestionsResponse)
async def readiness_start(body: ReadinessStartRequest):
    try:
        questions = ow.readiness_start(body.user_id)
        return ReadinessQuestionsResponse(
            user_id=body.user_id,
            questions=questions,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════
#  2b. READINESS — EVALUATE ANSWERS
#  POST /api/readiness/evaluate
#  GPT evaluates answers; only score+summary saved to MongoDB.
# ═══════════════════════════════════════════════════════════════════

@app.post("/api/readiness/evaluate", response_model=ReadinessResultResponse)
async def readiness_evaluate(body: ReadinessEvaluateRequest):
    try:
        result = ow.readiness_evaluate(body.user_id, body.answers)
        return ReadinessResultResponse(
            user_id=body.user_id,
            **result,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════
#  3. DASHBOARD
#  GET /api/dashboard/{user_id}
# ═══════════════════════════════════════════════════════════════════

@app.get("/api/dashboard/{user_id}")
async def dashboard(user_id: str):
    try:
        return ow.get_dashboard(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════
#  4a. ROADMAP — GET CURRENT
#  GET /api/roadmap/{user_id}
# ═══════════════════════════════════════════════════════════════════

@app.get("/api/roadmap/{user_id}", response_model=RoadmapResponse)
async def get_roadmap(user_id: str):
    try:
        result = ow.get_roadmap(user_id)
        return RoadmapResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════
#  4b. ROADMAP — REGENERATE
#  POST /api/roadmap/regenerate
# ═══════════════════════════════════════════════════════════════════

@app.post("/api/roadmap/regenerate", response_model=RoadmapResponse)
async def roadmap_regenerate(body: RoadmapRegenerateRequest):
    try:
        result = ow.regenerate_roadmap(body.user_id, body.target_role)
        return RoadmapResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════
#  5a. ACTION — GET QUESTIONS
#  POST /api/action/questions
#  GPT generates 10 questions; cached in memory only.
# ═══════════════════════════════════════════════════════════════════

@app.post("/api/action/questions", response_model=ActionQuestionsResponse)
async def action_questions(body: ActionQuestionsRequest):
    try:
        result = ow.get_action_questions(body.user_id, body.action_id)
        return ActionQuestionsResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════
#  5b. ACTION — ASSESS
#  POST /api/action/assess
#  Evaluates answers; updates score + confidence in MongoDB.
# ═══════════════════════════════════════════════════════════════════

@app.post("/api/action/assess", response_model=ActionAssessResponse)
async def action_assess(body: ActionAssessRequest):
    try:
        result = ow.assess_action(body.user_id, body.action_id, body.answers)
        return ActionAssessResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════
#  6. MARKET INTELLIGENCE
#  GET /api/market/{user_id}
# ═══════════════════════════════════════════════════════════════════

@app.get("/api/market/{user_id}")
async def market(user_id: str):
    try:
        return ow.get_market(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════
#  7. REROUTING
#  POST /api/reroute
# ═══════════════════════════════════════════════════════════════════

@app.post("/api/reroute", response_model=RerouteResponse)
async def reroute(body: RerouteRequest):
    try:
        result = ow.handle_reroute(body.user_id, body.new_role)
        return RerouteResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════
#  8. FEEDBACK
#  POST /api/feedback
# ═══════════════════════════════════════════════════════════════════

@app.post("/api/feedback", response_model=FeedbackResponse)
async def feedback(body: FeedbackRequest):
    try:
        result = ow.generate_feedback(body.user_id)
        return FeedbackResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════
#  9. HANDS-ON CHAT
#  POST /api/hands-on/chat
# ═══════════════════════════════════════════════════════════════════

@app.post("/api/hands-on/chat", response_model=HandsOnChatResponse)
async def hands_on_chat(body: HandsOnChatRequest):
    try:
        result = ow.hands_on_chat(
            body.user_id,
            body.message,
            body.conversation_history,
        )
        return HandsOnChatResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════
#  10. RESUME SKILL EXTRACTION
#  POST /api/resume/extract-skills
# ═══════════════════════════════════════════════════════════════════

@app.post("/api/resume/extract-skills")
async def extract_resume_skills(body: dict):
    try:
        resume_text = body.get("resume_text", "")
        if not resume_text:
            raise ValueError("resume_text is required")
        
        result = ow.extract_skills_from_resume(resume_text)
        return JSONResponse(content=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════
#  RUN
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
