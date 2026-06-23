import Alpine from 'alpinejs'
import mediumZoom from 'medium-zoom'

document.addEventListener('DOMContentLoaded', () => {
    mediumZoom('[data-zoomable]', {
        background: '#101010',
        margin: 24
    })
})

document.addEventListener('alpine:init', () => {
    Alpine.data('sidebarManager', () => ({
        movedToBottomCount: 0,
        
        init() {
            const runAdjust = () => {
                this.$nextTick(() => this.adjust());
            };

            if (document.readyState === 'complete') {
                runAdjust();
            } else {
                window.addEventListener('load', runAdjust);
            }
        },

        adjust() {
            const articleContent = document.querySelector('.article-content');
            const asideElement = document.querySelector('aside');
            const relatedArticles = document.querySelectorAll('.related-article-item');
            const bottomContainer = document.getElementById('bottom-related-container');
            const sidebarContainer = document.getElementById('related-articles-container');
            
            if (!articleContent || !asideElement) return;

            relatedArticles.forEach(article => {
                sidebarContainer.appendChild(article);
                article.classList.add('hidden');
                article.classList.remove('block', 'w-full', 'md:flex-1', 'bg-brand-gray/30', 'p-4', 'rounded-md', 'border', 'border-gray-800/50', 'hover:border-gray-700', 'transition-colors');
                article.classList.add('mb-6');
            });
            
            this.movedToBottomCount = 0; 
            void asideElement.offsetHeight;

            const maxAllowedHeight = Math.min(
                articleContent.offsetHeight,
                window.innerHeight - 40 
            );

            relatedArticles.forEach(article => {
                article.classList.remove('hidden');
                article.classList.add('block'); 
                
                const currentSidebarHeight = asideElement.scrollHeight;

                if (currentSidebarHeight > maxAllowedHeight) {
                    article.classList.remove('mb-6', 'block');
                    article.classList.add('w-full', 'md:flex-1', 'bg-brand-gray/30', 'p-4', 'rounded-md', 'border', 'border-gray-800/50', 'hover:border-gray-700', 'transition-colors');
                    
                    bottomContainer.appendChild(article);
                    this.movedToBottomCount++;
                }
            });
        }
    }))
})

window.Alpine = Alpine
Alpine.start()
