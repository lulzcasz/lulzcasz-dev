document.addEventListener("DOMContentLoaded", function() {
    const postContent = document.querySelector('.post-content');
    const asideElement = document.querySelector('aside');
    const relatedPosts = document.querySelectorAll('.related-post-item');
    const bottomContainer = document.getElementById('bottom-related-container');
    const bottomSection = document.getElementById('bottom-related-section');
    
    if (!postContent || !asideElement || relatedPosts.length === 0 || !bottomContainer) return;

    function adjustSidebarContent() {
        const viewportHeight = window.innerHeight;
        const maxPostHeight = postContent.offsetHeight;

        const sidebarContainer = document.getElementById('related-posts-container');
        relatedPosts.forEach(post => {
            post.classList.add('hidden');
            sidebarContainer.appendChild(post);
        });

        bottomContainer.innerHTML = '';
        bottomSection.classList.add('hidden');

        let movedToBottomCount = 0;

        for (let i = 0; i < relatedPosts.length; i++) {
            const currentPost = relatedPosts[i];
            
            currentPost.classList.remove('hidden');
            const currentSidebarHeight = asideElement.scrollHeight;

            let cabeNaSidebar = true;

            if (currentSidebarHeight > maxPostHeight) {
                cabeNaSidebar = false;
            }

            if (currentSidebarHeight > viewportHeight) {
                const excesso = currentSidebarHeight - viewportHeight;
                if (excesso > 250) {
                    cabeNaSidebar = false;
                }
            }

            if (!cabeNaSidebar) {
                currentPost.classList.remove('hidden'); 

                currentPost.classList.remove('mb-6');
                currentPost.classList.add('w-full', 'md:flex-1', 'bg-brand-gray/30', 'p-4', 'rounded-md', 'border', 'border-gray-800/50', 'hover:border-gray-700', 'transition-colors');
                
                bottomContainer.appendChild(currentPost);
                movedToBottomCount++;
            } else {
                currentPost.classList.add('mb-6');
                currentPost.classList.remove('w-full', 'md:flex-1', 'bg-brand-gray/30', 'p-4', 'rounded-md', 'border', 'border-gray-800/50', 'hover:border-gray-700', 'transition-colors');
            }
        }

        if (movedToBottomCount > 0) {
            bottomSection.classList.remove('hidden');
        }
    }

    window.addEventListener('load', adjustSidebarContent);
    window.addEventListener('resize', adjustSidebarContent);
});
