document.addEventListener('DOMContentLoaded', () => {
    // Mobile menu toggle
    const menuToggle = document.querySelector('[data-menu-toggle]');
    const mobileMenu = document.querySelector('[data-mobile-menu]');
    if (menuToggle && mobileMenu) {
        menuToggle.addEventListener('click', () => {
            mobileMenu.classList.toggle('hidden');
        });
    }

    // Flash messages auto-dismiss
    document.querySelectorAll('[data-flash]').forEach((flash) => {
        setTimeout(() => {
            flash.classList.add('opacity-0', 'translate-y-2');
            setTimeout(() => flash.remove(), 180);
        }, 4800);
    });

    // Search suggestions (mocked client-side)
    const searchInputs = document.querySelectorAll('[data-search-input]');
    const demoSuggestions = ['MacBook Pro 2020', 'Python 教科書', '電子計算機', '生活用品組合', '運動球類'];
    searchInputs.forEach((searchInput) => {
        const suggestionPanel = searchInput.parentElement.querySelector('[data-search-suggestions]');
        if (!suggestionPanel) return;

        let debounceTimer;
        searchInput.addEventListener('input', (e) => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                const term = e.target.value.trim();
                suggestionPanel.innerHTML = '';
                if (term.length < 2) {
                    suggestionPanel.classList.add('hidden');
                    return;
                }
                demoSuggestions
                    .filter((item) => item.toLowerCase().includes(term.toLowerCase()))
                    .forEach((item) => {
                        const row = document.createElement('button');
                        row.type = 'button';
                        row.className = 'w-full text-left px-4 py-2 hover:bg-primaryLight text-secondaryDark';
                        row.textContent = item;
                        row.addEventListener('click', () => {
                            searchInput.value = item;
                            suggestionPanel.classList.add('hidden');
                        });
                        suggestionPanel.appendChild(row);
                    });
                suggestionPanel.classList.toggle('hidden', suggestionPanel.childElementCount === 0);
            }, 260);
        });

        document.addEventListener('click', (e) => {
            if (!suggestionPanel.contains(e.target) && e.target !== searchInput) {
                suggestionPanel.classList.add('hidden');
            }
        });
    });

    // Image upload preview (used in product form)
    const imageInput = document.querySelector('[data-image-input]');
    const previewWrap = document.querySelector('[data-image-preview]');
    if (imageInput && previewWrap) {
        imageInput.addEventListener('change', (e) => {
            previewWrap.innerHTML = '';
            Array.from(e.target.files || []).slice(0, 5).forEach((file, idx) => {
                const reader = new FileReader();
                reader.onload = (event) => {
                    const tile = document.createElement('div');
                    tile.className = 'border border-secondaryLight rounded-xl overflow-hidden shadow-sm';
                    tile.innerHTML = `
                        <div class="h-28 w-28 bg-secondaryLight">
                            <img src="${event.target.result}" alt="預覽 ${idx + 1}" class="w-full h-full object-cover">
                        </div>
                        <div class="px-3 py-2 text-sm text-secondary flex justify-between">
                            <span class="flex items-center gap-1">⭐<span>設為主圖</span></span>
                            <span class="text-danger cursor-pointer">✕</span>
                        </div>
                    `;
                    previewWrap.appendChild(tile);
                };
                reader.readAsDataURL(file);
            });
        });
    }

    // Star rating selection
    const ratingStars = document.querySelectorAll('[data-rating-star]');
    if (ratingStars.length) {
        ratingStars.forEach((star) => {
            star.addEventListener('click', () => setRating(parseInt(star.dataset.ratingStar, 10)));
            star.addEventListener('mouseenter', () => paintStars(parseInt(star.dataset.ratingStar, 10)));
            star.addEventListener('mouseleave', () => paintStars(getCurrentRating()));
        });
        paintStars(getCurrentRating());
    }

    function setRating(value) {
        const input = document.querySelector('[name="rating"]');
        if (input) input.value = value;
        paintStars(value);
    }

    function paintStars(value) {
        ratingStars.forEach((star) => {
            const active = parseInt(star.dataset.ratingStar, 10) <= value;
            star.classList.toggle('text-yellow-400', active);
            star.classList.toggle('text-secondary', !active);
        });
        const label = document.querySelector('[data-rating-label]');
        if (label) {
            const textMap = ['很不滿意', '不滿意', '普通', '很好', '非常好'];
            label.textContent = value ? textMap[value - 1] : '點擊星星評分';
        }
    }

    function getCurrentRating() {
        const input = document.querySelector('[name="rating"]');
        return input ? parseInt(input.value || '0', 10) : 0;
    }
});
