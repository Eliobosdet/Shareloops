from django.utils import timezone
from django.http import HttpResponse, JsonResponse, FileResponse
from django.apps import apps
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView, ListView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import *
from .utils import get_ordered_loads
import logging
# from django.contrib.auth.forms import AuthenticationForm

logger = logging.getLogger(__name__)

### CBV ###

class ProfileDetailView(DetailView):
    model = User
    template_name = 'user/profile.html'
    context_object_name = 'user'
    login_url = '/login/'  # Specifica l'URL di login

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # logger.debug(f"ProfileDetailView - self.object: {self.object}")
        # logger.debug(f"ProfileDetailView - URL kwargs: {self.kwargs}")
        # logger.debug(f"ProfileDetailView - request.user: {self.request.user}")
        
        profile, _ = UserProfile.objects.get_or_create(user=self.object)
        context['profImg'] = profile
        context['total_likes_received'] = profile.total_likes_received()
        context['total_comments_received'] = profile.total_comments_received()
        context['total_downloads_received'] = profile.total_downloads_received()
        context['total_audioplays_received'] = profile.total_audioplays_received()
        # ✅ Popola il form con l'istanza esistente
        context['profForm'] = ProfileUpdateForm(instance=profile)
        context['loads'] = get_ordered_loads(self.object)
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if not request.user.is_authenticated:
            messages.error(request, "Devi essere loggato per modificare il profilo")
            return redirect('login')  # o redirect alla pagina di login

        if self.object != request.user:
            messages.error(request, "Non autorizzato")
            return redirect('profile', pk=request.user.pk)

        profile, created = UserProfile.objects.get_or_create(user=self.object)  # Aggiorna nome modello
        old_image = profile.image 
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

        if form.is_valid():
            try:
                # Elimina la vecchia immagine solo se diversa da quella default
                if (old_image and 
                    old_image.name != 'defaultProfileImage.jpg' and 
                    os.path.exists(old_image.path)):
                    os.remove(old_image.path)
                
                form.save()
                messages.success(request, "Profilo aggiornato!")
                return redirect('profile', pk=self.object.id)
                
            except Exception as e:
                messages.error(request, f"Errore: {str(e)}")
        else:
            messages.error(request, "Form non valido")

        context = self.get_context_data()
        context['profForm'] = form
        return self.render_to_response(context)

class GenericDetailView(DetailView):
    template_name = 'uploadableitem_detail.html'


    def get_object(self):
        modeltype = self.kwargs.get('modeltype').lower()
        pk = self.kwargs.get('pk')

        # Determina il modello in base al modeltype
        if modeltype == 'loop':
            model = Loop
        elif modeltype == 'samplepack':
            model = SamplePack
        else:
            raise ValueError("Modeltype non valido")

        # Recupera l'oggetto
        return get_object_or_404(model, pk=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['item'] = self.object
        context['modeltype'] = self.kwargs.get('modeltype')
        context['commentForm'] = CommentForm()
        context['comments'] = Comment.objects.filter(
            content_type=ContentType.objects.get_for_model(self.object),
            object_id=self.object.pk
        ).order_by('-created_at')
        if self.request.user.is_authenticated:
            context['liked_comments'] = self.request.user.likes_comments.all()
        else:
            context['liked_comments'] = []
        return context

class LoopsListView(ListView):
    model = Loop
    template_name = 'loops.html'
    context_object_name = 'loops'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.user.is_authenticated:
            context['liked_loops'] = self.request.user.likes_loop.all()
        else:
            context['liked_loops'] = []
        return context

class SamplePacksListView(ListView):
    model = SamplePack
    template_name = 'samplepacks.html'
    context_object_name = 'samplepacks'

### FBV ###

def home(request, *args, **kwargs):
    tmp_name="home.html"
    uploads = get_ordered_loads()

    context = {
        'uploads': uploads,
        'filterForm': FilterForm(request.GET)
    }

    return render(request,tmp_name, context)

def register_view(request, *args, **kwargs):
    if request.method == 'POST':
        form = CustomRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = CustomRegisterForm()
    return render(request, 'auth/register.html', {'form': form})

def login_view(request, *args, **kwargs):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user is not None:
                logger.info(f"User {user.username} logged in successfully.")  # Log di debug
                login(request, user)
                return redirect('home')
            else:
                logger.warning("Form valid but user is None.")
        else:
            logger.warning(f"Login form invalid: {form.errors}")
    else:
        form = CustomLoginForm()
    return render(request, 'auth/login.html', {'form': form})


def logout_view(request, *args, **kwargs):
    logout(request)
    return redirect('home')

@login_required
def change_password(request, pk):
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # mantiene l'utente loggato
            messages.success(request, 'La tua password è stata cambiata con successo!')
            return redirect('profile', pk=request.user.pk)
        else:
            # Se ci sono errori, aggiungi messaggi di errore
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, "user/password_change_form.html", {"form": form})

