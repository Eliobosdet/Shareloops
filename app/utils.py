from itertools import chain
from operator import attrgetter

def get_ordered_loads(u):
    from .models import Loop, SamplePack  # Import locale per evitare circular imports
    
    # Recupera i dati dai due modelli
    lista_modello1 = Loop.objects.filter(user=u)
    lista_modello2 = SamplePack.objects.filter(user=u)
    
    caricamenti = []
    for obj in chain(lista_modello1, lista_modello2):
        caricamenti.append({
            'obj': obj,
            'modeltype': obj.__class__.__name__,
        })
    
    caricamenti_ordinati = sorted(caricamenti, key=lambda x: x['obj'].uploaded_at, reverse=True)

    # Unisci e ordina per uploaded_at (decrescente)
    return caricamenti_ordinati