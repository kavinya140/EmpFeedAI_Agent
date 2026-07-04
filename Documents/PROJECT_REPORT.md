# Employee Feedback Agent — Project Report

## 1. Introduction

The **Employee Feedback Agent** is an AI-powered HR platform designed to collect, analyze, and act on employee feedback. It addresses a critical HR challenge: gathering honest employee input and transforming unstructured feedback into actionable insights.

## 2. Problem Statement

Organizations struggle to:
- Collect feedback at scale without survey fatigue
- Analyze open-text feedback efficiently
- Identify sentiment trends across departments
- Generate actionable HR recommendations from raw feedback

## 3. Solution Overview

Our solution uses:
- **Groq LLM (LLaMA 3.3-70B)** for intelligent feedback analysis
- **MongoDB** for persistent feedback storage
- **ChromaDB** for semantic vector search (RAG)
- **FastAPI** backend with **HTML/CSS/JS** frontend
- **Docker** for containerized deployment

## 4. Prompt Engineering Strategy

| Technique | Application |
|:----------|:------------|
| System Role | HR Analyst persona with empathy and objectivity |
| Few-Shot Examples | 2 annotated feedback examples guide output format |
| Chain-of-Thought | 7-step analysis process before JSON generation |
| Output Schema | Strict JSON with sentiment, themes, urgency, actions |
| RAG Context | Retrieved feedback injected into HR chat prompts |
| Temperature Tuning | Low (0.2) for analysis, higher (0.5) for reports |

## 5. Architecture

```
Employee → Web UI → FastAPI → [MongoDB + ChromaDB]
                              ↓
                         Groq LLM API
                              ↓
                    Sentiment + Themes + Actions
                              ↓
                    HR Dashboard + Reports
```

## 6. Key Features Demonstrated

1. **Feedback Submission** with instant AI analysis
2. **HR Analytics Dashboard** with sentiment metrics
3. **Semantic Search** across all feedback
4. **AI Chat Agent** for HR questions
5. **Executive Report Generation**

## 7. Deployment

Deployed using Docker Compose with MongoDB. See DEPLOYMENT.md for cloud options (Railway, Render, AWS).

## 8. Conclusion

The Employee Feedback Agent demonstrates practical application of LLM technology, prompt engineering, and modern full-stack development for HR use cases.
