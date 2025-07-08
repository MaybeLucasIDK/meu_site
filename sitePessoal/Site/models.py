import uuid #to generate unique identifiers
from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class ChatRoom(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_name = models.CharField(max_length=100)
    user_email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"ChatRoom with {self.id, self.user_name} - ({'Active' if self.is_active else 'Inactive'})"
    
class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    message = models.TextField()
    is_from_admin = models.BooleanField(default=False)
    time_stamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        sender = "Admin" if self.is_from_admin else self.room.user_name
        return f"Message from {sender} in room {self.room.id}: {self.message[:20]}... at {self.time_stamp.strftime('%Y-%m-%d %H:%M:%S')}"
