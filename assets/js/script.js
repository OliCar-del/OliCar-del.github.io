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
});
