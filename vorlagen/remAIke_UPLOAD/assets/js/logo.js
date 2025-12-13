// Hyperactive Logo Animation
document.addEventListener('DOMContentLoaded', function() {
    const logo = document.getElementById('hyperactive-logo');
    if (!logo) return;

    let animationInterval;
    let isAnimating = false;

    function startAnimation() {
        if (isAnimating) return;
        isAnimating = true;

        let colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#ffeaa7', '#dda0dd'];
        let currentColor = 0;

        animationInterval = setInterval(() => {
            logo.style.color = colors[currentColor];
            logo.style.transform = `scale(${1 + Math.random() * 0.2}) rotate(${Math.random() * 10 - 5}deg)`;
            currentColor = (currentColor + 1) % colors.length;
        }, 200);
    }

    function stopAnimation() {
        if (!isAnimating) return;
        isAnimating = false;
        clearInterval(animationInterval);
        logo.style.color = '#007bff';
        logo.style.transform = 'scale(1) rotate(0deg)';
    }

    // Start animation on hover
    logo.addEventListener('mouseenter', startAnimation);
    logo.addEventListener('mouseleave', stopAnimation);

    // Start brief animation on load
    setTimeout(() => {
        startAnimation();
        setTimeout(stopAnimation, 2000);
    }, 1000);
});