@login_required
@require_POST
def remove_profile_image(request, pk=None):
    profile = request.user.userprofile
    profile.image.delete(save=False)  # elimina il file fisico
    profile.image = 'defaultProfileImage.jpg'  # imposta l'immagine predefinita
    profile.save()
    return redirect('profile', pk=pk)

@login_required
def upload(request):
    return render(request, 'user/upload.html')        

@login_required
def upload_loop(request):
    if request.method == 'POST':
        form = LoopForm(request.POST, request.FILES)
        if form.is_valid():
            loop = form.save(commit=False)
            loop.user = request.user
            loop.save()
            form.save_m2m()  # Salva le relazioni many-to-many (inclusi i tag)

            url = reverse('uploadable_detail', args=["loop", loop.id])
            messages.success(
                request,
                f'Prodotto "{loop.title}" caricato con successo! <a href="{url}">Visualizza prodotto</a>',
                extra_tags='safe'
            )
            form = LoopForm()
    else:
        form = LoopForm()
    return render(request, 'user/upload_loop.html', {'form': form})

@login_required
def upload_samplepack(request):
    if request.method == 'POST':
        form = SamplePackForm(request.POST, request.FILES)
        if form.is_valid():
            samplepack = form.save(commit=False)
            samplepack.user = request.user
            samplepack.save()
            form.save_m2m()  # Salva le relazioni many-to-many (inclusi i tag)

            url = reverse('uploadable_detail', args=["samplepack", samplepack.id])
            messages.success(
                request, 
                f'Prodotto "{samplepack.title}" caricato con successo! <a href="{url}">Visualizza prodotto</a>',
                extra_tags='safe'
            )
            form = SamplePackForm()
    else:
        form = SamplePackForm()
    return render(request, 'user/upload_samplepack.html', {'form': form})

