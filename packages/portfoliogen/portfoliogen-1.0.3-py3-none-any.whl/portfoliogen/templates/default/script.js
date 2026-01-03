// Portfolio Website JavaScript
// Modern, responsive portfolio with right sidebar navigation

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all functionality
    initPreloader();
    initSidebar();
    initScrollEffects();
    initPortfolioFilter();
    initPortfolioModal();
    initContactForm();
    initSmoothScrolling();
    initAnimations();
    initThemeToggle();
});

// Preloader functionality
function initPreloader() {
    const preloader = document.getElementById('preloader');
    
    // Hide preloader after DOM is loaded
    setTimeout(() => {
        preloader.classList.add('hidden');
        setTimeout(() => {
            preloader.style.display = 'none';
        }, 500);
    }, 1500);
    
    // Fallback: hide preloader after 3 seconds regardless
    setTimeout(() => {
        if (!preloader.classList.contains('hidden')) {
            preloader.classList.add('hidden');
            setTimeout(() => {
                preloader.style.display = 'none';
            }, 500);
        }
    }, 3000);
}

// Sidebar functionality
function initSidebar() {
    const sidebar = document.getElementById('sidebar');
    const mobileToggle = document.getElementById('mobile-menu-toggle');
    const backdrop = document.getElementById('sidebar-backdrop');
    const navLinks = document.querySelectorAll('.nav-link');
    
    // Mobile menu toggle
    mobileToggle.addEventListener('click', function() {
        sidebar.classList.toggle('active');
        backdrop.classList.toggle('active');
        mobileToggle.classList.toggle('active');
        document.body.classList.toggle('sidebar-open');
    });
    
    // Close sidebar when clicking backdrop
    backdrop.addEventListener('click', function() {
        sidebar.classList.remove('active');
        backdrop.classList.remove('active');
        mobileToggle.classList.remove('active');
        document.body.classList.remove('sidebar-open');
    });
    
    // Close sidebar when clicking on nav links (mobile)
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            if (window.innerWidth <= 768) {
                sidebar.classList.remove('active');
                backdrop.classList.remove('active');
                mobileToggle.classList.remove('active');
                document.body.classList.remove('sidebar-open');
            }
        });
    });
    
    // Close sidebar when clicking outside (mobile)
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 768) {
            if (!sidebar.contains(e.target) && !mobileToggle.contains(e.target)) {
                sidebar.classList.remove('active');
                backdrop.classList.remove('active');
                mobileToggle.classList.remove('active');
                document.body.classList.remove('sidebar-open');
            }
        }
    });
    
    // Handle window resize
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            sidebar.classList.remove('active');
            backdrop.classList.remove('active');
            mobileToggle.classList.remove('active');
            document.body.classList.remove('sidebar-open');
        }
    });
}

// Scroll effects and active section highlighting
function initScrollEffects() {
    const sections = document.querySelectorAll('.section');
    const navLinks = document.querySelectorAll('.nav-link');
    
    // Function to update active navigation link
    function updateActiveNavLink() {
        let current = '';
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            
            if (window.scrollY >= (sectionTop - 200)) {
                current = section.getAttribute('id');
            }
        });
        
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('data-section') === current) {
                link.classList.add('active');
            }
        });
    }
    
    // Throttled scroll event listener
    let ticking = false;
    function handleScroll() {
        if (!ticking) {
            requestAnimationFrame(() => {
                updateActiveNavLink();
                ticking = false;
            });
            ticking = true;
        }
    }
    
    window.addEventListener('scroll', handleScroll);
    
    // Initial call
    updateActiveNavLink();
}

