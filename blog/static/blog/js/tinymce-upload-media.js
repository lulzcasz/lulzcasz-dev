function upload_media_handler(callback, value, meta) {
    if (meta.filetype === 'media') {
        const input = document.createElement('input');
        input.setAttribute('type', 'file');
        input.setAttribute('accept', 'video/mp4,video/webm,video/ogg');

        input.addEventListener('change', function (e) {
            const file = e.target.files[0];
            const formData = new FormData();
            formData.append('file', file);

            let articleUuid = null;
            const uuidMatch = document.body.textContent.match(/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/i);

            if (uuidMatch) {
                articleUuid = uuidMatch[0];
            } else {
                const uuidInput = document.querySelector('input[name="uuid"]');
                if (uuidInput) articleUuid = uuidInput.value;
            }

            if (articleUuid) {
                formData.append('article_uuid', articleUuid);
            }
            
            console.log("UUID Video:", articleUuid);

            document.body.style.cursor = 'wait';

            fetch('/tinymce/upload-video/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: formData
            })
            .then(response => {
                document.body.style.cursor = 'default';
                if (!response.ok) {
                    throw new Error('HTTP Error: ' + response.status);
                }
                return response.json();
            })
            .then(json => {
                if (!json || typeof json.location != 'string') {
                    throw new Error('Invalid JSON');
                }

                callback(json.location, { title: file.name });
            })
            .catch(error => {
                document.body.style.cursor = 'default';
                console.error('Video upload failed:', error);
                alert('Falha ao fazer upload do vídeo.');
            });
        });

        input.click();
    }
}
