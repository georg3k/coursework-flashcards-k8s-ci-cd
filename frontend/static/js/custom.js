$(document).ready(function() {
    console.log("Ready!");

    if($("#yes_btn").length > 0)
    {
        session = $.ajax({ dataType: "json", url: '/api/sessions/' + window.location.pathname.split('/')[2], async: false })
        session = session.responseJSON;
        session.cards = JSON.parse(session.cards);

        card = $.ajax({ dataType: "json", url: '/api/cards/' + session.cards[0], async: false });
        card = card.responseJSON;

        
        score = $.ajax({ dataType: "json", url: '/api/scores/' + session.cards[0], async: false });
        score = score.responseJSON;

        progress = Math.floor(100 - session.cards.length / 20 * 100)

        $('#card_text')[0].innerHTML = card.front;
        $('#last')[0].innerHTML = 'Последний просмотр: ' + score.last + '<p>Уровень карточки: ' + score.score + '</p>';
        $('#pbar').css("width", progress + "%");

        $("#yes_btn").hide()
        $("#no_btn").hide()
        $("#title_back").hide()
        $("#fin_card").hide()

        $('#show_btn').click(function(event) {

            $('#card_text')[0].innerHTML = card.back;

            $("#show_btn").hide(200)
            $("#yes_btn").show(200)
            $("#no_btn").show(200)

            $("#title_front").hide(200)
            $("#title_back").show(200)
        });

        $('#yes_btn').click(function(event) {

            r = $.post('/api/sessions/' + window.location.pathname.split('/')[2] + '/' + session.cards[0] + '/yes');
            
            setTimeout(() =>
            {
                r = r.responseJSON;
                if(r['fin'] != undefined)
                {           
                    $("#study_card").hide(200)
                    $("#fin_card").show(200)
                }
            }, 200);


            $.ajax({ dataType: "json", url: '/api/sessions/' + window.location.pathname.split('/')[2] + '/' + session.cards[0] + '/yes' + window.location.pathname.split('/')[2], async: false })

            setTimeout(() => {

                session = $.ajax({ dataType: "json", url: '/api/sessions/' + window.location.pathname.split('/')[2], async: false })
                session = session.responseJSON;
                session.cards = JSON.parse(session.cards);

                if(session['fin'] != undefined)
                {           
                    $("#study_card").hide()
                    $("#fin_card").show()
                }
        
                card = $.ajax({ dataType: "json", url: '/api/cards/' + session.cards[0], async: false });
                card = card.responseJSON;
        
                
                score = $.ajax({ dataType: "json", url: '/api/scores/' + session.cards[0], async: false });
                score = score.responseJSON;
        
                progress = Math.floor(100 - session.cards.length / 20 * 100)
        
                $('#card_text')[0].innerHTML = card.front;
                $('#last')[0].innerHTML = 'Последний просмотр: ' + score.last + '<p>Уровень карточки: ' + score.score + '</p>';
                $('#pbar').css("width", progress + "%");

                $("#show_btn").show(200)
                $("#yes_btn").hide(200)
                $("#no_btn").hide(200)
                
                $("#title_front").show(200)
                $("#title_back").hide(200)

            }, 200);
        });

        $('#no_btn').click(function(event) {

            r = $.post('/api/sessions/' + window.location.pathname.split('/')[2] + '/' + session.cards[0] + '/no');

            setTimeout(() =>
            {
                r = r.responseJSON;
                if(r['fin'] != undefined)
                {           
                    $("#study_card").hide(200)
                    $("#fin_card").show(200)
                }
            }, 200);


            $.ajax({ dataType: "json", url: '/api/sessions/' + window.location.pathname.split('/')[2] + '/' + session.cards[0] + '/yes' + window.location.pathname.split('/')[2], async: false })

            setTimeout(() => {

                session = $.ajax({ dataType: "json", url: '/api/sessions/' + window.location.pathname.split('/')[2], async: false })
                session = session.responseJSON;
                session.cards = JSON.parse(session.cards);
        
                card = $.ajax({ dataType: "json", url: '/api/cards/' + session.cards[0], async: false });
                card = card.responseJSON;
        
                
                score = $.ajax({ dataType: "json", url: '/api/scores/' + session.cards[0], async: false });
                score = score.responseJSON;
        
                progress = Math.floor(100 - session.cards.length / 20 * 100)
        
                $('#card_text')[0].innerHTML = card.front;
                $('#last')[0].innerHTML = 'Последний просмотр: ' + score.last + '<p>Уровень карточки: ' + score.score + '</p>';
                $('#pbar').css("width", progress + "%");

                $("#show_btn").show(200)
                $("#yes_btn").hide(200)
                $("#no_btn").hide(200)
                
                $("#title_front").show(200)
                $("#title_back").hide(200)

            }, 200);
        });
    }

    if($("#decks_cont").length > 0)
    {
        decks = $.ajax({ dataType: "json", url: '/api/decks', async: false });
        decks = decks.responseJSON;

        insertion = '';

        for(let i = 0; i < decks.length; i++)
        {
            insertion += `
                <div class="row row-cols-1 row-cols-md-3 mb-3 text-center">
                    <div width="100" class="col">
                        <div class="card mb-4 rounded-3 shadow-sm border-primary">
                            <div class="card-header py-3 text-bg-primary border-primary">
                                <h3 class="my-0 fw-normal">${ decks[i].title }</h3>
                            </div>
                            <div class="card-body">
                                <p>${ decks[i].description }</p>
                                <a href="/decks/${ decks[i].id }/study"><button type="button" class="w-100 btn btn-lg btn-primary">Начать обучение</button></a>
                            </div>
                        </div>
                </div>
                </div>
            `
        }

        $('#decks_cont')[0].innerHTML = insertion;
    }

    if($("#study_title").length > 0)
    {
        deck = $.ajax({ dataType: "json", url: '/api/decks/' + window.location.pathname.split('/')[2], async: false });
        deck = deck.responseJSON;

        $('#study_title')[0].innerHTML = deck[0].title;
        $('#study_desc')[0].innerHTML = deck[0].description;
    }
});