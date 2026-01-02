// Markdown preview functionality (vanilla JS, no jQuery)
var previewTimer = null;

function previewAjax(textareaId, divId, show_raw = false) {
    var textarea = document.getElementById(textareaId);
    var div = document.getElementById(divId);

    if (!textarea || !div) return;

    // Show raw textarea content while waiting for server-rendered Markdown
    if (show_raw) {
        // Escape HTML tags to prevent XSS
        var escaped = textarea.value
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
        div.innerHTML = '<span class="preview-raw-markup">' + escaped + '</span>';
    }

    // Debounce: clear previous timer and set new one
    if (previewTimer) {
        clearTimeout(previewTimer);
    }
    previewTimer = setTimeout(function() {
        sendPreview(textareaId, divId);
    }, 800);
}

function sendPreview(textareaId, divId) {
    var textarea = document.getElementById(textareaId);
    var div = document.getElementById(divId);

    if (!textarea || !div) return;

    var formData = new FormData();
    formData.append('data', textarea.value);

    fetch('/markup-editor-preview', {
        method: 'POST',
        body: formData,
        cache: 'no-store'
    })
    .then(function(response) {
        return response.text();
    })
    .then(function(html) {
        div.innerHTML = html;
    })
    .catch(function(error) {
        console.error('Preview error:', error);
    });
}