// Portfolio filtering functionality
function initPortfolioFilter() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    const portfolioItems = document.querySelectorAll('.portfolio-item');
    
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            const filter = this.getAttribute('data-filter');
            
            // Update active button
            filterButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // Filter portfolio items
            portfolioItems.forEach(item => {
                const category = item.getAttribute('data-category');
                
                if (filter === 'all' || category === filter) {
                    item.style.display = 'block';
                    // Add animation delay for staggered effect
                    setTimeout(() => {
                        item.style.opacity = '1';
                        item.style.transform = 'scale(1)';
                    }, 100);
                } else {
                    item.style.opacity = '0';
                    item.style.transform = 'scale(0.8)';
                    setTimeout(() => {
                        item.style.display = 'none';
                    }, 300);
                }
            });
        });
    });
    
    // Add hover effects to portfolio items
    portfolioItems.forEach(item => {
        item.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px) scale(1.02)';
        });
        
        item.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
}

// Portfolio Modal functionality
function initPortfolioModal() {
    const portfolioItems = document.querySelectorAll('.portfolio-item');
    const modal = document.getElementById('portfolio-modal');
    const modalBackdrop = document.querySelector('.portfolio-modal-backdrop');
    const modalClose = document.querySelector('.portfolio-modal-close');
    
    // Modal elements
    const modalImage = document.getElementById('modal-image');
    const modalTitle = document.getElementById('modal-title');
    const modalDescription = document.getElementById('modal-description');
    const modalTech = document.getElementById('modal-tech');
    const modalFeatures = document.getElementById('modal-features');
    const modalLink = document.getElementById('modal-link');
    
    // Add click listeners to portfolio items for modal
    portfolioItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            openPortfolioModal(this);
        });
        
        // Add cursor pointer to indicate clickability
        item.style.cursor = 'pointer';
    });
    
    // Close modal listeners
    modalClose.addEventListener('click', closePortfolioModal);
    modalBackdrop.addEventListener('click', closePortfolioModal);
    
    // Close modal on Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && modal.classList.contains('active')) {
            closePortfolioModal();
        }
    });
    
    function openPortfolioModal(item) {
        // Get data from portfolio item
        const title = item.getAttribute('data-title');
        const description = item.getAttribute('data-description');
        const image = item.getAttribute('data-image');
        const link = item.getAttribute('data-link');
        const tech = item.getAttribute('data-tech').split(',');
        const features = item.getAttribute('data-features').split(',');
        
        // Populate modal content
        modalTitle.textContent = title;
        modalDescription.textContent = description;
        modalImage.src = image;
        modalImage.alt = title;
        modalLink.href = link;
        
        // Clear and populate tech tags
        modalTech.innerHTML = '';
        tech.forEach(techItem => {
            const tag = document.createElement('span');
            tag.className = 'tech-tag';
            tag.textContent = techItem.trim();
            modalTech.appendChild(tag);
        });
        
        // Clear and populate features
        modalFeatures.innerHTML = '';
        features.forEach(feature => {
            const li = document.createElement('li');
            li.textContent = feature.trim();
            modalFeatures.appendChild(li);
        });
        
        // Show modal
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
}

// Global function to close modal (called from HTML)
function closePortfolioModal() {
    const modal = document.getElementById('portfolio-modal');
    modal.classList.remove('active');
    document.body.style.overflow = '';
}

