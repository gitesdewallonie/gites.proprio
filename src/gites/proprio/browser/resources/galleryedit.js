jQuery(document).ready(function($) {

    $('#fileupload').fileupload({
        url: 'upload-image',
        dataType: 'json',
        done: function (e, data) {
            $("#gallery-form").load("crop-image", {'hebPk': data.result.hebPk,
                                                   'originalFile': data.result.filename,
                                                   'imageName': data.result.imageName});
        },
        progressall: function (e, data) {
            var progress = parseInt(data.loaded / data.total * 100, 10);
            var percentVal = progress + '%';
            $('#progress .bar').css(
                'width',
                progress + '%'
            );
            $('#progress .bar').html(percentVal);
        }
    });

});
