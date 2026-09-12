# Kinesis AI — Phase 2 Changelog

## New Features

### Injury Risk Prediction Engine (`injury_risk_engine.py`)
- Session-level fatigue drift: compares form score of first-third vs last-third
  reps within a session to catch technique breakdown as it happens.
- Cross-session trend: tracks rolling average form score over the last 30 days
  per exercise, flags compounding decline before it becomes an injury.
- Returns risk_level (low/moderate/high), risk_score (0-100), a plain-language
  note, and a corrective drill per exercise type.

### Gamification Engine (`gamification.py`)
- XP = effort (reps + duration) × form-quality multiplier — sloppy volume
  earns less than clean technique, per the original README promise.
- 10-level XP curve, day-based streak tracking (breaks on >1 day gap),
  7 badges (first workout, streak milestones, form perfectionist, level 5,
  century club).
- Leaderboard sort by XP.

### New route: `POST /api/complete-session`
The missing piece that ties it all together — call this once when a workout
set/session ends with:
```json
{
  "exercise_type": "squat",
  "reps_completed": 15,
  "duration_minutes": 6,
  "calories_burned": 45,
  "rep_form_scores": [88, 85, 90, 82, 76, 70, 65],
  "notes": "optional"
}
```
Saves the Workout row, runs both risk assessments, awards XP/streak/badges,
and returns everything in one response.

### New route: `GET /api/leaderboard`

### New DB tables
- `UserStats` — xp, level, streak, badges per user
- `InjuryRiskLog` — risk assessment history

## Bugs Fixed This Phase

1. **Workout model schema mismatch** — `export_data`, `import_data`,
   `backup_data`, `restore_data` referenced `duration`/`difficulty`/`exercises`
   fields that didn't exist on the `Workout` model (real column was
   `duration_minutes`, no `difficulty`/`exercises` at all). Would have crashed
   on first use. Fixed field names, added `difficulty` column.

2. **No session-save path ever existed** — pose_detection.py analyzed reps
   live but nothing persisted a completed session's `reps_completed` /
   `form_score` to the DB. Added `/api/complete-session` to close this gap.

3. **`diet_service.py`** — DeepSeek-R1 reasoning model was exhausting its
   `num_predict` budget entirely inside `<think>` blocks, leaving no JSON to
   parse. Fixed with reasoning-model detection, bigger token budget, robust
   JSON extraction tolerant of unclosed think tags, and a diet-preference-aware
   fallback plan (previously always served chicken/salmon even for Vegan).

4. **`gemini.py`** — `models/gemini-2.0-flash` was deprecated by Google;
   switched default to `models/gemini-3.6-flash`. Also gave `_ollama_complete`
   (the Gemini-failure fallback path) a real timeout — it had none, so a slow
   reasoning model could hang the request indefinitely with no error.

5. **Stale `instance/kinesis.db` removed** — old schema predates the new
   columns/tables above; `db.create_all()` won't alter existing tables, so a
   fresh DB is required. It will be recreated automatically on next app start.

## What's Still Not Built (per original README claims)
- `sports_tracker.py` (shuttle runs, jump-rope cadence, agility ladder) — not
  present in codebase.
- `coach_dashboard.py` (school/batch-level view) — not present in codebase.
- Frontend UI for injury risk / XP / badges / leaderboard — backend routes
  exist and return data, but no dashboard template consumes them yet.

## Required: Frontend Wiring
Wherever `pose_detection.py`'s live analysis loop runs client-side, you need
to accumulate each rep's `form_score` into an array and POST it to
`/api/complete-session` when the user ends the set. This wasn't wired up as
part of this phase — it's the one manual integration step left.
