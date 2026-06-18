document.addEventListener("DOMContentLoaded", function() {
    const articleTitleH1 = document.querySelector('h1.text-3xl');
    const articleContent = document.querySelector('.article-content');
    const tocContainer = document.getElementById('table-of-contents');
    const tocList = document.getElementById('toc-list');
    
    if (!tocContainer || !tocList) return;

    const headings = articleContent ? articleContent.querySelectorAll('h2, h3') : [];

    if (articleTitleH1 || headings.length > 0) {
        tocContainer.classList.remove('hidden');
    }

    if (articleTitleH1) {
        if (!articleTitleH1.id) {
            articleTitleH1.id = 'article-main-title';
        }

        const liH1 = document.createElement('li');
        const linkH1 = document.createElement('a');
        
        linkH1.href = '#' + articleTitleH1.id;
        linkH1.textContent = articleTitleH1.textContent;
        linkH1.className = "hover:text-brand-yellow transition-colors duration-200 block py-1 text-brand-light font-bold text-base";
        
        liH1.appendChild(linkH1);
        tocList.appendChild(liH1);
    }

    headings.forEach((heading, index) => {
        if (!heading.id) {
            heading.id = 'heading-' + index;
        }

        const li = document.createElement('li');
        const link = document.createElement('a');
        
        link.href = '#' + heading.id;
        link.textContent = heading.textContent;
        link.className = "hover:text-brand-yellow transition-colors duration-200 block py-1";

        if (heading.tagName.toLowerCase() === 'h2') {
            li.className = "pl-3 border-l-2 border-gray-700/30 ml-1";
            link.classList.add("text-brand-light", "font-semibold");
        } else if (heading.tagName.toLowerCase() === 'h3') {
            li.className = "pl-6 border-l-2 border-gray-700/50 ml-1";
            link.classList.add("text-gray-400", "text-xs");
        }
        
        li.appendChild(link);
        tocList.appendChild(li);
    });
});
