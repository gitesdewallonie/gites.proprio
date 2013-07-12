jQuery(document).ready(function($) {

    $("#gallery-edition").sortable({
        containment: "parent",
        cursor: "move",
        items: "> .photo",
        opacity: 0.6,
        stop: function( event, ui ) {
            var sortedDivs = $(".photo").sortable("toArray");
            var sortedIds = "";
            $.each(sortedDivs, function() {
                if (sortedIds.length > 0) sortedIds = sortedIds + '|' + this.id;
                else sortedIds = this.id;
            });
            $("#images-orders").val(sortedIds);
        }
    });
    $("#gallery-edition").disableSelection();

    $(".delete").click(function(){
        $(this).parents(".photo").fadeOut(300, function(){ 
            $(this).remove();
            var sortedDivs = $(".photo").sortable("toArray");
            var sortedIds = "";
            $.each(sortedDivs, function() {
                if (sortedIds.length > 0) sortedIds = sortedIds + '|' + this.id;
                else sortedIds = this.id;
            });
            $("#images-orders").val(sortedIds);
        });
    });

    $('#fileupload').fileupload({
        url: 'upload-image',
        dataType: 'json',
        done: function (e, data) {
            if (data.result.status == -1)
            {
                $("#error-message").text(data.result.message);
                $("#error-message").show();
            }
            else {
                $("#gallery-edition-fieldset").load("crop-image", {'hebPk': data.result.hebPk,
                                                                   'originalFile': data.result.filename,
                                                                   'status': data.result.status,
                                                                   'height': data.result.height,
                                                                   'width': data.result.width,
                                                                   'message': data.result.message});
            }
        },
        progressall: showProgress
    });

    $('#fileupload-proprio').fileupload({
        url: 'upload-image-proprio',
        dataType: 'json',
        done: function (e, data) {
            if (data.result.status == -1)
            {
                $("#error-message").text(data.result.message);
                $("#error-message").show();
            }
            else {
                $("#proprio-photo-edition-fieldset").load("crop-image-proprio", {'proPk': data.result.proPk,
                                                                                 'originalFile': data.result.filename,
                                                                                 'status': data.result.status,
                                                                                 'height': data.result.height,
                                                                                 'width': data.result.width,
                                                                                 'message': data.result.message});
            }
        },
        progressall: showProgress
    });

});


function showProgress(e, data) {
    $("#error-message").hide();
    $("#progress").show();
    var progress = parseInt(data.loaded / data.total * 100, 10);
    var percentVal = progress + '%';
    $('#progress .bar').css(
        'width',
        progress + '%'
    );
    $('#progress .bar').html(percentVal);
};

function checkCoords() {
    if (parseInt($('#w').val(), 10) > 0) return true;
    alert("Veuillez d'abord couper l'image avant de la sauvegarder.");
    return false;
};
