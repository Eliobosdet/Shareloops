const input = document.querySelector('input[name=tags]');
      const tagify = new Tagify(input, {
          whitelist: [],
          dropdown: {
              enabled: 1,
              classname: 'tags-look',
              maxItems: 10,
              position: 'text',
              closeOnSelect: false,
          }
      });

      // Autocomplete AJAX
      tagify.on('input', function(e){
          let value = e.detail.value;
          fetch(`/api/tags/?q=${value}`)
              .then(res => res.json())
              .then(data => {
                  tagify.settings.whitelist = data.map(obj => obj.value);
                  tagify.dropdown.show.call(tagify, value); // show the suggestions
              });
      });