jQuery.loadIndex = function(element, callback) {
    element.load('/include', function(){
        Recaptcha.create("{{public_key}}", 'recaptcha_place', {
                tabindex: 0,
                callback: Recaptcha.focus_response_field
          });

        callback();
    });
};

