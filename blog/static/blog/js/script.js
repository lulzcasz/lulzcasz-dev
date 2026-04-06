document.addEventListener("DOMContentLoaded", function() {
    const contentContainer = document.querySelector('.article-content');

    if (contentContainer) {
        contentContainer.addEventListener('click', function(event) {
            if (event.target.tagName === 'IMG') {
                const fullResUrl = event.target.dataset.original || event.target.src;
                openFullscreen(fullResUrl);
            }
        });
    }
});

function openFullscreen(imageUrl) {
  var overlay = document.getElementById('fullscreenOverlay');
  var img = document.getElementById('overlayImage');
  
  img.src = imageUrl;
  
  overlay.style.display = "flex";
}

function closeFullscreen() {
  var overlay = document.getElementById('fullscreenOverlay');
  overlay.style.display = "none";
  document.getElementById('overlayImage').src = '';
}
