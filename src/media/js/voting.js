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
jQuery.updateResults = function(el) {
    var json = $.ajax({
        url: "/result",
        dataType:"json",
        async: false,
        cache:false,
        success: function(data){
            el.html("votos "+data.votos);
        }
    }).responseText;
};

