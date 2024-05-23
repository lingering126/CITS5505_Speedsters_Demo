# notifications/routes.py
from flask import render_template, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from . import notifications_bp
from app.models.models import Notification,db, User


@notifications_bp.route('/')
@login_required
def notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id).all()
    notifications_data = []
    for notification in notifications:
        actor = notification.actor  # The user who performed the action
        post = notification.post  # The post where the action happened
        notifications_data.append({
            'id': notification.id,
            'message': notification.message[:30] + '...',  # Display part of the content
            'created_at': notification.created_at,
            'is_read': notification.is_read,
            'actor_name': actor.username,
            'actor_image': actor.profile_image_url,
            'notification_type': notification.notification_type,
            'post_id': post.id
        })
    return render_template('notifications/notifications.html', notifications=notifications_data)

# mark the notification as read
@notifications_bp.route('/mark_as_read/<int:notification_id>')
@login_required
def mark_as_read(notification_id):
    notification = Notification.query.get(notification_id)
    if notification and notification.user_id == current_user.id:
        notification.is_read = True
        db.session.commit()
    return redirect(url_for('notifications.notifications'))


# delete notification
@notifications_bp.route('/delete/<int:notification_id>')
@login_required
def delete_notification(notification_id):
    notification = Notification.query.get(notification_id)
    if notification and notification.user_id == current_user.id:
        db.session.delete(notification)
        db.session.commit()
        flash('Notification deleted.', 'success')
    return redirect(url_for('notifications.notifications'))



# Showing latest notification
@notifications_bp.route('/latest')
@login_required
def latest_notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).order_by(Notification.created_at.desc()).limit(3).all()
    return jsonify([{
        'id': n.id,
        'message': n.message,
        'created_at': n.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'is_read': n.is_read
    } for n in notifications])
