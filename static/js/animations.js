// Animation utilities for the website

// Smooth scroll animation
function smoothScroll(target, duration = 500) {
    const targetElement = document.querySelector(target);
    if (!targetElement) return;
    
    const targetPosition = targetElement.getBoundingClientRect().top + window.pageYOffset;
    const startPosition = window.pageYOffset;
    const distance = targetPosition - startPosition;
    let startTime = null;
    
    function animation(currentTime) {
        if (startTime === null) startTime = currentTime;
        const timeElapsed = currentTime - startTime;
        const progress = Math.min(timeElapsed / duration, 1);
        const ease = easeOutQuart(progress);
        
        window.scrollTo(0, startPosition + distance * ease);
        
        if (timeElapsed < duration) {
            requestAnimationFrame(animation);
        }
    }
    
    // Easing function for smooth deceleration
    function easeOutQuart(t) {
        return 1 - Math.pow(1 - t, 4);
    }
    
    requestAnimationFrame(animation);
}

// Add smooth scroll to all links with data-scroll attribute
function initSmoothScroll() {
    const scrollLinks = document.querySelectorAll('[data-scroll]');
    
    scrollLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const target = link.getAttribute('href');
            smoothScroll(target);
        });
    });
}

// Fade-in animation for elements
function fadeInElements() {
    const fadeElements = document.querySelectorAll('.fade-in');
    
    // Create intersection observer
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
    
    // Observe each element
    fadeElements.forEach(element => {
        observer.observe(element);
    });
}

// Floating animation for elements
function floatingAnimation(element, amplitude = 10, period = 3000) {
    if (!element) return;
    
    const startY = element.offsetTop;
    let startTime = Date.now();
    
    function animate() {
        const elapsed = Date.now() - startTime;
        const offset = amplitude * Math.sin((elapsed / period) * (2 * Math.PI));
        
        element.style.transform = `translateY(${offset}px)`;
        requestAnimationFrame(animate);
    }
    
    animate();
}

// Animate numbers counting up
function animateNumbers() {
    const numberElements = document.querySelectorAll('.animate-number');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const element = entry.target;
                const final = parseInt(element.getAttribute('data-final'), 10);
                const duration = parseInt(element.getAttribute('data-duration') || 2000, 10);
                
                animateValue(element, 0, final, duration);
                observer.unobserve(element);
            }
        });
    }, {
        threshold: 0.5
    });
    
    numberElements.forEach(element => {
        observer.observe(element);
    });
}

// Helper function for number animation
function animateValue(element, start, end, duration) {
    let startTime = null;
    
    function animation(currentTime) {
        if (startTime === null) startTime = currentTime;
        const timeElapsed = currentTime - startTime;
        const progress = Math.min(timeElapsed / duration, 1);
        const value = Math.floor(progress * (end - start) + start);
        
        element.textContent = value;
        
        if (timeElapsed < duration) {
            requestAnimationFrame(animation);
        } else {
            element.textContent = end;
        }
    }
    
    requestAnimationFrame(animation);
}

// Particle effect for buttons
function addParticleEffect(button) {
    if (!button) return;
    
    button.addEventListener('click', (event) => {
        const x = event.clientX - button.getBoundingClientRect().left;
        const y = event.clientY - button.getBoundingClientRect().top;
        
        // Create particles
        for (let i = 0; i < 15; i++) {
            createParticle(x, y, button);
        }
    });
}

// Helper function to create a single particle
function createParticle(x, y, button) {
    const particle = document.createElement('span');
    particle.classList.add('particle');
    
    // Random size
    const size = Math.floor(Math.random() * 10 + 5);
    particle.style.width = `${size}px`;
    particle.style.height = `${size}px`;
    
    // Random position
    const destinationX = x + (Math.random() - 0.5) * 100;
    const destinationY = y + (Math.random() - 0.5) * 100;
    
    // Set initial position
    particle.style.left = `${x}px`;
    particle.style.top = `${y}px`;
    
    // Animation properties
    particle.style.opacity = '1';
    particle.style.transform = 'translate(-50%, -50%)';
    
    // Add to button
    button.appendChild(particle);
    
    // Animate
    particle.animate([
        {
            transform: 'translate(-50%, -50%)',
            opacity: 1
        },
        {
            transform: `translate(${destinationX - x}px, ${destinationY - y}px)`,
            opacity: 0
        }
    ], {
        duration: 1000,
        easing: 'cubic-bezier(0, 0.5, 0.5, 1)'
    }).onfinish = () => {
        particle.remove();
    };
}

// Initialize animations when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    initSmoothScroll();
    fadeInElements();
    animateNumbers();
    
    // Add particle effects to primary buttons
    const primaryButtons = document.querySelectorAll('.btn-primary');
    primaryButtons.forEach(button => {
        addParticleEffect(button);
    });
});
