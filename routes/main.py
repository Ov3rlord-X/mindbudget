from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import MoodLog, Expense, Budget, Journal
from extensions import db, bcrypt
from datetime import datetime, timedelta

main = Blueprint('main', __name__)


@main.route('/')
def home():
    return render_template('home.html')


@main.route('/dashboard')
@login_required
def dashboard():
    moods = MoodLog.query.filter_by(user_id=current_user.id)\
        .order_by(MoodLog.date_logged.desc()).limit(7).all()

    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    expenses = Expense.query.filter_by(user_id=current_user.id)\
        .filter(Expense.date_spent >= seven_days_ago).all()

    current_month = datetime.utcnow().strftime('%B %Y')
    budget = Budget.query.filter_by(
        user_id=current_user.id,
        month=current_month
    ).first()

    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)
    monthly_expenses = Expense.query.filter_by(user_id=current_user.id)\
        .filter(Expense.date_spent >= month_start).all()
    total_spent = sum(e.amount for e in monthly_expenses)

    budget_alert = None
    if budget:
        percent_spent = (total_spent / budget.amount) * 100
        if percent_spent >= 100:
            budget_alert = 'danger'
        elif percent_spent >= 75:
            budget_alert = 'warning'

    return render_template('dashboard.html',
        moods=moods,
        expenses=expenses,
        budget=budget,
        total_spent=total_spent,
        budget_alert=budget_alert,
        current_month=current_month
    )


# ── JOURNAL ──────────────────────────────────────────────

@main.route('/journal')
@login_required
def journal():
    entries = Journal.query.filter_by(user_id=current_user.id)\
        .order_by(Journal.date_written.desc()).all()
    return render_template('journal.html', entries=entries)


@main.route('/journal/new', methods=['GET', 'POST'])
@login_required
def new_entry():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')

        if not title or not content:
            flash('Please fill in both the title and content.', 'danger')
            return redirect(url_for('main.new_entry'))

        entry = Journal(
            user_id=current_user.id,
            title=title,
            content=content
        )
        db.session.add(entry)
        db.session.commit()

        flash('Journal entry saved.', 'success')
        return redirect(url_for('main.journal'))

    return render_template('new_entry.html')


@main.route('/journal/<int:entry_id>')
@login_required
def view_entry(entry_id):
    entry = Journal.query.get_or_404(entry_id)
    if entry.user_id != current_user.id:
        flash('You cannot view this entry.', 'danger')
        return redirect(url_for('main.journal'))
    return render_template('view_entry.html', entry=entry)


@main.route('/journal/delete/<int:entry_id>')
@login_required
def delete_entry(entry_id):
    entry = Journal.query.get_or_404(entry_id)
    if entry.user_id != current_user.id:
        flash('You cannot delete this entry.', 'danger')
        return redirect(url_for('main.journal'))
    db.session.delete(entry)
    db.session.commit()
    flash('Journal entry deleted.', 'info')
    return redirect(url_for('main.journal'))


# ── WEEKLY REPORT ─────────────────────────────────────────

@main.route('/weekly-report')
@login_required
def weekly_report():
    today = datetime.utcnow()
    week_start = today - timedelta(days=7)

    moods = MoodLog.query.filter_by(user_id=current_user.id)\
        .filter(MoodLog.date_logged >= week_start)\
        .order_by(MoodLog.date_logged.asc()).all()

    expenses = Expense.query.filter_by(user_id=current_user.id)\
        .filter(Expense.date_spent >= week_start)\
        .order_by(Expense.date_spent.asc()).all()

    total_spent = sum(e.amount for e in expenses)

    category_totals = {}
    for e in expenses:
        category_totals[e.category] = category_totals.get(e.category, 0) + e.amount

    mood_counts = {}
    for m in moods:
        mood_counts[m.mood] = mood_counts.get(m.mood, 0) + 1

    dominant_mood = max(mood_counts, key=mood_counts.get) if mood_counts else None

    mood_scores = {
        'happy': 5, 'okay': 4, 'tired': 3,
        'frustrated': 2, 'sad': 2, 'stressed': 1
    }

    if moods:
        avg_score = sum(mood_scores.get(m.mood, 3) for m in moods) / len(moods)
    else:
        avg_score = 0

    if avg_score >= 4.5:
        wellness_message = "You had an amazing week emotionally. Keep doing whatever you are doing."
        wellness_color = "#2ecc71"
    elif avg_score >= 3.5:
        wellness_message = "Your week was mostly positive. A few tough moments but you held up well."
        wellness_color = "#27ae60"
    elif avg_score >= 2.5:
        wellness_message = "It was a mixed week. Try to identify what pulled your mood down and address it."
        wellness_color = "#f39c12"
    elif avg_score >= 1.5:
        wellness_message = "This week was tough. Be kind to yourself and reach out to someone you trust."
        wellness_color = "#e67e22"
    else:
        wellness_message = "This was a really difficult week. You are stronger than you know."
        wellness_color = "#e74c3c"

    current_month = datetime.utcnow().strftime('%B %Y')
    budget = Budget.query.filter_by(
        user_id=current_user.id,
        month=current_month
    ).first()

    return render_template('weekly_report.html',
        moods=moods,
        expenses=expenses,
        total_spent=total_spent,
        category_totals=category_totals,
        mood_counts=mood_counts,
        dominant_mood=dominant_mood,
        avg_score=avg_score,
        wellness_message=wellness_message,
        wellness_color=wellness_color,
        budget=budget,
        week_start=week_start,
        today=today
    )


# ── ABOUT ─────────────────────────────────────────────────

@main.route('/about')
def about():
    return render_template('about.html')


# ── SETTINGS ─────────────────────────────────────────────

@main.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'update_name':
            new_name = request.form.get('fullname')
            if new_name:
                current_user.fullname = new_name
                db.session.commit()
                flash('Name updated successfully.', 'success')

        elif action == 'change_password':
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')

            if not bcrypt.check_password_hash(current_user.password, current_password):
                flash('Current password is incorrect.', 'danger')
            elif new_password != confirm_password:
                flash('New passwords do not match.', 'danger')
            elif len(new_password) < 6:
                flash('Password must be at least 6 characters.', 'danger')
            else:
                current_user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
                db.session.commit()
                flash('Password changed successfully.', 'success')

        return redirect(url_for('main.settings'))

    return render_template('settings.html')