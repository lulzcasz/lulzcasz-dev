import Alpine from 'alpinejs'

import 'prismjs';
import 'prismjs/plugins/autoloader/prism-autoloader.min.js';
import 'prismjs/plugins/toolbar/prism-toolbar.min.js';
import 'prismjs/plugins/treeview/prism-treeview.min.js';
import 'prismjs/plugins/copy-to-clipboard/prism-copy-to-clipboard.min.js';

import 'prismjs/plugins/toolbar/prism-toolbar.min.css';
import 'prismjs/plugins/treeview/prism-treeview.min.css';
import 'prism-themes/themes/prism-coldark-dark.min.css';
import '@fortawesome/fontawesome-free/css/all.min.css';

Prism.plugins.autoloader.languages_path = 'https://cdnjs.cloudflare.com/ajax/libs/prism/1.30.0/components/';

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
    }));

    Alpine.data('lightbox', () => ({
        isOpen: false,
        imgSrc: '',
        
        openImage(event) {
            this.imgSrc = event.detail;
            this.isOpen = true;
        },
        
        close() {
            this.isOpen = false;
        },
        
        closeOnScroll() {
            if (this.isOpen) {
                this.close();
            }
        }
    }));
});

window.Alpine = Alpine
Alpine.start()