// Contact form validation and submission
function initContactForm() {
    const contactForm = document.getElementById('contact-form');
    const formInputs = contactForm.querySelectorAll('input, textarea');
    
    // Real-time validation
    formInputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (this.value.trim() !== '') {
                validateField(this);
            }
        });
        
        input.addEventListener('input', function() {
            clearFieldError(this);
        });
    });
    
    // Form submission
    contactForm.addEventListener('submit', function(e) {
        let isValid = true;
        
        // Validate all fields
        formInputs.forEach(input => {
            if (!validateField(input)) {
                isValid = false;
            }
        });
        
        if (!isValid) {
            e.preventDefault();
            showFormError('Please correct the errors above.');
        } else {
            // Let Web3Forms handle the submission
            showFormSuccess('Sending message...');
        }
    });
    
    // Field validation function
    function validateField(field) {
        const value = field.value.trim();
        const fieldName = field.name;
        let isValid = true;
        let errorMessage = '';
        
        // Required field validation
        if (!value) {
            isValid = false;
            errorMessage = `${fieldName.charAt(0).toUpperCase() + fieldName.slice(1)} is required.`;
        }
        
        // Email validation
        if (fieldName === 'email' && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                isValid = false;
                errorMessage = 'Please enter a valid email address.';
            }
        }
        
        // Name validation
        if (fieldName === 'name' && value) {
            if (value.length < 2) {
                isValid = false;
                errorMessage = 'Name must be at least 2 characters long.';
            }
        }
        
        // Message validation
        if (fieldName === 'message' && value) {
            if (value.length < 10) {
                isValid = false;
                errorMessage = 'Message must be at least 10 characters long.';
            }
        }
        
        // Show/hide error
        if (!isValid) {
            showFieldError(field, errorMessage);
        } else {
            clearFieldError(field);
        }
        
        return isValid;
    }
    
    // Clear all errors on page load
    function clearAllErrors() {
        formInputs.forEach(input => {
            clearFieldError(input);
        });
    }
    
    // Clear all errors when page loads
    clearAllErrors();
    
    // Show field error
    function showFieldError(field, message) {
        clearFieldError(field);
        
        field.style.borderColor = '#e74c3c';
        field.classList.add('error');
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'field-error';
        errorDiv.textContent = message;
        errorDiv.style.color = '#e74c3c';
        errorDiv.style.fontSize = '14px';
        errorDiv.style.marginTop = '5px';
        
        field.parentNode.appendChild(errorDiv);
    }
    
    // Clear field error
    function clearFieldError(field) {
        field.style.borderColor = '';
        field.classList.remove('error');
        
        const existingError = field.parentNode.querySelector('.field-error');
        if (existingError) {
            existingError.remove();
        }
    }
    
    // Show form error
    function showFormError(message) {
        const existingError = contactForm.querySelector('.form-error');
        if (existingError) {
            existingError.remove();
        }
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'form-error';
        errorDiv.textContent = message;
        errorDiv.style.color = '#e74c3c';
        errorDiv.style.textAlign = 'center';
        errorDiv.style.marginBottom = '20px';
        errorDiv.style.padding = '10px';
        errorDiv.style.backgroundColor = '#fdf2f2';
        errorDiv.style.borderRadius = '5px';
        errorDiv.style.border = '1px solid #fecaca';
        
        contactForm.insertBefore(errorDiv, contactForm.firstChild);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.remove();
            }
        }, 5000);
    }
    
    // Web3Forms will handle the actual submission
    // We just provide user feedback
    
    // Show form success message
    function showFormSuccess(message = 'Thank you! Your message has been sent successfully.') {
        const successDiv = document.createElement('div');
        successDiv.className = 'form-success';
        successDiv.innerHTML = `
            <div style="color: #27ae60; text-align: center; margin-bottom: 20px; padding: 15px; background-color: #d5f4e6; border-radius: 5px; border: 1px solid #a8e6cf;">
                <i class="fas fa-check-circle" style="margin-right: 10px;"></i>
                ${message}
            </div>
        `;
        
        contactForm.insertBefore(successDiv, contactForm.firstChild);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (successDiv.parentNode) {
                successDiv.remove();
            }
        }, 5000);
    }
}

