from itertools import chain
from operator import attrgetter

def get_ordered_loads(u=None):
    from .models import Loop, SamplePack  # Import locale per evitare circular imports
    
    lista_modello1 = Loop.objects.all()
    lista_modello2 = SamplePack.objects.all()

    if u:
        # Filtra per utente se fornito
        lista_modello1 = lista_modello1.filter(user=u)
        lista_modello2 = lista_modello2.filter(user=u)
    
    caricamenti = []
    for obj in chain(lista_modello1, lista_modello2):
        caricamenti.append({
            'obj': obj,
            'modeltype': obj.__class__.__name__,
        })
    
    caricamenti_ordinati = sorted(caricamenti, key=lambda x: x['obj'].uploaded_at, reverse=True)

    # Unisci e ordina per uploaded_at (decrescente)
    return caricamenti_ordinati

def get_most_liked_loads(limit=5):
    from .models import Loop, SamplePack  # Import locale per evitare circular imports
    
    lista_modello1 = Loop.objects.all()
    lista_modello2 = SamplePack.objects.all()

    caricamenti = []
    for obj in chain(lista_modello1, lista_modello2):
        caricamenti.append({
            'obj': obj,
            'modeltype': obj.__class__.__name__,
        })
    
    caricamenti_ordinati = sorted(caricamenti, key=lambda x: x['obj'].likes.count(), reverse=True)

    return caricamenti_ordinati[:limit]

def process_tags_from_request(request):
    """
    Estrae e processa i tag dal campo 'tags' della richiesta POST.
    Restituisce una lista di istanze Tag.
    """
    from .models import Tag  # Import locale per evitare circular imports

    tags = request.POST.getlist('tags')

    new_tags = []

    for tag in tags:
        if tag.isdigit():
            tag_id = int(tag)
            if Tag.objects.filter(id=tag_id).exists():
                new_tags.append(tag_id)
        else:
            tag_name = tag.strip()
            if tag_name:
                new_tag, created = Tag.objects.get_or_create(name=tag_name)
                new_tags.append(new_tag.id)
    post_data = request.POST.copy()
    post_data.setlist('tags', [str(pk) for pk in new_tags])
    print(f"🔍 ALL POST data: {dict(post_data)}")
    return post_data, new_tags
