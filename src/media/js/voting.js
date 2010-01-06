jQuery.attachVoting = function() {
    $('#votacao_votar').click(function(){
        button = $(this);

        quesitos = ''

        $('input.valor-quesito:checked').each(function(){
            item = $(this);
            quesitos += item.attr('id') + '=' + item.val()
            quesitos += "&"
        });

        bodyContent = $.ajax({
                url: "vote",
                global: false,
                type: "POST",
                data: quesitos,
                dataType: "html",
                async: false,
                cache: false
            }
        ).responseText;
        $('#voting-result').html(bodyContent);

    });
};