// Smooth scrolling for navigation links
function initSmoothScrolling() {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            
            if (targetSection) {
                const offsetTop = targetSection.offsetTop - 80; // Account for any fixed headers
                
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// Initialize scroll animations
function initAnimations() {
    // Make sure all sections are visible
    const sections = document.querySelectorAll('.section');
    sections.forEach(section => {
        section.style.opacity = '1';
        section.style.transform = 'translateY(0)';
    });
    
    // Intersection Observer for fade-in animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, observerOptions);
    
    // Add animation classes to elements
    const animatedElements = document.querySelectorAll('.section-header, .about-text, .skills, .timeline-item, .portfolio-item, .contact-item');
    
    animatedElements.forEach((element, index) => {
        element.classList.add('fade-in');
        element.style.animationDelay = `${index * 0.1}s`;
        observer.observe(element);
    });
    
    // Add staggered animation to portfolio items
    const portfolioItems = document.querySelectorAll('.portfolio-item');
    portfolioItems.forEach((item, index) => {
        item.style.animationDelay = `${index * 0.1}s`;
    });
    
    // Add hover effects to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px) scale(1.05)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
    
    // Add typing effect to hero name
    const heroName = document.querySelector('.name');
    if (heroName) {
        const text = heroName.textContent;
        heroName.textContent = '';
        
        let i = 0;
        const typeWriter = () => {
            if (i < text.length) {
                heroName.textContent += text.charAt(i);
                i++;
                setTimeout(typeWriter, 100);
            }
        };
        
        // Start typing effect after preloader
        setTimeout(typeWriter, 1500);
    }
    
    // Typing effect for subtitle
    initTypingEffect();
}

// Typing effect for subtitle
function initTypingEffect() {
    const texts = [
        "I'm a Student",
        "I'm a Web Developer", 
        "I'm a Freelancer"
    ];
    
    let textIndex = 0;
    let charIndex = 0;
    let isDeleting = false;
    const typingElement = document.getElementById('typing-text');
    
    function typeText() {
        const currentText = texts[textIndex];
        
        if (isDeleting) {
            // Deleting characters
            typingElement.textContent = currentText.substring(0, charIndex - 1);
            charIndex--;
        } else {
            // Typing characters
            typingElement.textContent = currentText.substring(0, charIndex + 1);
            charIndex++;
        }
        
        let typeSpeed = isDeleting ? 50 : 100;
        
        if (!isDeleting && charIndex === currentText.length) {
            // Pause at end of text
            typeSpeed = 2000;
            isDeleting = true;
        } else if (isDeleting && charIndex === 0) {
            // Move to next text
            isDeleting = false;
            textIndex = (textIndex + 1) % texts.length;
            typeSpeed = 500;
        }
        
        setTimeout(typeText, typeSpeed);
    }
    
    // Start typing effect after name typing is complete
    setTimeout(typeText, 3000);
}

// Theme Toggle functionality
function initThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    const body = document.body;
    
    // Check for saved theme preference or default to light theme
    const savedTheme = localStorage.getItem('theme') || 'light';
    body.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
    
    // Create stars and comet for dark theme
    if (savedTheme === 'dark') {
        createStars();
        createComet();
    }
    
    themeToggle.addEventListener('click', function() {
        const currentTheme = body.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        body.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeIcon(newTheme);
        
        // Handle stars and comet
        if (newTheme === 'dark') {
            createStars();
            createComet();
        } else {
            removeStarsAndComet();
        }
    });
}

function updateThemeIcon(theme) {
    const themeToggle = document.getElementById('theme-toggle');
    const icon = themeToggle.querySelector('i');
    
    if (theme === 'dark') {
        icon.className = 'fas fa-sun';
    } else {
        icon.className = 'fas fa-moon';
    }
}

function createStars() {
    // Remove existing stars
    removeStarsAndComet();
    
    const starsContainer = document.createElement('div');
    starsContainer.className = 'stars';
    document.body.appendChild(starsContainer);
    
    // Create 100 stars with varying sizes and positions
    for (let i = 0; i < 100; i++) {
        const star = document.createElement('div');
        star.className = 'star';
        
        // Random size (1-4px)
        const size = Math.random() * 3 + 1;
        star.style.width = size + 'px';
        star.style.height = size + 'px';
        
        // Random position
        star.style.left = Math.random() * 100 + '%';
        star.style.top = Math.random() * 100 + '%';
        
        // Random animation delay
        star.style.animationDelay = Math.random() * 4 + 's';
        
        // Random animation duration
        star.style.animationDuration = (Math.random() * 3 + 2) + 's';
        
        starsContainer.appendChild(star);
    }
    
    // Create shooting stars occasionally
    createShootingStars();
}

function createShootingStars() {
    // Create 3-5 shooting stars
    const shootingStarCount = Math.floor(Math.random() * 3) + 3;
    
    for (let i = 0; i < shootingStarCount; i++) {
        setTimeout(() => {
            createShootingStar();
        }, i * 2000); // Stagger creation
    }
}

function createShootingStar() {
    const shootingStar = document.createElement('div');
    shootingStar.className = 'shooting-star';
    
    // Random starting position
    const startX = Math.random() * 100;
    const startY = Math.random() * 100;
    
    shootingStar.style.left = startX + '%';
    shootingStar.style.top = startY + '%';
    
    // Random animation delay
    shootingStar.style.animationDelay = Math.random() * 2 + 's';
    
    document.body.appendChild(shootingStar);
    
    // Remove after animation completes
    setTimeout(() => {
        if (shootingStar.parentNode) {
            shootingStar.parentNode.removeChild(shootingStar);
        }
    }, 5000);
}

function createComet() {
    const comet = document.createElement('div');
    comet.className = 'comet';
    
    // Random starting position
    comet.style.left = Math.random() * 100 + '%';
    comet.style.top = Math.random() * 100 + '%';
    
    // Random animation delay
    comet.style.animationDelay = Math.random() * 8 + 's';
    
    document.body.appendChild(comet);
    
    // Remove comet after animation completes
    setTimeout(() => {
        if (comet.parentNode) {
            comet.remove();
        }
    }, 8000);
    
    // Create new comet every 8 seconds
    setTimeout(() => {
        if (document.body.getAttribute('data-theme') === 'dark') {
            createComet();
        }
    }, 8000);
}

function removeStarsAndComet() {
    const stars = document.querySelector('.stars');
    const comets = document.querySelectorAll('.comet');
    const shootingStars = document.querySelectorAll('.shooting-star');
    
    if (stars) {
        stars.remove();
    }
    
    comets.forEach(comet => {
        comet.remove();
    });
    
    shootingStars.forEach(star => {
        star.remove();
    });
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Add CSS for animations (injected dynamically)
const animationStyles = `
    .fade-in {
        opacity: 0;
        transform: translateY(30px);
        transition: all 0.6s ease;
    }
    
    .fade-in.visible {
        opacity: 1;
        transform: translateY(0);
    }
    
    .field-error {
        color: #e74c3c;
        font-size: 14px;
        margin-top: 5px;
    }
    
    .form-error {
        color: #e74c3c;
        text-align: center;
        margin-bottom: 20px;
        padding: 10px;
        background-color: #fdf2f2;
        border-radius: 5px;
        border: 1px solid #fecaca;
    }
    
    .form-success {
        color: #27ae60;
        text-align: center;
        margin-bottom: 20px;
        padding: 15px;
        background-color: #d5f4e6;
        border-radius: 5px;
        border: 1px solid #a8e6cf;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-50px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(50px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
`;

// Inject animation styles
const styleSheet = document.createElement('style');
styleSheet.textContent = animationStyles;
document.head.appendChild(styleSheet);

// Add loading state styles
const loadingStyles = `
    .btn:disabled {
        opacity: 0.7;
        cursor: not-allowed;
    }
    
    .btn:disabled:hover {
        transform: none;
    }
`;

const loadingStyleSheet = document.createElement('style');
loadingStyleSheet.textContent = loadingStyles;
document.head.appendChild(loadingStyleSheet);

// Console welcome message
console.log('%c🚀 Portfolio Website Loaded Successfully!', 'color: #4A90E2; font-size: 16px; font-weight: bold;');
console.log('%cBuilt with ❤️ by Sameer Lamichhane', 'color: #666; font-size: 12px;');
