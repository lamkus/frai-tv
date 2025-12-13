document.addEventListener('DOMContentLoaded', function() {
    const logoContainer = document.querySelector('.logo-hyperactive');
    if (!logoContainer) return;

    const logoSharp = logoContainer.querySelector('.logo-sharp');
    const logoBlurred = logoContainer.querySelector('.logo-blurred');

    let animationFrame;
    let startTime = Date.now();

    function animate() {
        const now = Date.now();
        const elapsed = now - startTime;
        const cycleDuration = 4000; // 4 seconds for smoother transition

        // Create a smooth sine wave for blur intensity
        const progress = (elapsed % cycleDuration) / cycleDuration;
        const blurIntensity = Math.sin(progress * Math.PI * 2) * 2 + 3; // Range from 1 to 5px blur

        // Apply blur to the sharp logo (which is always visible)
        logoSharp.style.filter = `blur(${Math.max(0, blurIntensity)}px)`;
        logoBlurred.style.opacity = '0'; // Hide the blurred version

        animationFrame = requestAnimationFrame(animate);
    }

    // Start with sharp logo visible
    logoSharp.style.opacity = '1';
    logoBlurred.style.opacity = '0';

    // Start animation
    animate();
});
