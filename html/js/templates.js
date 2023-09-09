$('template').each(function () {
    const template_name = $(this).attr('id');
    console.log(template_name);
    $.template(template_name, $(this));
});