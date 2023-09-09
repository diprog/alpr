let videos = [];
let videos_map = {}; // dict[filename: str, video: dict]
let video_list_items = {};
let queue = []; // dict[filename: str, jquery]
const video_intervals = {};
whenDone([getVideos(), getQueue()], () => {
    if (videos.length) {
        for (const video of videos) {
            addVideoListItem(video);
        }
        fadeOut('#no_videos_added', () => fadeIn('#videos_list'));
    }
    updateTooltips();
    console.log(video_list_items);
    fadeOut('div.main_loader', () => fadeIn('div.main'));
});

function getVideos() {
    return ajax('get_videos', {}, (result) => {
        videos = result;
        console.log('videos', videos);
    })
}

function getQueue() {
    return ajax('get_queue', {}, (result) => {
        queue = result;
        console.log('queue', queue);
    })
}

function onAddVideoBtnClick() {
    $('#file_chooser').click();
}

function onVideoFileSelected(file_chooser) {
    const file = file_chooser[0].files[0];
    const callbacks = addVideoListItem({'filename': file.name}, true);
    uploadVideo(file, callbacks);
}


function getVideoQueuePosition(video) {
    for (const i in queue) {
        const filename = queue[i];
        if (video.filename === filename) {
            console.log(filename, video.filename);
            return i;
        }
    }
    return -1;
}

function addVideoListItem(video, initial = false, index = -1) {
    const videos_list = $('#videos_list');
    let video_list_item = $.tmpl('video_template', video);
    if (index >= 0) {
        const target_element = videos_list.children().eq(index);
        video_list_item = video_list_item.insertBefore(target_element);
    } else {
        video_list_item = video_list_item.appendTo(videos_list);
    }
    const status = video_list_item.find('div.status');
    const toggle_btn = video_list_item.find('button.toggle-btn');
    const export_btns = video_list_item.find('div.export-buttons').find('button');

    if (initial) {
        toggle_btn.prop('disabled', true);
        status.addClass('text-primary');
        status.html('<div class="spinner-grow spinner-grow-sm text-primary" role="status"></div> <span>Начало загрузки...</span>');
        const status_text = status.find('span');
        export_btns.prop('disabled', true);
        return {
            progress_callback: (percent_complete) => {
                status_text.html('Загрузка ' + percent_complete + '%...')
            },
            finish_callback: (video) => {
                status.removeClass('text-primary');
                status.html('');
                $.tmpl('awaiting_action_template').appendTo(status);
                updateTooltips();
                toggle_btn.prop('disabled', false);
                videos.push(video);
                videos_map[video.filename] = video;
                video_list_items[video.filename] = video_list_item;
                setVideoPreview(video, video_list_item);
                setVideoDatetime(video, video_list_item);
            }
        };
    } else {
        videos_map[video.filename] = video;
        video_list_items[video.filename] = video_list_item;
        setVideoPreview(video, video_list_item);
        setVideoDatetime(video, video_list_item);
        const queue_position = getVideoQueuePosition(video);

        if (video.searching_frame === -1) {
            if (queue_position >= 0) {
                $.tmpl('in_queue_template', {pos: Number(queue_position) + 1}).appendTo(status);
                video_list_item.find('div.alpr-buttons').addClass('d-none');
            } else {
                $.tmpl('awaiting_action_template').appendTo(status);
            }
            enableDisableExportButtons(video_list_item, false);
        } else if (video.searching_frame !== video.total_frames) {
            // Если видео в процессе обработки.
            console.log('йес')
            appendFoundPlatesToVideoDOM(video, video_list_item);
            findUniquePlates(video.filename, true);
            enableDisableExportButtons(video_list_item, false);
        } else if (video.filtered_plates.length) {
            // Если видео обработано.
            appendFilteredPlatesToVideoDOM(video, video_list_item);
            $.tmpl('found_plates_template', {amount: video.filtered_plates.length}).appendTo(status);
            fadeOut(video_list_item.find('span.no_plates'));
            video_list_item.find('div.alpr-buttons').addClass('d-none');
            enableDisableExportButtons(video_list_item, true);
            video_list_item.find('button.restart-video').removeClass('d-none');
        }
    }
}


