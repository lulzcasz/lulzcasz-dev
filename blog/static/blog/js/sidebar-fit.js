document.addEventListener("DOMContentLoaded", function() {
    const articleContent = document.querySelector('.article-content');
    const asideElement = document.querySelector('aside');
    const relatedArticles = document.querySelectorAll('.related-article-item');
    const bottomContainer = document.getElementById('bottom-related-container');
    const bottomSection = document.getElementById('bottom-related-section');
    
    if (!articleContent || !asideElement || relatedArticles.length === 0 || !bottomContainer) return;

    function adjustSidebarContent() {
        const viewportHeight = window.innerHeight;
        const maxArticleHeight = articleContent.offsetHeight;

        const sidebarContainer = document.getElementById('related-articles-container');
        relatedArticles.forEach(article => {
            article.classList.add('hidden');
            sidebarContainer.appendChild(article);
        });

        bottomContainer.innerHTML = '';
        bottomSection.classList.add('hidden');

        let movedToBottomCount = 0;

        for (let i = 0; i < relatedArticles.length; i++) {
            const currentArticle = relatedArticles[i];
            
            currentArticle.classList.remove('hidden');
            const currentSidebarHeight = asideElement.scrollHeight;

            let cabeNaSidebar = true;

            if (currentSidebarHeight > maxArticleHeight) {
                cabeNaSidebar = false;
            }

            if (currentSidebarHeight > viewportHeight) {
                const excesso = currentSidebarHeight - viewportHeight;
                if (excesso > 250) {
                    cabeNaSidebar = false;
                }
            }

            if (!cabeNaSidebar) {
                currentArticle.classList.remove('hidden'); 

                currentArticle.classList.remove('mb-6');
                currentArticle.classList.add('w-full', 'md:flex-1', 'bg-brand-gray/30', 'p-4', 'rounded-md', 'border', 'border-gray-800/50', 'hover:border-gray-700', 'transition-colors');
                
                bottomContainer.appendChild(currentArticle);
                movedToBottomCount++;
            } else {
                currentArticle.classList.add('mb-6');
                currentArticle.classList.remove('w-full', 'md:flex-1', 'bg-brand-gray/30', 'p-4', 'rounded-md', 'border', 'border-gray-800/50', 'hover:border-gray-700', 'transition-colors');
            }
        }

        if (movedToBottomCount > 0) {
            bottomSection.classList.remove('hidden');
        }
    }

    window.addEventListener('load', adjustSidebarContent);
    window.addEventListener('resize', adjustSidebarContent);
});
