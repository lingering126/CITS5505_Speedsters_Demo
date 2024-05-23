from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import current_user, login_required, login_user
from . import user
from app.models.models import Post, Reply, User, db
import os
from werkzeug.utils import secure_filename
from .forms import UpdatePictureForm, ChangePasswordForm
from werkzeug.security import generate_password_hash,check_password_hash


@user.route('/user/profile/<int:user_id>',methods=['GET', 'POST'])
@login_required
def user_profile(user_id, tab='posts'):

    user = User.query.get_or_404(user_id)
    post_page = request.args.get('post_page', 1, type=int)
    reply_page = request.args.get('reply_page', 1, type=int)
    per_page = 5  # Number of items per page
    
    # Query posts and replies associated with the user
    posts = Post.query.filter_by(user_id=user_id).order_by(Post.created_at.desc()).paginate(page=post_page, per_page=per_page)
    replies = Reply.query.filter_by(user_id=user_id).order_by(Reply.created_at.desc()).paginate(page=reply_page, per_page=per_page)

    return render_template('user/user_profile.html', user=user, posts=posts, replies=replies, active_tab=tab)

# Route for user settings
@user.route('/user_settings', methods=['GET', 'POST'])
@login_required
def user_settings():
    # Create forms for updating profile picture and changing password
    picture_form = UpdatePictureForm()
    password_form = ChangePasswordForm()

    # Handle profile picture update form submission
    if picture_form.validate_on_submit() and 'submit_picture' in request.form:
        if picture_form.picture.data:
            filename = secure_filename(picture_form.picture.data.filename)
            filepath = os.path.join(current_app.root_path, 'static/uploads', filename)
            picture_form.picture.data.save(filepath)
            current_user.profile_image_url = url_for('static', filename='uploads/' + filename)
            db.session.commit()
            flash('Profile picture updated successfully.','success')
        return redirect(url_for('user.user_settings'))

    # Handle password change form submission
    if password_form.validate_on_submit() and 'submit_password' in request.form:
        if not check_password_hash(current_user.password_hash, password_form.current_password.data):
            flash('Current password is wrong.', 'danger')
        elif password_form.password.data != password_form.confirm_password.data:
            flash('Passwords must match', 'danger')
        else:
            # Generate password hash and update user's password in database
            current_user.password_hash = generate_password_hash(password_form.password.data)
            db.session.commit()
            flash('Password updated successfully.','success')
            return redirect(url_for('user.user_settings'))

    # Render user settings template with forms and current user object
    return render_template('user/user_settings.html', picture_form=picture_form, password_form=password_form, user=current_user)