@login_required
def edit_uploadable(request, pk, modeltype):
    template = 'user/edit_uploadable.html'
    if modeltype == 'Loop':
        obj = get_object_or_404(Loop, pk=pk, user=request.user)
        form_class = LoopForm
        context_name = 'loop'
    elif modeltype == 'SamplePack':
        obj = get_object_or_404(SamplePack, pk=pk, user=request.user)
        form_class = SamplePackForm
        context_name = 'samplepack'
    else:
        messages.error(request, "Invalid model type.")
        return redirect('profile', pk=request.user.pk)

    if request.method == 'POST':
        if request.POST.get('action') == 'back':
            return redirect('profile', pk=request.user.pk)
        form = form_class(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            updated_obj = form.save()  # ← Il form gestisce automaticamente i tag
            url = reverse('uploadable_detail', args=[modeltype.lower(), updated_obj.id])
            messages.success(
                request, 
                f'Prodotto "{updated_obj.title}" modificato con successo! <a href="{url}">Visualizza prodotto</a>',
                extra_tags='safe'
            )
            return redirect('profile', pk=request.user.id)
    else:
        form = form_class(instance=obj)
    return render(request, template, {'form': form, context_name: obj})

@login_required
@require_POST
def delete_uploadable(request, pk, modeltype):
    if modeltype == 'Loop':
        load = get_object_or_404(Loop, pk=pk, user=request.user)
    elif modeltype == 'SamplePack':
        load = get_object_or_404(SamplePack, pk=pk, user=request.user)
    else:
        messages.error(request, "Invalid model type.")
        return redirect('profile', pk=request.user.pk)

    load.delete()
    messages.success(request, f"{modeltype} deleted successfully!")
    return redirect('profile', pk=request.user.pk)

@login_required
def like_uploadable(request, modeltype, pk):
    if request.method == "POST":
        # Recupera il modello dinamicamente
        try:
            model = apps.get_model('app', modeltype)  # 'app' è il nome della tua app
        except LookupError:
            return JsonResponse({"error": "Modello non trovato"}, status=404)

        # Recupera l'oggetto
        try:
            obj = model.objects.get(pk=pk)
        except model.DoesNotExist:
            return JsonResponse({"error": "Oggetto non trovato"}, status=404)

        # Gestisci il like
        user = request.user
        if user in obj.likes.all():
            obj.likes.remove(user)
            liked = False
        else:
            obj.likes.add(user)
            liked = True

        return JsonResponse({
            "liked": liked,
            "likes_count": obj.likes.count()
        })

    return JsonResponse({"error": "Metodo non consentito"}, status=405)


@login_required
def like_comment(request, comment_id):
    if request.method == "POST":
        comment = get_object_or_404(Comment, id=comment_id)
        user = request.user

        if user in comment.likes.all():
            comment.likes.remove(user)
            liked = False
        else:
            comment.likes.add(user)
            liked = True

        return JsonResponse({
            "liked": liked,
            "likes_count": comment.likes.count()
        })

    return JsonResponse({"error": "Metodo non consentito"}, status=405)

@login_required
@require_POST  
def add_comment(request, pk, modeltype, parent_id=None):
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            content_type = ContentType.objects.get(model=modeltype.lower())
            obj = get_object_or_404(content_type.model_class(), pk=pk)
            comment = form.save(commit=False)
            comment.user = request.user
            comment.content_type = content_type
            comment.object_id = obj.pk
            if parent_id:
                comment.parent = get_object_or_404(Comment, pk=parent_id)
            comment.save()
            messages.success(request, "Commento aggiunto con successo!")
        else:
            messages.error(request, "Errore nel commento.")
    return redirect('uploadable_detail', modeltype=modeltype, pk=pk)

@login_required
@require_POST  
def delete_comment(request, pk, modtype, upl_pk):
    comment = get_object_or_404(Comment, pk=pk)
    if request.user == comment.user:
        comment.delete()
        messages.success(request, "Commento eliminato con successo!")
    else:
        messages.error(request, "Non puoi eliminare questo commento.")
    return redirect('uploadable_detail', modeltype=modtype, pk=upl_pk)

@login_required
def audio_file_download(request, modeltype, pk):
    content_type = ContentType.objects.get(model=modeltype.lower())
    item = get_object_or_404(content_type.model_class(), pk=pk)

    # Registra il download se non è l'autore
    if request.user != item.user:
        _, created = Download.objects.get_or_create(
            user=request.user,
            content_type=content_type,
            object_id=item.pk
        )

    # Serve il file direttamente (senza redirect)
    file = item.audio_file.open('rb')
    response = FileResponse(file, content_type="audio/mpeg")
    response['Content-Disposition'] = f'attachment; filename="{item.audio_file.name}"'
    return response

def track_audio_play(request, modeltype, pk):
    content_type = ContentType.objects.get(model=modeltype.lower())
    item = get_object_or_404(content_type.model_class(), pk=pk)

    # Ottieni l'IP dell'utente
    ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
    if ip_address:
        ip_address = ip_address.split(',')[0].strip()
    else:
        ip_address = request.META.get('REMOTE_ADDR')

    # Se l'utente è loggato, usa user, altrimenti usa solo l'IP
    user = request.user if request.user.is_authenticated else None

    # Cerca un AudioPlay per utente o IP
    audioplay, created = AudioPlay.objects.get_or_create(
        user=user,
        ip_address=ip_address,
        content_type=content_type,
        object_id=item.pk,
        defaults={'played_at': timezone.now()}
    )

    # Aggiorna played_at solo se non è stato creato oggi
    if not created and audioplay.played_at.date() < timezone.now().date():
        audioplay.played_at = timezone.now()
        audioplay.save(update_fields=['played_at'])

    return redirect(item.audio_file.url)