function setVideoPreview(video, video_dom) {
    const video_preview = video_dom.find('div.video-preview');
    const background_image = 'min-width: 48px; min-height:48px; background-image: url("img/preview_' + video.filename + '.jpg"); background-position: center;'
    video_preview.attr('style', video_preview.attr('style') + background_image);
}

function setVideoDatetime(video, video_dom) {
    video_dom.find('small.time').html('<i class="bi bi-clock"></i> ' + getVideoDuration(video));

}

function getVideoIndex(video) {
    for (const i in videos) {
        if (videos[i].filename === video.filename) {
            return i;
        }
    }
    return -1;
}

function uploadVideo(file, callbacks) {
    const form_data = new FormData();
    form_data.append('video', file);

    const xhr = new XMLHttpRequest();
    fadeOut('#no_videos_added', () => fadeIn('#videos_list'));

    xhr.upload.addEventListener("progress", function (event) {
        if (event.lengthComputable) {
            const percentComplete = (event.loaded / event.total) * 100;
            callbacks.progress_callback(percentComplete.toFixed(2));
        }
    });

    xhr.addEventListener("load", function (result) {
        const video = JSON.parse(xhr.responseText);
        callbacks.finish_callback(video);
    });

    xhr.addEventListener("error", function () {
        fadeOut('#videos_list', () => fadeIn('#no_videos_added'));
    });

    xhr.open("POST", "/upload_video");
    xhr.send(form_data);
}

function toggleVideoListItem(toggle_btn) {
    const video_menu = toggle_btn.parent().parent().find('[name=video-menu]');
    if (!toggle_btn.prop('checked')) {
        toggle_btn.html('<i class="bi bi-caret-down"></i>')
        fadeIn(video_menu);
        toggle_btn.prop('checked', true);
    } else {
        toggle_btn.html('<i class="bi bi-caret-up"></i>')
        fadeOut(video_menu);
        toggle_btn.prop('checked', false);
    }

}

function updateTooltips() {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
}

function appendPlatesToVideoDOM(plates, video, video_dom) {
    const plates_div = video_dom.find('div.plates');
    for (const i in plates) {
        const plate = plates[i];
        fadeIn($.tmpl('plate_number_template', {
            index: Number(i) + 1,
            plate: plate.censored_text,
            video_filename: video.filename,
            frame_number: plate.frame_number

        }).appendTo(plates_div));
    }
    fadeIn(plates_div);
}

function appendFoundPlatesToVideoDOM(video, video_dom) {
    appendPlatesToVideoDOM(video.plates, video, video_dom);
}

function appendFilteredPlatesToVideoDOM(video, video_dom) {
    appendPlatesToVideoDOM(video.filtered_plates, video, video_dom);
}

function findUniquePlates(video_filename, from_load = false) {

    let video = videos_map[video_filename];
    console.log(video, video_filename);
    const video_list_item = video_list_items[video.filename]
    console.log(video_list_item);
    if (!from_load) {
        ajax('/find_unique_plates', {filename: video_filename}, (result) => {
            console.log(result)
            if (result.added_to_queue) {
                // Определяем, ушло ли видео в обработку. Если ушло, то начинаем отображать прогресс.
                if (!result.recognizing) {
                    trackVideoProgress(video, video_list_item);
                } else {
                    queue.push(video_filename);
                    const video_status = video_list_item.find('div.status');
                    video_status.html('');
                    $.tmpl('in_queue_template', {pos: Number(getVideoQueuePosition(video)) + 1}).appendTo(video_status);
                    video_list_item.find('div.alpr-buttons').addClass('d-none');
                }
            }
        });
    } else {
        trackVideoProgress(video, video_list_item);
    }
}

