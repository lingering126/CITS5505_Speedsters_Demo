# notifications/utils.py
from app.models.models import Notification,db

def create_notification(user_id, actor_id, post_id=None, reply_id=None, message='', notification_type=''):
    notification = Notification(
        user_id=user_id,
        actor_id=actor_id,
        post_id=post_id,
        reply_id=reply_id,
        message=message,
        notification_type=notification_type
    )
    db.session.add(notification)
    db.session.commit()


def extract_mentions(content):
    import re
    mentions = re.findall(r'@(\w+)', content)
    return list(set(mentions))  # Return unique mentions
