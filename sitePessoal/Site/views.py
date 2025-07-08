from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import json
from .models import ChatRoom


# Create your views here.

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def projects(request):
    return render(request, 'projects.html')

def gallery(request):
    return render(request, 'gallery.html')

@require_POST
def create_chat_room(request):
    """View para criar uma sala de chat via AJAX."""
    try:
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        email = data.get('email', '').strip() 

        if not name or not email:
            return JsonResponse({'error': 'Name and E-mail are required'}, status=400)
        
        validate_email(email)
        
        room = ChatRoom.objects.filter(user_email = email, is_active = True).first()

        if room:
            # se sala encontrada, carrega histórico
            print(f"Restauring existent session for {email}")
            messages = room.messages.order_by('time_stamp')
            history = [
                {
                    'message': msg.message,
                    'is_from_admin': msg.is_from_admin
                }
                for msg in messages
            ]
            request.session['chat_room_uuid'] = str(room.id)
            return JsonResponse({'room_uuid': room.id, 'history': history})
        
        else:
            #cria sala se nenhuma ativa
            print(f"Creating new session for {email}")
            new_room = ChatRoom.objects.create(user_name = name, user_email = email)
            request.session['chat_room_uuid'] = str(new_room.id)
            return JsonResponse({'room_uuid': new_room.id, 'history': []})
        
    except ValidationError:
        return JsonResponse({'error': 'Invalid email format'}, status=400)
    except Exception as e:
        return JsonResponse({'error:' 'Unexpected error occurred'}, status=500)

from django.http import HttpResponse

# -- admin --
@staff_member_required
def admin_chat_list(request):
    """Lista todas as salas de chat ativas para o admin."""
    active_rooms = ChatRoom.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'Site/admin_chat_list.html', {'rooms': active_rooms})

@staff_member_required
def admin_chat_room(request, room_uuid):
    """Entra em uma sala de chat específica como admin."""
    room = get_object_or_404(ChatRoom, id=room_uuid)
    messages = room.messages.order_by('time_stamp')
    return render(request, 'Site/admin_chat_room.html', {
        'room': room,
        'messages': messages,
    })

@staff_member_required
@require_POST
def admin_delete_chat_room(request, room_uuid):
    room_to_delete = get_object_or_404(ChatRoom, id=room_uuid)
    room_to_delete.delete()

    return redirect('Site:admin_chat_list')
        