function trackVideoProgress(video, video_list_item) {
    const video_status = video_list_item.find('div.status');
    const plates_div = video_list_item.find('div.plates');
    const progress_desc = video_list_item.find('span.progress-desc');
    video_status.html('');
    const badge = $.tmpl('finding_plates_template').appendTo(video_status);
    fadeIn(badge);
    fadeIn(plates_div);
    fadeIn(progress_desc.parent());
    fadeIn(video_list_item.find('button.stop-video'));
    fadeOut(video_list_item.find('span.no_plates'));
    video_list_item.find('div.alpr-buttons').addClass('d-none');
    updateTooltips();


    let request_completed = true;
    const interval_id = setInterval(() => {
        if (request_completed) {
            request_completed = false;
            ajax('/get_video', {filename: video.filename}, (new_video) => {
                if (new_video.plates.length > video.plates.length) {
                    // Добавляем номер.
                    for (let i = video.plates.length; i < new_video.plates.length; i++) {
                        const plate = new_video.plates[i];
                        const templ = $.tmpl('plate_number_template', {
                            'index': i + 1,
                            'plate': plate.censored_text,
                            'video_filename': video.filename
                        }).appendTo(plates_div);
                        fadeIn(templ);
                    }
                }
                // Если поиск закончился.
                if (new_video.searching_frame === new_video.total_frames) {
                    fadeOut(progress_desc.parent());
                    video_status.html('');
                    // Добавляем номера без мусора.
                    plates_div.html('');
                    appendFilteredPlatesToVideoDOM(new_video, video_list_item);
                    clearInterval(interval_id);
                    // Включаем кнопки экспорта
                    enableDisableExportButtons(video_list_item, true)
                    $.tmpl('found_plates_template', {amount: video.filtered_plates.length}).appendTo(video_status);
                    if (queue.length) {
                        trackVideoProgress(videos_map[queue[0]], video_list_items[queue[0]]);
                        queue.shift();
                        updateQueueLabels();
                    }
                    video_list_item.find('button.restart-video').removeClass('d-none');
                } else {
                    // Обновляем полосу загрузки.
                    const percent = Math.ceil(new_video.searching_frame / new_video.total_frames * 100);
                    progress_desc.html('Обработано кадров: ' + new_video.searching_frame + '/' + new_video.total_frames + ' (' + percent + '%)');
                }

                video = new_video;
                updateVideo(video);


                request_completed = true;
            });
        }
    }, 1000);
    video_intervals[video.filename] = interval_id;
}

function enableDisableExportButtons(video_dom, enable = true) {
    const export_buttons_div = video_dom.find('div.export-buttons');
    const export_btns = export_buttons_div.find('button');
    const info_span = export_buttons_div.find('span.info');
    if (enable) {
        fadeOut(info_span);
        export_btns.prop('disabled', false);
    } else {
        export_btns.prop('disabled', true);
        info_span.html('Сначала выполните поиск номеров, чтобы было что экспортировать.');
        fadeIn(info_span);
    }

}

function updateQueueLabels() {
    for (const video of videos) {
        const video_list_item = video_list_items[video.filename];
        const queue_position = Number(getVideoQueuePosition(video));
        const queue_status_badge = video_list_item.find('div.status').find('button');
        if (queue_position >= 0) {
            queue_status_badge.html('В очереди (' + (queue_position + 1) + ')');
        }
    }
}

function updateVideo(video_from_map) {
    for (const index in videos) {
        const video = videos[index];
        if (video.filename === video_from_map.filename) {
            videos[index] = video_from_map;
            break;
        }
    }
}

function downloadExcel(video_filename) {

    ajax('/download_excel', {filename: video_filename}, (response) => {
        const blob = new Blob([response], {type: "application/octetstream"});
        const url = window.URL || window.webkitURL;
        link = url.createObjectURL(blob);
        const a = $("<a />");
        a.attr("download", video_filename + '.xlsx');
        a.attr("href", link);
        $("body").append(a);
        a[0].click();
        $("body").remove(a);

    }, {
        dataType: null, xhr: function () {
            var xhr = new XMLHttpRequest();
            xhr.onreadystatechange = function () {
                if (xhr.readyState == 2) {
                    if (xhr.status == 200) {
                        xhr.responseType = "blob";
                    } else {
                        xhr.responseType = "text";
                    }
                }
            };
            return xhr;
        },
    });
}

