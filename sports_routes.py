"""
Kinesis AI - Sports Routes
Handles Sports Center Hub, Football & Cricket modules, individual drills, and AI Sports Training Planner.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user, login_required
from models import db, SportsSession, TrainingPlan
from ai_provider import get_ai
from football_analyzer import FootballAnalyzer
from cricket_analyzer import CricketAnalyzer

sports_bp = Blueprint('sports', __name__)


# ============================================================
# Sports Center Hub
# ============================================================

@sports_bp.route('/sports')
def sports_hub():
    """Sports Center main landing page."""
    return render_template('sports.html')


# ============================================================
# Football Hub & Drill Pages
# ============================================================

@sports_bp.route('/football')
def football_hub():
    """Football Training Hub."""
    return render_template('football.html')


@sports_bp.route('/football/shooting')
def football_shooting():
    """Football Shooting Technique analysis page."""
    return render_template('football_shooting.html')


@sports_bp.route('/football/dribbling')
def football_dribbling():
    """Football Dribbling & Agility pose-based analysis page."""
    return render_template('football_dribbling.html')


@sports_bp.route('/football/agility')
def football_agility():
    """Football Agility & Reaction drill page."""
    return render_template('football_agility.html')


# ============================================================
# Cricket Hub & Shot Pages
# ============================================================

@sports_bp.route('/cricket')
def cricket_hub():
    """Cricket Training Hub."""
    return render_template('cricket.html')


@sports_bp.route('/cricket/pull-shot')
def cricket_pull_shot():
    """Cricket Pull Shot biomechanics analysis page."""
    return render_template('cricket_pull_shot.html')


@sports_bp.route('/cricket/cover-drive')
def cricket_cover_drive():
    """Cricket Cover Drive biomechanics (with optional Kohli style) page."""
    return render_template('cricket_cover_drive.html')


@sports_bp.route('/cricket/straight-drive')
def cricket_straight_drive():
    """Cricket Straight Drive biomechanics analysis page."""
    return render_template('cricket_straight_drive.html')


@sports_bp.route('/cricket/bowling')
def cricket_bowling():
    """Cricket Bowling action & shoulder/lumbar biomechanics page."""
    return render_template('cricket_bowling.html')


@sports_bp.route('/cricket/batting-stance')
def cricket_batting_stance():
    """Cricket Batting Stance balance & readiness analysis page."""
    return render_template('cricket_batting_stance.html')


# ============================================================
# AI Sports Workout Generator
# ============================================================

@sports_bp.route('/sports/workout-generator', methods=['GET', 'POST'])
def sports_workout_generator():
    """AI Sports Training Plan Generator (4-week progressive plan)."""
    generated_plan = None
    provider_used = None

    if request.method == 'POST':
        sport = request.form.get('sport', 'football')
        position = request.form.get('position', 'Forward')
        skill_level = request.form.get('skill_level', 'intermediate')
        goal = request.form.get('goal', 'Speed & Agility')
        equipment = request.form.get('equipment', 'Basic (Cones, Ball)')
        weeks = int(request.form.get('weeks', 4) or 4)

        ai = get_ai()
        result = ai.generate_training_plan(
            sport=sport,
            position=position,
            skill_level=skill_level,
            goal=goal,
            equipment=equipment,
            weeks=weeks
        )
        generated_plan = result.get('text', '')
        provider_used = result.get('provider', 'ollama')

        # Save to database if user is logged in
        if current_user.is_authenticated:
            plan_obj = TrainingPlan(
                user_id=current_user.id,
                plan_type=f"{sport}_sports",
                sport=sport,
                position=position,
                skill_level=skill_level,
                goal=goal,
                equipment=equipment,
                duration_weeks=weeks,
                ai_provider=provider_used
            )
            plan_obj.plan = {'text': generated_plan}
            db.session.add(plan_obj)
            db.session.commit()
            flash('Your personalized 4-week training plan has been saved!', 'success')

    return render_template('sports_workout.html', plan=generated_plan, provider=provider_used)
