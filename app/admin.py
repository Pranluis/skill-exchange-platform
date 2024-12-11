from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from .models import User  # Replace with your actual User model
from . import db
from .routes import mongo_db
from bson import ObjectId
from bson.objectid import ObjectId

admin = Blueprint('admin', __name__, template_folder='templates/admin')

@admin.route('/admin', methods=['GET'])  # Ensure only logged-in users can access
def admin_dashboard():
    # Fetch all users and feed data
    users = User.query.all()  # SQLAlchemy for PostgreSQL
    feed_posts = mongo_db.feeds.find()  # MongoDB
    
    return render_template('admin_dashboard.html', users=users, feed_posts=feed_posts)

@admin.route('/admin/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash(f"User {user_id} deleted successfully.", "success")
    else:
        flash("User not found.", "danger")
    return redirect(url_for('admin.admin_dashboard'))

@admin.route('/admin/delete_post/<string:post_id>', methods=['POST'])
def delete_post(post_id):
    object_id = ObjectId(post_id)
    result = mongo_db.feeds.delete_one({'_id': object_id})
    if result.deleted_count > 0:
        flash(f"Post {post_id} deleted successfully.", "success")
    else:
        flash("Post not found.", "danger")
    return redirect(url_for('admin.admin_dashboard'))
