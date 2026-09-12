# Kinesis AI - Judge Demonstration Guide

This guide provides step-by-step instructions for SIH judges to test the Kinesis AI prototype.

## Prerequisites

- Laptop with webcam
- Modern browser (Chrome/Edge recommended)
- Internet connection (for loading libraries, optional for AI features)
- 5-10 minutes for quick demo, 15 minutes for full demo

## Quick Setup (2 minutes)

1. **Navigate to application**
   - URL: http://localhost:5000 (or provided deployment URL)
   - Wait for page to load

2. **Check system status**
   - Look for AI status indicator on homepage
   - Green = AI available, Yellow = Fallback only, Red = No AI

## Demo 1: User Registration (1 minute)

**Objective:** Create a test account

**Steps:**
1. Click "Register" button in top navigation
2. Fill in registration form:
   - Username: `judge_test`
   - Email: `judge@sih.test`
   - Password: `Test123!`
   - Full Name: `SIH Judge`
   - Fitness Level: Intermediate
   - Preferred Sport: Fitness
3. Click "Create Account"
4. Observe automatic login and redirect to dashboard

**Expected Output:**
- Success message: "Account created successfully!"
- Dashboard loads with user profile
- XP shows 0, Level 1

## Demo 2: Real-Time Fitness Analysis (3 minutes)

**Objective:** Demonstrate push-up analysis with real-time feedback

**Steps:**
1. From dashboard, click "Workout" in navigation
2. Select "Push-Up Analysis"
3. Click "Start Camera" button
4. **Allow camera permission** when browser prompts
5. Stand in front of camera (full body visible)
6. Wait for "Calibration OK" message
7. Perform 3-5 push-ups:
   - Lower chest toward ground
   - Keep body straight
   - elbows to 90°
8. Observe real-time feedback:
   - Skeleton overlay on body
   - Form score (0-100) updating live
   - Rep counter incrementing
   - Corrections/positives appearing
9. Click "Finish Session" after completing reps

**Expected Output:**
- Skeleton rendered over body
- Form score between 60-95 for good form
- Rep counter increments on each complete rep
- Quality rep counter increments only for good form
- Real-time feedback: "Good body alignment" or "Keep your body straight"
- Session summary shows: reps, quality reps, avg form score, XP earned

## Demo 3: Incorrect Form Detection (2 minutes)

**Objective:** Show system detects poor form

**Steps:**
1. Start a new push-up session (or continue previous)
2. Perform 2-3 push-ups with intentional errors:
   - Sag hips (banana back)
   - Elbows flaring outward
   - Not going deep enough
3. Observe feedback

**Expected Output:**
- Form score drops below 60
- Corrections appear: "Hips are sagging", "Keep both arms even", "Go deeper"
- Quality reps do not increment for poor form
- Movement-risk indicator may show "Moderate Risk"

## Demo 4: Sports Analysis - Football (2 minutes)

**Objective:** Demonstrate football shooting analysis

**Steps:**
1. Navigate to "Football" from main menu
2. Select "Shooting Technique"
3. Start camera and calibrate
4. Perform shooting motion (simulate kick):
   - Plant foot stable
   - Kicking leg windup
   - Hip rotation
   - Follow-through
5. Observe shooting-specific feedback

**Expected Output:**
- Shooting-specific metrics: Plant Foot, Hip Rotation, Knee Position
- Score breakdown by component
- Feedback: "Stable plant foot" or "Straighten plant leg slightly"
- Style coaching option visible (e.g., "Technical Dribbler")

## Demo 5: Sports Analysis - Cricket (2 minutes)

**Objective:** Demonstrate cricket shot analysis

**Steps:**
1. Navigate to "Cricket" from main menu
2. Select "Pull Shot"
3. Start camera and calibrate
4. Simulate pull shot motion:
   - Back-foot transfer
   - Hip rotation
   - Bat swing
5. Observe cricket-specific feedback

**Expected Output:**
- Cricket-specific metrics: stance, weight transfer, hip rotation
- Feedback: "Good back-foot anchor" or "Ensure fuller shoulder rotation"
- Optional "Kohli Mode" toggle visible on cover drive

## Demo 6: Injury Risk Analysis (2 minutes)

**Objective:** Show movement-risk detection

**Steps:**
1. During any exercise session, observe the risk indicator
2. Perform movements with clear asymmetry or poor alignment
3. Check risk level display

**Expected Output:**
- Risk level: Low (green), Moderate (yellow), High (red)
- Risk score (0-100)
- Indicators: "Significant knee asymmetry detected"
- Body areas affected: "Knees", "Ankles", etc.
- **Disclaimer visible:** "This is a movement-risk indicator, not a medical diagnosis"

## Demo 7: AI Voice Coach (2 minutes)

**Objective:** Demonstrate bilingual voice coaching

**Steps:**
1. Navigate to "Voice Coach" from menu
2. Click microphone icon
3. Ask in English: "How was my form?"
4. Wait for AI response and audio playback
5. Ask in Hindi/Hinglish: "Mera pull shot kaisa tha?"
6. Observe language detection and response

**Expected Output:**
- Voice recognition captures query
- AI response appears in text
- Text-to-speech speaks response
- Hindi queries get Hindi responses
- English queries get English responses
- Fallback message if AI unavailable

## Demo 8: Dashboard & Gamification (2 minutes)

**Objective:** Show progress tracking and gamification

**Steps:**
1. Navigate to "Dashboard"
2. Review sections:
   - Recent workouts list
   - Total reps and quality reps
   - Average form score
   - XP and level progress
   - Achievements/badges
   - Injury risk records
3. Check charts (if Chart.js loaded)

