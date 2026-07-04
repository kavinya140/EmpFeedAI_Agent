"""Seed sample feedback data for demo purposes."""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.mongodb import connect_mongodb, close_mongodb
from app.services.feedback_service import submit_feedback

SAMPLE_FEEDBACK = [
    ("Engineering", "The flexible remote work policy is great, but our CI/CD pipeline is slow and causes frustration during releases."),
    ("Sales", "Management is very supportive and targets are realistic. Would love more training on new product features."),
    ("HR", "Onboarding was confusing — nobody explained the benefits package. Need a clearer checklist for new hires."),
    ("Marketing", "Love the creative freedom here! Team collaboration tools could be better integrated."),
    ("Operations", "Workload has increased significantly without additional headcount. Burnout is becoming a concern."),
    ("Engineering", "My manager takes credit for my work sometimes. This is affecting my motivation and mental health."),
    ("Sales", "Commission structure changed without proper communication. Very demotivating."),
    ("General", "Company culture is positive overall. The annual town halls are informative and transparent."),
]


async def seed():
    await connect_mongodb()
    print("Seeding sample feedback...")
    for dept, text in SAMPLE_FEEDBACK:
        result = await submit_feedback(text, department=dept, is_anonymous=True)
        print(f"  ✓ [{dept}] {result.get('sentiment')} — {result.get('summary', '')[:60]}...")
    await close_mongodb()
    print(f"\nDone! Seeded {len(SAMPLE_FEEDBACK)} feedback entries.")


if __name__ == "__main__":
    asyncio.run(seed())
