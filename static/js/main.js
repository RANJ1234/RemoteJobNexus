// Remote Work Job Board Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize animations
    initAnimations();
    
    // Add event listeners
    setupEventListeners();
});

// Initialize animations for elements
function initAnimations() {
    // Animate elements that should fade in when they enter the viewport
    const animatedElements = document.querySelectorAll('.animated-element');
    
    if (animatedElements.length > 0) {
        // Create an intersection observer
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    // Unobserve after animation is triggered
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1 // Trigger when at least 10% of the element is visible
        });
        
        // Observe each animated element
        animatedElements.forEach(element => {
            observer.observe(element);
        });
    }
    
    // Initialize any other animations here
}

// Set up event listeners for interactive elements
function setupEventListeners() {
    // Search functionality
    const searchForm = document.querySelector('.search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', handleSearch);
    }
    
    // Category dropdown functionality
    const categorySelect = document.getElementById('job-category');
    if (categorySelect) {
        categorySelect.addEventListener('change', updateSubcategories);
    }
    
    // Smooth scrolling for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId !== '#') {
                e.preventDefault();
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    smoothScroll(targetElement);
                }
            }
        });
    });
}

// Handle search form submission
function handleSearch(event) {
    // Optional: Add search validation or processing here
    // For example, tracking search analytics
    console.log('Search submitted');
}

// Update subcategories based on selected category
function updateSubcategories() {
    const categorySelect = document.getElementById('job-category');
    const subcategoryInput = document.getElementById('job-subcategory');
    
    if (!categorySelect || !subcategoryInput) return;
    
    const category = categorySelect.value;
    
    // Clear current value
    subcategoryInput.value = '';
    
    // Provide placeholder based on selected category
    if (category === 'technology') {
        subcategoryInput.placeholder = 'E.g., Software Development, Data Science, DevOps';
    } else if (category === 'creative') {
        subcategoryInput.placeholder = 'E.g., Graphic Design, Content Writing, Video Production';
    } else if (category === 'professional') {
        subcategoryInput.placeholder = 'E.g., Accounting, Legal, Human Resources';
    } else if (category === 'healthcare') {
        subcategoryInput.placeholder = 'E.g., Telemedicine, Medical Writing, Health Coaching';
    } else if (category === 'education') {
        subcategoryInput.placeholder = 'E.g., Online Tutoring, Curriculum Development, ESL';
    } else if (category === 'skilled-trades') {
        subcategoryInput.placeholder = 'E.g., Technical Support, Virtual Assistance, Customer Service';
    } else {
        subcategoryInput.placeholder = 'Enter a specific subcategory';
    }
}

// Smooth scroll to element function
function smoothScroll(target, duration = 500) {
    const targetPosition = target.getBoundingClientRect().top + window.pageYOffset;
    const startPosition = window.pageYOffset;
    const distance = targetPosition - startPosition;
    let startTime = null;
    
    function animation(currentTime) {
        if (startTime === null) startTime = currentTime;
        const timeElapsed = currentTime - startTime;
        const scrollAmount = easeOutQuart(timeElapsed, startPosition, distance, duration);
        window.scrollTo(0, scrollAmount);
        if (timeElapsed < duration) requestAnimationFrame(animation);
    }
    
    // Easing function for smooth animation
    function easeOutQuart(t, b, c, d) {
        t /= d;
        t--;
        return -c * (t * t * t * t - 1) + b;
    }
    
    requestAnimationFrame(animation);
}

// Share job on social media
function shareJob(platform, jobTitle, jobUrl) {
    let shareUrl;
    
    switch(platform) {
        case 'twitter':
            shareUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(jobTitle)}&url=${encodeURIComponent(jobUrl)}`;
            break;
        case 'linkedin':
            shareUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(jobUrl)}`;
            break;
        case 'facebook':
            shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(jobUrl)}`;
            break;
        case 'email':
            shareUrl = `mailto:?subject=${encodeURIComponent(jobTitle)}&body=${encodeURIComponent('Check out this job: ' + jobUrl)}`;
            break;
    }
    
    if (shareUrl) {
        window.open(shareUrl, '_blank');
    }
}

// Toggle dark/light mode
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    
    // Save preference to localStorage
    if (document.body.classList.contains('dark-mode')) {
        localStorage.setItem('darkMode', 'enabled');
    } else {
        localStorage.setItem('darkMode', 'disabled');
    }
}

// Check user's dark mode preference from localStorage
function checkDarkModePreference() {
    if (localStorage.getItem('darkMode') === 'enabled') {
        document.body.classList.add('dark-mode');
    }
}

// Call this function on page load
checkDarkModePreference();