function isHidden(element) {
    return element.hasClass('d-none');
}

function fadeIn(q, done = () => {
}) {
    const element = $(q);
    if (!isHidden(element)) { return; }
    if (element.hasClass('d-none')) {
        element.hide();
        element.removeClass('d-none');
        element.fadeIn(100, done);
    }
}

function fadeOut(q, done = () => {
}) {
    const element = $(q);
    if (isHidden(element)) { return; }
    element.fadeOut(100, () => {
        element.hide();
        element.addClass('d-none');
        done();
    });
}



function whenDoneOne(xhr, on_done) {
    $.when(xhr).done(() => on_done());
}

function whenDone(xhr_list, on_done) {
    $.when.apply($, xhr_list).done(() => on_done());
}


function formatTimestamp(timestamp) {
  var date = new Date(timestamp * 1000); // Умножаем на 1000, так как в JavaScript используется миллисекунды
  var year = date.getFullYear();
  var month = ("0" + (date.getMonth() + 1)).slice(-2); // Добавляем ведущий ноль, если месяц < 10
  var day = ("0" + date.getDate()).slice(-2); // Добавляем ведущий ноль, если день < 10
  var hours = ("0" + date.getHours()).slice(-2); // Добавляем ведущий ноль, если час < 10
  var minutes = ("0" + date.getMinutes()).slice(-2); // Добавляем ведущий ноль, если минута < 10
  var seconds = ("0" + date.getSeconds()).slice(-2); // Добавляем ведущий ноль, если секунда < 10

  var formattedDate = day + "." + month + "." + year;
  var formattedTime = hours + ":" + minutes + ":" + seconds;

  return {date: formattedDate, time: formattedTime};
}