function downloadTxt(video_filename) {

    ajax('/download_txt', {filename: video_filename}, (response) => {
        var blob = new Blob([response], {type: 'text/plain'});
        const url = window.URL || window.webkitURL;
        link = url.createObjectURL(blob);
        const a = $("<a />");
        a.attr("download", video_filename + '.txt');
        a.attr("href", link);
        $("body").append(a);
        a[0].click();
        $("body").remove(a);

    }, {
        dataType: null, xhr: function () {
            var xhr = new XMLHttpRequest();
            xhr.onreadystatechange = function () {
                if (xhr.readyState == 2) {
                    xhr.responseType = "text";
                }
            };
            return xhr;
        },
    });
}

function deleteVideo(video_filename) {

    ajax('/delete_video', {filename: video_filename}, (response) => {
        if (response.success) {
            delete videos_map[video_filename];
            const video_list_item = video_list_items[video_filename];
            video_list_item.remove();
            delete video_list_items[video_filename];
            for (const i in videos) {
                const video = videos[i];
                if (video.filename === video_filename) {
                    videos.splice(i, 1);
                    break;
                }
            }
            if (!videos.length) {
                fadeOut('#videos_list', () => fadeIn('#no_videos_added'));
            }
        }
    });
}

function downloadCarImagesZip(video_filename) {
    const video_list_item = video_list_items[video_filename];
    console.log(video_list_item);
    const download_frames_btn = video_list_item.find('button.download-frames-btn');
    const download_frames_btn_html = download_frames_btn.html();
    download_frames_btn.prop('disabled', true);
    download_frames_btn.html('Пожалуйста, подождите...');
    ajax('/download_cars', {filename: video_filename}, (response) => {
        const blob = new Blob([response], {type: "application/octetstream"});
        const url = window.URL || window.webkitURL;
        link = url.createObjectURL(blob);
        const a = $("<a />");
        a.attr("download", video_filename + '.zip');
        a.attr("href", link);
        $("body").append(a);
        a[0].click();
        $("body").remove(a);
        download_frames_btn.html(download_frames_btn_html);
        download_frames_btn.prop('disabled', false);

    }, {
        dataType: null, xhr: function () {
            var xhr = new XMLHttpRequest();
            xhr.onreadystatechange = function () {
                if (xhr.readyState == 2) {
                    if (xhr.status == 200) {
                        xhr.responseType = "blob";
                    } else {
                        xhr.responseType = "text";
                    }
                }
            };
            return xhr;
        },
    });
}

function getVideoDuration(video) {
    const totalFrames = video.total_frames;
    const fps = video.fps;
    const durationSeconds = totalFrames / fps;

    const hours = Math.floor(durationSeconds / 3600);
    const minutes = Math.floor((durationSeconds % 3600) / 60);
    const seconds = Math.floor(durationSeconds % 60);

    let duration = "";

    if (hours > 0) {
        duration += hours.toString().padStart(2, "0") + ":";
    }

    duration += minutes.toString().padStart(2, "0") + ":" + seconds.toString().padStart(2, "0");

    return duration;
}

function resetVideo(video) {
    const video_index = getVideoIndex(video);
    const video_list_item = video_list_items[video.filename];
    addVideoListItem(video, false, video_index);
    videos[video_index] = video;
    video_list_item.remove();
    if (queue.length) {
        trackVideoProgress(videos_map[queue[0]], video_list_items[queue[0]]);
        queue.shift();
        updateQueueLabels();
    }
}

function stopVideo(video_filename) {
    const video_list_item = video_list_items[video_filename];
    video_list_item.find('button.stop-video').html('<div class="spinner-border spinner-border-sm" role="status"></div>')
    ajax('/stop_video', {filename: video_filename}, (video) => {
        clearInterval(video_intervals[video_filename]);
        resetVideo(video);
    });
}

function restartVideo(video_filename) {
    const video_list_item = video_list_items[video_filename];
    video_list_item.find('button.restart-video').html('<div class="spinner-border spinner-border-sm" role="status"></div>')
    ajax('/reset_video', {filename: video_filename}, (video) => {

        resetVideo(video);
    });
}