**Expected Output:**
- Workout history with timestamps
- Aggregate statistics calculated correctly
- XP reflects earned points from sessions
- Level progression bar visible
- Badges displayed (if earned)
- Risk records with timestamps

## Demo 9: AI Training Plan Generation (2 minutes)

**Objective:** Show AI-powered workout planning

**Note:** Requires Ollama or Gemini API key configured

**Steps:**
1. Navigate to "Sports" → "Workout Generator"
2. Fill form:
   - Sport: Football
   - Position: Forward
   - Skill Level: Intermediate
   - Goal: Speed & Agility
   - Equipment: Basic
   - Duration: 4 weeks
3. Click "Generate Plan"
4. Wait for AI response (2-10 seconds)
5. Review generated plan

**Expected Output:**
- Structured 4-week training plan
- Week-by-week breakdown
- Specific exercises, sets, reps
- Warm-up and cool-down included
- Provider indicated (Ollama or Gemini)
- Plan saved to database if logged in

## Demo 10: Yoga Posture Analysis (2 minutes)

**Objective:** Show yoga alignment feedback

**Steps:**
1. Navigate to "Yoga" from menu
2. Select "Warrior II"
3. Start camera and calibrate
4. Perform Warrior II pose:
   - Wide stance
   - Front knee bent ~90°
   - Arms extended horizontal
   - Hips open
5. Observe pose-specific feedback

**Expected Output:**
- Pose-specific metrics: front knee angle, back knee angle, arm straightness
- Feedback: "Excellent front knee flexion" or "Bend your front knee deeper"
- Score between 0-100
- Corrections for alignment issues

## Troubleshooting Common Issues

### Camera not starting
- Check browser camera permissions
- Ensure no other app is using camera
- Try different browser (Chrome/Edge)
- Check if webcam is properly connected

### Skeleton not appearing
- Ensure good lighting
- Stand farther from camera (full body visible)
- Check calibration message
- Refresh page and try again

### AI features not working
- Check AI status on homepage
- If Ollama: ensure Ollama is running locally
- If Gemini: check API key in .env
- System will show fallback message if unavailable

### Form score always 0
- Ensure full body is visible in frame
- Check lighting conditions
- Verify calibration passed
- Try moving closer/farther from camera

## Demo Script Summary

| Demo | Time | Key Features Demonstrated |
|------|------|---------------------------|
| Registration | 1 min | User account creation, authentication |
| Fitness Analysis | 3 min | Real-time pose detection, form scoring, rep counting |
| Incorrect Form | 2 min | Poor form detection, quality gating |
| Football Analysis | 2 min | Sports-specific biomechanics, style coaching |
| Cricket Analysis | 2 min | Shot analysis, Kohli mode |
| Injury Risk | 2 min | Movement-risk indicators, safety disclaimers |
| Voice Coach | 2 min | Bilingual AI voice, language detection |
| Dashboard | 2 min | Progress tracking, gamification, charts |
| Training Plans | 2 min | AI workout generation, structured plans |
| Yoga Analysis | 2 min | Posture alignment, balance scoring |

**Total Time:** 18 minutes for full demo
**Quick Demo:** 8 minutes (Registration + Fitness + Dashboard)

## Key Talking Points for Judges

1. **Privacy-First:** Video processed locally, no frame uploads to cloud
2. **Real-Time:** 30 FPS analysis with sub-50ms latency
3. **Biomechanical:** Deterministic calculations, not AI inference during analysis
4. **Quality-Focused:** XP rewards form quality, not just rep count
5. **Safety-First:** Clear medical disclaimers, movement-risk not diagnosis
6. **Accessible:** Works with any webcam, no specialized hardware
7. **Bilingual:** Hindi/English support for pan-India reach
8. **Scalable:** Architecture supports multi-user deployment
9. **AI Hybrid:** Local Ollama + cloud Gemini fallback
10. **SIH Aligned:** Addresses Fitness & Sports theme with grassroots impact

## What to Highlight

**Technical Innovation:**
- Client-side MediaPipe for low latency
- Ollama-first AI architecture for privacy
- Deterministic biomechanical engine
- Quality rep gating system

**Social Impact:**
- Democratizes elite coaching
- Injury prevention for athletes
- Affordable solution (no expensive equipment)
- Bilingual support for accessibility

**Practicality:**
- Works with existing hardware
- Easy to use (web-based)
- Quick setup (2 minutes)
- No specialized training needed

## Post-Demo Questions

**Q: How accurate is the form detection?**
A: The system uses biomechanical calculations based on joint angles. Accuracy depends on camera positioning and lighting. We recommend consistent testing conditions for benchmarking.

**Q: Can this replace a human coach?**
A: No. Kinesis AI provides movement guidance and form feedback, but cannot replace human coaching expertise, especially for complex technical adjustments and holistic training.

**Q: Is the medical advice?**
A: No. The injury-risk engine provides movement indicators only. We explicitly state this is not medical diagnosis. Users should consult healthcare professionals for pain or injuries.

**Q: What about data privacy?**
A: Video frames are processed locally in the browser using MediaPipe JavaScript. Only structured metrics (angles, scores) are sent to the server. AI processing uses either local Ollama (no data leaves device) or Gemini cloud (only metrics, not video).

**Q: How does this scale?**
A: The architecture is stateless and horizontally scalable. Client-side pose processing reduces server load. Database can be upgraded to PostgreSQL. Multiple Flask instances can run behind a load balancer.

**Q: What's the business model?**
A: Potential models include: freemium (basic features free, advanced AI paid), institutional licensing (schools, academies), B2B integration (fitness apps, sports teams), and premium coaching tiers.

---

*Prepared for Smart India Hackathon 2026 Judges*
*Team INOVE8 | PS ID: 26196 | Fitness & Sports Theme*
