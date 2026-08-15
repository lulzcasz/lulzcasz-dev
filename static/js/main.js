import Alpine from 'alpinejs'
import hljs from 'highlight.js/lib/core';

import arduino from 'highlight.js/lib/languages/arduino';
import armasm from 'highlight.js/lib/languages/armasm';
import avrasm from 'highlight.js/lib/languages/avrasm';
import bash from 'highlight.js/lib/languages/bash';
import c from 'highlight.js/lib/languages/c';
import cmake from 'highlight.js/lib/languages/cmake';
import cpp from 'highlight.js/lib/languages/cpp';
import css from 'highlight.js/lib/languages/css';
import django from 'highlight.js/lib/languages/django';
import dockerfile from 'highlight.js/lib/languages/dockerfile';
import javascript from 'highlight.js/lib/languages/javascript';
import json from 'highlight.js/lib/languages/json';
import makefile from 'highlight.js/lib/languages/makefile';
import x86asm from 'highlight.js/lib/languages/x86asm';
import powershell from 'highlight.js/lib/languages/powershell';
import python from 'highlight.js/lib/languages/python';
import sql from 'highlight.js/lib/languages/sql';
import ini from 'highlight.js/lib/languages/ini';
import yaml from 'highlight.js/lib/languages/yaml';
import shell from 'highlight.js/lib/languages/shell';
import plaintext from 'highlight.js/lib/languages/plaintext';

hljs.registerLanguage('arduino', arduino);
hljs.registerLanguage('armasm', armasm);
hljs.registerLanguage('avrasm', avrasm);
hljs.registerLanguage('bash', bash);
hljs.registerLanguage('c', c);
hljs.registerLanguage('cmake', cmake);
hljs.registerLanguage('cpp', cpp);
hljs.registerLanguage('css', css);
hljs.registerLanguage('django', django);
hljs.registerLanguage('docker', dockerfile);
hljs.registerLanguage('javascript', javascript);
hljs.registerLanguage('json', json);
hljs.registerLanguage('makefile', makefile);
hljs.registerLanguage('nasm', x86asm);
hljs.registerLanguage('powershell', powershell);
hljs.registerLanguage('python', python);
hljs.registerLanguage('sql', sql);
hljs.registerLanguage('toml', ini);
hljs.registerLanguage('yaml', yaml);
hljs.registerLanguage('shell', shell);
hljs.registerLanguage('plaintext', plaintext);

document.querySelectorAll('pre').forEach((block) => {
    const code = block.querySelector('code');
    if (!code) return;

    hljs.highlightElement(code);

    block.style.position = 'relative';

    const button = document.createElement('button');
    button.type = 'button';
    button.innerHTML = '<i class="fa-solid fa-copy"></i>';
    button.className = 'absolute top-3 right-3 bg-brand-gray text-brand-light px-2.5 py-1.5 rounded text-xs border border-gray-700 hover:bg-gray-800 transition-colors cursor-pointer';

    button.addEventListener('click', () => {
        navigator.clipboard.writeText(code.innerText).then(() => {
            button.innerHTML = '<i class="fa-solid fa-check text-brand-yellow"></i>';
            setTimeout(() => {
                button.innerHTML = '<i class="fa-solid fa-copy"></i>';
            }, 2000);
        });
    });

    block.appendChild(button);
});

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
