from flask import render_template, request,jsonify, redirect, url_for, flash, session,g
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user, login_required, login_user
from . import pr
from app.models.models import Post, Reply, db, User, Vote
from datetime import datetime
from .forms import PostForm
import openai
from app.blueprint.notifications.utils import create_notification, extract_mentions
from .utils import fetch_car_news
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')
print("OpenAI API Key:", openai.api_key)
from flask import g

# Set user globally for every request
@pr.before_request
def before_request():
    g.user = current_user if current_user.is_authenticated else None

# Route for the post page
@pr.route('/view_posts')
def view_post():
    tag = request.args.get('tag')
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Number of posts per page

    # user can select the tag to filter post
    if tag:
        posts = Post.query.filter_by(category=tag).order_by(Post.last_reply_date.desc()).paginate(page=page, per_page=per_page)
    else:
        posts = Post.query.order_by(Post.last_reply_date.desc()).paginate(page=page, per_page=per_page)


    user = current_user
    for post in posts.items:
        last_reply = Reply.query.filter_by(post_id=post.id).order_by(Reply.created_at.desc()).first()
        if last_reply:  # Check if there is a reply
            post.last_replier_username = last_reply.user.username
            post.last_reply_date = last_reply.created_at
        else:
            post.last_replier_username = 'No replies'
            post.last_reply_date = post.created_at  # Use the post creation date if no replies

    return render_template('posts/view_posts.html', posts = posts, user = user)

# Route for the main page
@pr.route('/forums')
def forums():
    return render_template('forums.html')

# Create post
@pr.route('/create-post', methods=['GET', 'POST'])
def create_post():
    # Check if the user is authenticated
    if not current_user.is_authenticated:
        flash('You must be logged in to view this page.','warning')
        return redirect(url_for('auth.login'))  
        # Redirect them to the registration page

    form = PostForm()
    if form.validate_on_submit():
        new_post = Post(title=form.title.data, category=form.category.data, content=form.content.data, user_id=current_user.id)
        db.session.add(new_post)
        db.session.commit()

        # 1.1 new feature: check for mentions and create notification
        mentions = extract_mentions(form.content.data) # Extract mentions from the post content
        for username in mentions:
            user = User.query.filter_by(username=username).first()
            if user:
                create_notification(
                    user_id=user.id, 
                    actor_id=current_user.id,
                    post_id=new_post.id, 
                    message=form.content.data[:50] + '...',
                    notification_type='mention'
                )
        # -end- 1.1

        flash('Your post has been created!', 'success')
        return redirect(url_for('pr.view_post'))  # Redirect to posts page
    return render_template('posts/create_post.html', form=form,user=current_user)



@pr.route('/detail/<int:post_id>')
def details(post_id):
    page = request.args.get('page', 1, type=int)
    per_page = 6  # Number of replies per page

    post = Post.query.get_or_404(post_id)  # Fetch the post or return 404 if not found

    # Fetch replies with pagination
    replies = Reply.query.filter_by(post_id=post.id).order_by(Reply.created_at.asc()).paginate(page=page, per_page=per_page)
    
    post.views += 1  # Increment the view count
    db.session.commit()
    return render_template('posts/detail.html', post=post,replies=replies)


# Handle submit reply
@pr.route('/submit-reply/<int:post_id>', methods=['POST'])
def submit_reply(post_id):
    # Check if the user is authenticated
    if not current_user.is_authenticated:
        flash('You must be logged in to view this page.','warning')
        return redirect(url_for('auth.login'))  
        # Redirect them to the registration page

    post = Post.query.get_or_404(post_id)  # Make sure the post exists
    reply_content = request.form['reply_content']
    if reply_content:
        reply = Reply(content=reply_content, post_id=post.id, user_id=current_user.id)
        db.session.add(reply)
        db.session.commit()

        #Increment the reply count
        post.replies_count += 1 
        db.session.commit()
        # Update the last reply date
        post.last_reply_date = datetime.utcnow() 
        db.session.commit()

        #####################1.1 new feature
        # Create notification for the post author
        if current_user.id != post.user_id:  # Avoid notifying the user themselves
            create_notification(
                user_id=post.user_id, # the one who receives the notification
                actor_id=current_user.id, # the one who performs the notification
                post_id=post.id, 
                reply_id=reply.id, 
                message=reply_content[:50] + '...',
                notification_type='new_reply'
            )
        
        # Check for mentions and create notifications
        mentions = extract_mentions(reply_content)  # Extract mentions from the reply content
        for username in mentions:
            user = User.query.filter_by(username=username).first()
            if user and user.id != post.user_id:  # Avoid duplicate notification to the post author
                create_notification(
                    user_id=user.id, 
                    actor_id=current_user.id,
                    post_id=post.id, 
                    reply_id=reply.id, 
                    message=reply_content[:50] + '...',
                    notification_type='mention'
                )
        #######################1.1 end

        flash('Your reply has been posted.', 'success')
    else:
        flash('Reply cannot be empty.', 'error')
    return redirect(url_for('pr.details', post_id=post_id))  # Redirect back to the post detail page

