function upload_media_handler(callback, value, meta) {
    if (meta.filetype === 'media') {
        const input = document.createElement('input');
        input.setAttribute('type', 'file');
        input.setAttribute('accept', 'video/mp4,video/webm,video/ogg');

        input.addEventListener('change', function (e) {
            const file = e.target.files[0];
            const formData = new FormData();
            formData.append('file', file);

            let postUuid = null;
            const adminUuidField = document.querySelector('.field-uuid .readonly');
            if (adminUuidField) {
                postUuid = adminUuidField.innerText.trim();
            } else {
                const uuidInput = document.querySelector('input[name="uuid"]');
                if (uuidInput) postUuid = uuidInput.value;
            }

            if (postUuid) {
                formData.append('post_uuid', postUuid);
            }

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
