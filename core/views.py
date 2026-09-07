from django.http import HttpResponse, HttpResponseForbidden
from django.template import Template, Context
from .models import PrivateNote
import urllib.request
from urllib.parse import urlparse
import socket
import ipaddress

def view_note(request, note_id):
    # FLAW 1: A01 Broken Access Control (IDOR)
    # We fetch the note by the ID in the URL, but NEVER check if the logged-in user owns it.
    note = PrivateNote.objects.get(id=note_id)
    
    # THE FIX: (Uncomment these two lines to fix the flaw)
    # if note.user != request.user:
    #    return HttpResponseForbidden("Access Denied: This is not your note!")
        
    return HttpResponse(f"<h1>Private Note:</h1><p>{note.secret_content}</p>")

def search(request):
    # Grab the search query from the URL (e.g., ?q=hello)
    query = request.GET.get('q', '')
    
    # FLAW 2: A03 Injection (XSS)
    # The '|safe' filter tells Django to execute whatever the user types as raw code.
    html = "<h1>Search</h1><p>You searched for: {{ query|safe }}</p>"
    
    # THE FIX: (Uncomment this and comment out the vulnerable html above)
    # Removing '|safe' allows Django to automatically sanitize the input.
    # html = "<h1>Search</h1><p>You searched for: {{ query }}</p>"
    
    template = Template(html)
    context = Context({'query': query})
    return HttpResponse(template.render(context))

def crash(request):
    # Helper view to trigger an error for Flaw 3
    return HttpResponse(1 / 0)

def fetch_external(request):
    url = request.GET.get('url', 'http://example.com')
    
    # FLAW 5: A10:2021 Server Side Request Forgery (SSRF)
    # The backend fetches an external resource using unvalidated user input, 
    # allowing attackers to make requests to internal network configurations or metadata endpoints.
    # response = urllib.request.urlopen(url)
    # return HttpResponse(response.read())

    # THE FIX: (Uncomment the block below and comment out the two active lines above)
    parsed = urlparse(url)
    if parsed.scheme not in ['http', 'https']:
        return HttpResponseForbidden("Blocked: Invalid protocol")
    try:
        ip = socket.gethostbyname(parsed.hostname)
        parsed_ip = ipaddress.ip_address(ip)
        if parsed_ip.is_private or parsed_ip.is_loopback or parsed_ip.is_link_local:
            return HttpResponseForbidden("Blocked: Internal or reserved IP address")
    except Exception:
        return HttpResponseForbidden("Blocked: Invalid hostname")
    
    response = urllib.request.urlopen(url, timeout=5)
    return HttpResponse(response.read())