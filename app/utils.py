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