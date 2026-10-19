document.addEventListener('DOMContentLoaded', function() {
    const menuToggle = document.querySelector('.menu-toggle');
    const mobileNav = document.querySelector('.mobile-nav');

    function setMenuOpen(open) {
        menuToggle.classList.toggle('active', open);
        mobileNav.classList.toggle('active', open);
        menuToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    }

    menuToggle.addEventListener('click', function() {
        setMenuOpen(!mobileNav.classList.contains('active'));
    });

    // Close menu when clicking outside or pressing Escape
    document.addEventListener('click', function(event) {
        if (!event.target.closest('nav')) {
            setMenuOpen(false);
        }
    });
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            setMenuOpen(false);
        }
    });

    // Looping clips (_includes/video.html): download and play only near the screen.
    // People whose system asks for reduced motion get the normal play controls instead.
    const loopVideos = document.querySelectorAll('video[data-autoplay]');
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    function play(video) {
        const attempt = video.play();
        if (attempt) attempt.catch(function() { video.controls = true; });
    }
    if (reduceMotion) {
        loopVideos.forEach(function(video) {
            video.controls = true;
            video.preload = 'metadata';
        });
    } else if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    play(entry.target);
                } else {
                    entry.target.pause();
                }
            });
        }, { rootMargin: '200px 0px' });
        loopVideos.forEach(function(video) { observer.observe(video); });
    } else {
        loopVideos.forEach(play);
    }

    // Project write-ups: click an image to see it full size; click again or press Escape to close.
    const writeUp = document.querySelector('.post-view .content');
    if (writeUp && typeof HTMLDialogElement === 'function') {
        const lightbox = document.createElement('dialog');
        lightbox.className = 'lightbox';
        lightbox.innerHTML = '<button type="button" class="lightbox-close" aria-label="Close">&times;</button><img alt="">';
        document.body.appendChild(lightbox);
        const fullImage = lightbox.querySelector('img');
        writeUp.addEventListener('click', function(event) {
            const img = event.target.closest('.image-gallery img');
            if (!img) return;
            fullImage.src = img.currentSrc || img.src;
            fullImage.alt = img.alt;
            lightbox.showModal();
        });
        lightbox.addEventListener('click', function() { lightbox.close(); });
    }

    // YouTube (_includes/youtube-video.html): swap the thumbnail for the player on click.
    document.querySelectorAll('.youtube-facade').forEach(function(link) {
        link.addEventListener('click', function(event) {
            event.preventDefault();
            const iframe = document.createElement('iframe');
            iframe.src = 'https://www.youtube-nocookie.com/embed/' + link.dataset.youtubeId + '?autoplay=1';
            iframe.title = link.dataset.title;
            iframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';
            iframe.allowFullscreen = true;
            link.replaceWith(iframe);
            iframe.focus();
        });
    });
});
