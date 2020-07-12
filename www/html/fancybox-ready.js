/*
*  FancyBox needs to be ready on document ready
*/
$(document).ready(function() {

    $('.fancybox').fancybox();

    $("a.largefancybox").fancybox({
        width : '80%',
        height : '80%'
    });

/* TESTS FOR AUTOMATIC OPENING AND CLOSING
                $(".test").fancybox();
                $(".test").hover(function() {
                    $(this).click();
                    $("#fancybox-overlay").remove(); //remove the overlay so you can close when hover off.
                }, function() {
                    $.fancybox.close();
                });
*/
});

