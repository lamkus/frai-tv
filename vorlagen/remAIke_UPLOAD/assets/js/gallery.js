document.addEventListener('DOMContentLoaded', () => {
    const gallery = document.getElementById('comparison-gallery');
    if (!gallery) {
        console.error('Gallery container #comparison-gallery not found.');
        return;
    }

    fetch('assets/screenshots/frame_comparisons.json')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(comparisons => {
            // Clear existing content
            gallery.innerHTML = '';

            // Take first 6 comparisons
            const galleryItems = comparisons.slice(0, 6);

            galleryItems.forEach((item, index) => {
                const originalPath = item.original;
                const enhancedPath = item.enhanced;

                const col = document.createElement('div');
                col.className = 'col-md-4 mb-4';

                col.innerHTML = `
                    <div class="card h-100">
                        <div class="card-body">
                            <h6 class="card-title">${item.title || 'Vergleich ' + (index + 1)}</h6>
                            <div class="comparison-container">
                                <div class="before-after-container">
                                    <img src="${originalPath}" alt="Original" class="img-fluid mb-2" style="max-height: 200px;">
                                    <img src="${enhancedPath}" alt="8K Enhanced" class="img-fluid" style="max-height: 200px;">
                                </div>
                                <div class="text-center mt-2">
                                    <small class="text-muted">Original ↔ 8K Enhanced</small>
                                </div>
                            </div>
                        </div>
                    </div>
                `;

                gallery.appendChild(col);
            });
        })
        .catch(error => {
            console.error('Could not load comparison data:', error);
            gallery.innerHTML = '<div class="col-12"><p class="text-center text-muted">Vergleichsbilder konnten nicht geladen werden.</p></div>';
        });
});
