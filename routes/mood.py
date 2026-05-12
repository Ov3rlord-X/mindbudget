from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models import MoodLog

mood = Blueprint('mood', __name__)

AFFIRMATIONS = {
    'happy': {
        'message': 'That is wonderful! Keep that energy going.',
        'tip': 'Use this positive energy to tackle something you have been putting off.'
    },
    'okay': {
        'message': 'Okay is perfectly fine. Not every day has to be amazing.',
        'tip': 'Try doing one small thing today that makes you smile.'
    },
    'sad': {
        'message': 'It is okay to feel sad. Your feelings are valid and this will pass.',
        'tip': 'Be kind to yourself today. Rest if you need to.'
    },
    'stressed': {
        'message': 'You are carrying a lot right now but you are stronger than you think.',
        'tip': 'Take 5 deep slow breaths right now. Then tackle one thing at a time.'
    },
    'frustrated': {
        'message': 'Frustration means you care. That is not a bad thing.',
        'tip': 'Step away from what is frustrating you for 10 minutes then come back.'
    },
    'tired': {
        'message': 'Your body and mind are telling you something. Listen to them.',
        'tip': 'Rest is not laziness. Give yourself permission to slow down today.'
    }
}


@mood.route('/mood', methods=['GET', 'POST'])
@login_required
def log_mood():
    affirmation = None

    if request.method == 'POST':
        selected_mood = request.form.get('mood')
        note = request.form.get('note')
        is_financial = request.form.get('financial_stress')

        new_mood = MoodLog(
            user_id=current_user.id,
            mood=selected_mood,
            note=note
        )
        db.session.add(new_mood)
        db.session.commit()

        affirmation = AFFIRMATIONS.get(selected_mood, {}).copy()

        if is_financial:
            affirmation['financial_tip'] = 'Consider reviewing your budget today. Small adjustments now can ease a lot of pressure later.'

        flash('Mood logged successfully.', 'success')

    mood_history = MoodLog.query.filter_by(user_id=current_user.id)\
        .order_by(MoodLog.date_logged.desc()).limit(10).all()

    return render_template('mood.html', affirmation=affirmation, mood_history=mood_history)


@mood.route('/mood/history')
@login_required
def mood_history():
    moods = MoodLog.query.filter_by(user_id=current_user.id)\
        .order_by(MoodLog.date_logged.desc()).all()
    return render_template('mood_history.html', moods=moods)