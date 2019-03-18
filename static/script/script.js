'use strict';

// Run after webpage has loaded
$(document).ready(function() {
    // When 'Punctuate' button is clicked, extract form data and post it via ajax to required endpoint
    $('#input_text').click(function() {
       const form = new FormData(document.getElementById('text_in'));
       $.ajax({
           type: 'POST',
           url: '/punct_text',
           data: form,
           processData: false, // Required for form data
           contentType: false // Required for form data
       })
        // After processing by endpoint
       .done(function(data){
        // Display error message
        if (data.error) {
            $('#text_errorAlert').text(data.error).show();
            $('#text_successAlert').hide();
        }
        // Display punctuated sentence and highlight punctuation
        else {
            $('#text_successAlert').text(data.result).show();
            let txt = $('#text_successAlert').text();
            let r = "<mark class=\"highlighted\">$1</mark>"
            txt = txt.replace(/([?!.,;:])/g, r);
            $('#text_successAlert').html(txt);
            $('#text_errorAlert').hide();
        }
       });
    });
});