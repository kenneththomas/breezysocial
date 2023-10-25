$(document).ready(function () {
    $("#tweetForm").submit(function (e) {
        e.preventDefault();
        const postData = $(this).serialize();
        $.post("your_post_url_here", postData, function (response) {
            $("#message").html(`<p>${response.message}</p>`);
        }).fail(function (response) {
            $("#message").html(`<p>Error: ${response.responseJSON.error}</p>`);
        });
    });
});