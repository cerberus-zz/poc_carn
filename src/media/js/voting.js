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

        //$.updateResults($('#voting-result'));
    });
};
jQuery.updateResults = function(el) {
    var json = $.ajax({
        url: "/result",
        dataType:"json",
        async: false,
        cache:false,
        success: function(data){
            template = "votos: @@votos@@<br />harmonia: @@harmonia@@<br />evolucao: @@evolucao@@<br />mestre sala: @@ms_pb@@"
            el.html(template.replace('@@votos@@', data.votos)
                            .replace('@@harmonia@@', data.nota_harmonia)
                            .replace('@@evolucao@@', data.nota_evolucao)
                            .replace('@@ms_pb@@', data.nota_ms_pb)
                            );
        }
    }).responseText;
};

