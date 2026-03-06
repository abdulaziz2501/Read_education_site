// Add border or shadow to navbar on scroll
document.addEventListener('DOMContentLoaded', () => {
    const navbar = document.getElementById('navbar');

    if (navbar) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 20) {
                navbar.classList.add('shadow-md');
                navbar.classList.replace('bg-white/80', 'bg-white/95');
                navbar.classList.replace('py-0', 'py-1');
            } else {
                navbar.classList.remove('shadow-md');
                navbar.classList.replace('bg-white/95', 'bg-white/80');
                navbar.classList.replace('py-1', 'py-0');
            }
        });
    }
});
