document.addEventListener("DOMContentLoaded", function () {
    // Funzione per ottenere il token CSRF dai cookie
    function getCookie(name) {
      let cookieValue = null;
      if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    }
  
    const csrftoken = getCookie('csrftoken');
  
    document.querySelectorAll(".like-icon").forEach(icon => {
      icon.addEventListener("click", function () {
        const loadId = this.getAttribute("data-id");
        const modelType = this.getAttribute("data-type");
        const likeCountSpan = this.nextElementSibling; // assume <span> is right after the icon
  
        const url = `/like/${loadId}/${modelType}/`;

        fetch(url, {
          method: "POST",
          headers: {
            "X-CSRFToken": csrftoken,
            "Content-Type": "application/json"
          }
        })
        .then(response => {
          if (response.ok) return response.json();
          else throw new Error("Errore nella richiesta AJAX");
        })
        .then(data => {
          // Cambia stile dell'icona
          if (data.liked) {
            this.classList.remove("far");
            this.classList.add("fas");
          } else {
            this.classList.remove("fas");
            this.classList.add("far");
          }
          // Aggiorna conteggio like
          likeCountSpan.textContent = data.likes_count;
        })
        .catch(error => {
          console.error("Errore:", error);
        });
      });
    });
  });