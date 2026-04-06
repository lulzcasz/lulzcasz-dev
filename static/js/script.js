document.addEventListener("click", function(event) {
    // Check if the clicked element is an IMG and is inside .article-content
    if (event.target.tagName === 'IMG' && event.target.closest('.article-content')) {
        const fullResUrl = event.target.dataset.original || event.target.src;
        openFullscreen(fullResUrl);
    }
});

function openFullscreen(imageUrl) {
    var overlay = document.getElementById('fullscreenOverlay');
    var img = document.getElementById('overlayImage');
    
    if (overlay && img) {
        img.src = imageUrl;
        overlay.style.display = "flex";
    }
}

function closeFullscreen() {
    var overlay = document.getElementById('fullscreenOverlay');
    if (overlay) {
        overlay.style.display = "none";
        document.getElementById('overlayImage').src = '';
    }
}
