from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models import Expense, Budget
from datetime import datetime

finance = Blueprint('finance', __name__)

CATEGORIES = ['Food', 'Transport', 'Data', 'Stationery', 'Personal Care', 'Rent', 'Entertainment', 'Other']


@finance.route('/expense/add', methods=['GET', 'POST'])
@login_required
def add_expense():
    if request.method == 'POST':
        title = request.form.get('title')
        amount = float(request.form.get('amount'))
        category = request.form.get('category')

        new_expense = Expense(
            user_id=current_user.id,
            title=title,
            amount=amount,
            category=category
        )
        db.session.add(new_expense)
        db.session.commit()

        flash('Expense logged successfully.', 'success')
        return redirect(url_for('finance.expenses'))

    return render_template('add_expense.html', categories=CATEGORIES)


@finance.route('/expenses')
@login_required
def expenses():
    all_expenses = Expense.query.filter_by(user_id=current_user.id)\
        .order_by(Expense.date_spent.desc()).all()

    category_totals = {}
    for expense in all_expenses:
        category_totals[expense.category] = \
            category_totals.get(expense.category, 0) + expense.amount

    return render_template('expenses.html', expenses=all_expenses, category_totals=category_totals)


@finance.route('/budget', methods=['GET', 'POST'])
@login_required
def set_budget():
    current_month = datetime.utcnow().strftime('%B %Y')
    existing_budget = Budget.query.filter_by(
        user_id=current_user.id,
        month=current_month
    ).first()

    if request.method == 'POST':
        amount = float(request.form.get('amount'))

        if existing_budget:
            existing_budget.amount = amount
        else:
            new_budget = Budget(
                user_id=current_user.id,
                month=current_month,
                amount=amount
            )
            db.session.add(new_budget)

        db.session.commit()
        flash('Budget set for ' + current_month + '.', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('set_budget.html', existing_budget=existing_budget, current_month=current_month)


@finance.route('/expense/delete/<int:expense_id>')
@login_required
def delete_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    if expense.user_id != current_user.id:
        flash('You cannot delete this expense.', 'danger')
        return redirect(url_for('finance.expenses'))
    db.session.delete(expense)
    db.session.commit()
    flash('Expense deleted.', 'info')
    return redirect(url_for('finance.expenses'))