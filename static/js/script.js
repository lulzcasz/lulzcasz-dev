document.addEventListener('DOMContentLoaded', function() {
    if (typeof mediumZoom !== 'undefined') {
        mediumZoom('.zoomable', {
            margin: 24,
            background: '#000000ee' 
        });
    }
});