#Route for chatbot
@pr.route("/chat", methods=["GET", "POST"])
def chat():
    # Check if the user is logged in
    if not current_user.is_authenticated:
        flash('You must be logged in to use the chatbot.', 'warning')
        return redirect(url_for('auth.login'))

    # Initialize chat history if not present in the session
    if 'chat_history' not in session:
        session['chat_history'] = []

    if request.method == "POST":
        # Extract the question from the form data
        question = request.form["question"]
        
        # Append the user's question to the chat history
        session['chat_history'].append({'role': 'user', 'content': question})
        
        # Generate a response using the GPT-3.5 Turbo model
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=session['chat_history'],  # Send the entire chat history
            temperature=0.6, 
            max_tokens=1000, 
        )
        answer = response.choices[0].message['content']
        
        # Append the bot's answer to the chat history
        session['chat_history'].append({'role': 'assistant', 'content': answer})
        
        # Redirect to the same page to display the updated chat history
        return redirect(url_for("pr.chat"))

    # Retrieve the chat history from the session
    chat_history = session.get('chat_history', [])
    
    # Render the chatbot template with the chat history
    return render_template("posts/chatbot.html", chat_history=chat_history, user=current_user) #define user





#search function
@pr.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    search_type = request.args.get('search_type')
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Number of search results per page

    # Get current user if logged in
    user = current_user if current_user.is_authenticated else None

    # Initialize results query
    results_query = None

    if query:
        # Ensure the query and search type are handled properly
        query = f"%{query}%"

        if search_type == 'Titles':
            # Search by post titles
            results_query = Post.query.filter(Post.title.ilike(query))
        elif search_type == 'Descriptions':
            # Search by post descriptions
            results_query = Post.query.filter(Post.content.ilike(query))
        else:
            # Search by both titles and descriptions
            results_query = Post.query.filter(
                (Post.title.ilike(query)) | (Post.content.ilike(query))
            )

        # Order by last_reply_date before pagination
        results_query = results_query.order_by(Post.last_reply_date.desc())

        # Paginate the results
        results = results_query.paginate(page=page, per_page=per_page)

        # fetch the last replier's username and last reply date for each post
        for post in results.items:
            last_reply = Reply.query.filter_by(post_id=post.id).order_by(Reply.created_at.desc()).first()
            if last_reply:
                post.last_replier_username = last_reply.user.username
                post.last_reply_date = last_reply.created_at
            else:
                post.last_replier_username = 'No replies'
                post.last_reply_date = post.created_at
    else:
        results = None

    return render_template('posts/search_results.html', results=results, query=query, user=user)



#######################1.1 new features likes 
@pr.route('/vote/<string:type>/<int:id>/<string:action>', methods=['POST'])
@login_required
def vote(type, id, action):
    try:
        # Determine the item type (post or reply)
        if type == 'post':
            item = Post.query.get_or_404(id)
        elif type == 'reply':
            item = Reply.query.get_or_404(id)
        else:
            return jsonify({'success': False, 'error': 'Invalid type'}), 400

        # Check if the user has already voted on this item
        existing_vote = Vote.query.filter_by(
            user_id=current_user.id,
            post_id=id if type == 'post' else None,
            reply_id=id if type == 'reply' else None
        ).first()

        if existing_vote:
            if existing_vote.vote_type == action:
                # User is trying to vote the same way again, do nothing
                return jsonify({'success': False, 'error': 'You have already voted this way'}), 400
            
            # User is changing their vote
            if existing_vote.vote_type == 'like' and action == 'dislike':
                item.likes -= 1  # Remove the like
            elif existing_vote.vote_type == 'dislike' and action == 'like':
                item.likes += 1  # Remove the dislike

            # Remove the existing vote
            db.session.delete(existing_vote)
            db.session.commit()

            # Allow user to vote again
            return jsonify({'success': True, 'likes': item.likes, 'neutral': True})

        else:
            # Create a new vote record
            vote = Vote(
                user_id=current_user.id,
                post_id=id if type == 'post' else None,
                reply_id=id if type == 'reply' else None,
                vote_type=action
            )
            if action == 'like':
                item.likes += 1
            else:
                item.likes -= 1
            db.session.add(vote)

            db.session.commit()

            return jsonify({'success': True, 'likes': item.likes, 'neutral': False})

    except Exception as e:
        db.session.rollback()
        print(f"Error in vote route: {e}")  # Log the error
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

#######################


############1.1 new feature see news
@pr.route('/news')
def news():
    api_key = 'eb24ca091e3a4ffa8ee813dd7ca5195b'  # Replace with NewsAPI key
    articles = fetch_car_news(api_key)
    return render_template('posts/news.html', articles=articles)
##########