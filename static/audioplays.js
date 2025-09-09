function registerPlay(modeltype, pk) {
      fetch(`/${modeltype}/${pk}/track_play/`, {
        method: "POST",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"), // Django CSRF
          "Content-Type": "application/json"
        },
        body: JSON.stringify({})
      }).then(response => {
        if (!response.ok) {
          console.error("Errore nel tracking dell'ascolto");
        }
      });
    }

    // Helper per leggere il CSRF cookie
    function getCookie(name) {
      let cookieValue = null;
      if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
          cookie = cookie.trim();
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    }