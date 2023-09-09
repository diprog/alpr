

function ajax(path, data = {}, on_success = null, additional_options={}) {
    const url = path;
    const default_options = {
        type: 'POST',
        dataType: 'json',
        contentType: 'application/json; charset=UTF-8',
        data: JSON.stringify(data),
        success: function (result) {
            if (on_success != null) {
                on_success(result);
            }

        },
        error: function (xhr, status, error) {
            console.log('error', xhr, status, error);
        }
    }
    const options = {...default_options, ...additional_options};
    return $.ajax(url, options);
}