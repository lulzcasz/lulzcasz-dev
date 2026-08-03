function getCookie(name) {
    let cookieArray = document.cookie.split(';');

    for (let i = 0; i < cookieArray.length; i++) {
        let cookie = cookieArray[i].trim();
        if (cookie.startsWith(name + '=')) {
            return decodeURIComponent(cookie.substring(name.length + 1));
        }
    }
    return null;
}

function upload_image(blobInfo, progress) {
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.withCredentials = false;
        const url = `/tinymce/upload-image/`;
        
        xhr.open('POST', url);
        xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));

        xhr.upload.onprogress = (e) => {
            progress(e.loaded / e.total * 100);
        };

        xhr.onload = () => {
            if (xhr.status === 403) {
                reject({ message: 'HTTP Error: ' + xhr.status, remove: true });
                return;
            }
            if (xhr.status < 200 || xhr.status >= 300) {
                reject('HTTP Error: ' + xhr.status);
                return;
            }

            const json = JSON.parse(xhr.responseText);
            if (!json || typeof json.location != 'string') {
                reject('Invalid JSON: ' + xhr.responseText);
                return;
            }
            resolve(json.location);
        };

        xhr.onerror = () => {
            reject('Image upload failed due to a XHR Transport error. Code: ' + xhr.status);
        };

        const formData = new FormData();
        formData.append('file', blobInfo.blob(), blobInfo.filename());

        let articleUuid = null;

        const adminUuidField = document.querySelector('.field-uuid .readonly');
        if (adminUuidField) {
            articleUuid = adminUuidField.innerText.trim();
        }

        else {
            const uuidInput = document.querySelector('input[name="uuid"]');
            if (uuidInput) articleUuid = uuidInput.value;
        }

        if (articleUuid) {
            formData.append('article_uuid', articleUuid);
        }

        console.log(articleUuid);

        xhr.send(formData);
    });
}
