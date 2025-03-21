// Main JavaScript functionality for the website

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Navbar scroll effect
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.classList.add('navbar-scrolled');
            } else {
                navbar.classList.remove('navbar-scrolled');
            }
        });
    }
    
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // Add animation classes to elements
    const animatedElements = document.querySelectorAll('.job-card, .step-card');
    animatedElements.forEach((element, index) => {
        element.classList.add('fade-in');
        element.style.animationDelay = `${index * 0.1}s`;
    });
});

// Search functionality
function handleSearch(event) {
    const form = event.target.closest('form');
    const searchInput = form.querySelector('input[type="text"]');
    
    if (searchInput.value.trim() === '') {
        event.preventDefault();
        searchInput.focus();
        
        // Add shake animation to indicate error
        searchInput.classList.add('error-shake');
        setTimeout(() => {
            searchInput.classList.remove('error-shake');
        }, 500);
        
        return false;
    }
    
    return true;
}

// Initialize search forms
const searchForms = document.querySelectorAll('.search-form');
searchForms.forEach(form => {
    form.addEventListener('submit', handleSearch);
});

// Share functionality
function shareJob(platform, jobTitle, jobUrl) {
    let shareUrl;
    
    switch (platform) {
        case 'twitter':
            shareUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(`Check out this remote job: ${jobTitle}`)}&url=${encodeURIComponent(jobUrl)}`;
            break;
        case 'linkedin':
            shareUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(jobUrl)}`;
            break;
        case 'email':
            shareUrl = `mailto:?subject=${encodeURIComponent(`Remote Job: ${jobTitle}`)}&body=${encodeURIComponent(`I found this remote job that might interest you: ${jobUrl}`)}`;
            break;
        default:
            return;
    }
    
    window.open(shareUrl, '_blank');
}

// Add parallax effect to background elements
function addParallaxEffect() {
    document.addEventListener('mousemove', (e) => {
        const mouseX = e.clientX / window.innerWidth;
        const mouseY = e.clientY / window.innerHeight;
        
        const parallaxElements = document.querySelectorAll('.parallax');
        parallaxElements.forEach(element => {
            const speed = element.getAttribute('data-speed') || 0.05;
            const x = (0.5 - mouseX) * speed * 100;
            const y = (0.5 - mouseY) * speed * 100;
            
            element.style.transform = `translate(${x}px, ${y}px)`;
        });
    });
}

// Add parallax effect if there are elements with the .parallax class
if (document.querySelector('.parallax')) {
    addParallaxEffect();
}

// Handle mobile navigation
const navbarToggler = document.querySelector('.navbar-toggler');
if (navbarToggler) {
    navbarToggler.addEventListener('click', function() {
        this.classList.toggle('active');
    });
}

// Prevent form submission on Enter key for URL extraction field
const jobUrlInput = document.getElementById('job-url');
if (jobUrlInput) {
    jobUrlInput.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            document.getElementById('extract-btn').click();
        }
    });
}

// Initialize any CSS animations for page elements
function initAnimations() {
    // Add .visible class to elements with .animated class when they come into view
    const animatedElements = document.querySelectorAll('.animated:not(.visible)');
    
    if (animatedElements.length > 0) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1
        });
        
        animatedElements.forEach(element => {
            observer.observe(element);
        });
    }
}

// Call animation initialization
initAnimations();
