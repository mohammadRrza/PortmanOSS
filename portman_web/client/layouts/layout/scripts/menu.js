$(document).ready(function(){
    $( ".nav-link" ).click(function() {
        //console.log(this);
        $('.nav-link').parent().parent().parent().addClass('active').removeClass('active');
        $(this).parent().parent().parent().addClass('active').addClass('active');
        //$('.nav-item').removeClass('active')
        //$(this).closest('.nav-item').addClass('active')
    });
    
});
