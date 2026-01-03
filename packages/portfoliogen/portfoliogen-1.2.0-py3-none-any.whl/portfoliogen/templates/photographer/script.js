// Professional Photography Portfolio - Optimized Interactive JavaScript

document.addEventListener('DOMContentLoaded', function() {
    console.log('🎨 Photography Portfolio Loaded Successfully!');
    
    // Initialize all components
    initPreloader();
    initNavigation();
    initHeroAnimations();
    initPortfolioFilter();
    initLightbox();
    initTestimonialSlider();
    initContactForm();
    initScrollEffects();
    initCounterAnimations();
    initBackToTop();
    
    // Preloader with improved timeout handling
    function initPreloader() {
        const preloader = document.querySelector('.preloader');
        let hasLoaded = false;
        
        function hidePreloader() {
            if (hasLoaded || !preloader) return;
            hasLoaded = true;
            
            preloader.classList.add('hidden');
            document.body.classList.add('loaded');
            
            // Trigger hero animations after preloader
            setTimeout(() => {
                triggerHeroAnimations();
            }, 300);
        }
        
        // Hide preloader when page loads
        window.addEventListener('load', () => {
            setTimeout(hidePreloader, 300);
        });
        
        // Fallback: Hide preloader after maximum 2 seconds
        setTimeout(hidePreloader, 2000);
        
        // Also hide if DOM is ready and basic content is loaded
        if (document.readyState === 'complete') {
            setTimeout(hidePreloader, 300);
        }
    }
    
    // Navigation with improved hamburger menu
    function initNavigation() {
        const navbar = document.querySelector('.navbar');
        const hamburger = document.querySelector('.hamburger');
        const navMenu = document.querySelector('.nav-menu');
        const navLinks = document.querySelectorAll('.nav-link');
        
        if (!navbar) return;
        
        // Mobile menu toggle
        if (hamburger && navMenu) {
            hamburger.addEventListener('click', (e) => {
                e.stopPropagation();
                toggleMobileMenu();
            });
        }
        
        function toggleMobileMenu() {
            hamburger.classList.toggle('active');
            navMenu.classList.toggle('active');
            document.body.style.overflow = navMenu.classList.contains('active') ? 'hidden' : '';
        }
        
        // Close mobile menu on link click
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                closeMobileMenu();
            });
        });
        
        function closeMobileMenu() {
            hamburger?.classList.remove('active');
            navMenu?.classList.remove('active');
            document.body.style.overflow = '';
        }
        
        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (navMenu?.classList.contains('active') && 
                !hamburger?.contains(e.target) && 
                !navMenu?.contains(e.target)) {
                closeMobileMenu();
            }
        });
        
        // Close menu on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && navMenu?.classList.contains('active')) {
                closeMobileMenu();
            }
        });
        
        // Optimized navbar scroll effect
        let lastScrollY = window.scrollY;
        let ticking = false;
        
        function updateNavbar() {
            const currentScrollY = window.scrollY;
            
            if (currentScrollY > 100) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
            
            lastScrollY = currentScrollY;
            ticking = false;
        }
        
        window.addEventListener('scroll', () => {
            if (!ticking) {
                requestAnimationFrame(updateNavbar);
                ticking = true;
            }
        });
        
        // Smooth scrolling for navigation links with active state management
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                
                // Remove active class from all links first
                navLinks.forEach(l => l.classList.remove('active'));
                // Add active class to clicked link
                link.classList.add('active');
                
                const targetId = link.getAttribute('href');
                const targetSection = document.querySelector(targetId);
                
                if (targetSection) {
                    const headerOffset = 80;
                    const elementPosition = targetSection.offsetTop;
                    const offsetPosition = elementPosition - headerOffset;
                    
                    window.scrollTo({
                        top: offsetPosition,
                        behavior: 'smooth'
                    });
                }
            });
        });
        
        // Active section highlighting with improved logic
        const sections = document.querySelectorAll('section[id]');
        let activeNavTicking = false;
        
        function updateActiveNav() {
            const scrollPos = window.scrollY + 150; // Increased offset for better detection
            let activeSection = null;
            
            // Find the current active section
            sections.forEach(section => {
                const sectionTop = section.offsetTop;
                const sectionHeight = section.offsetHeight;
                const sectionId = section.getAttribute('id');
                
                if (scrollPos >= sectionTop && scrollPos < sectionTop + sectionHeight) {
                    activeSection = sectionId;
                }
            });
            
            // Update navigation links - ensure only one is active
            navLinks.forEach(link => {
                link.classList.remove('active');
                const href = link.getAttribute('href');
                if (href === `#${activeSection}`) {
                    link.classList.add('active');
                }
            });
            
            // If no section is active, activate home by default
            if (!activeSection && window.scrollY < 100) {
                const homeLink = document.querySelector('a[href="#home"]');
                if (homeLink) {
                    homeLink.classList.add('active');
                }
            }
            
            activeNavTicking = false;
        }
        
        window.addEventListener('scroll', () => {
            if (!activeNavTicking) {
                requestAnimationFrame(updateActiveNav);
                activeNavTicking = true;
            }
        });
    }
    
    // Hero Animations
    function initHeroAnimations() {
        const heroStats = document.querySelectorAll('.hero-stats .stat-number');
        
        // Animate hero stats on load
        function animateHeroStats() {
            heroStats.forEach((stat, index) => {
                const finalValue = parseInt(stat.getAttribute('data-count'));
                if (finalValue) {
                    animateCounter(stat, 0, finalValue, '', 2000, index * 200);
                }
            });
        }
        
        // Trigger stats animation when hero is visible
        const heroObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    setTimeout(animateHeroStats, 500);
                    heroObserver.unobserve(entry.target);
                }
            });
        }, { threshold: 0.3 });
        
        const heroSection = document.querySelector('.hero');
        if (heroSection) {
            heroObserver.observe(heroSection);
        }
    }
    
    function triggerHeroAnimations() {
        const heroElements = document.querySelectorAll('.hero-badge, .hero-title .title-line, .hero-subtitle, .hero-stats, .hero-buttons');
        
        heroElements.forEach((el, index) => {
            if (el) {
                setTimeout(() => {
                    el.style.opacity = '1';
                    el.style.transform = 'translateY(0)';
                }, index * 150);
            }
        });
    }
    
    // Portfolio Filter with improved performance
    function initPortfolioFilter() {
        const filterButtons = document.querySelectorAll('.filter-btn');
        const portfolioItems = document.querySelectorAll('.portfolio-item');
        
        if (!filterButtons.length || !portfolioItems.length) return;
        
        filterButtons.forEach(button => {
            button.addEventListener('click', () => {
                // Remove active class from all buttons
                filterButtons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
                
                const filterValue = button.getAttribute('data-filter');
                
                // Add loading effect
                const portfolioGrid = document.querySelector('.portfolio-grid');
                if (portfolioGrid) {
                    portfolioGrid.style.opacity = '0.7';
                }
                
                setTimeout(() => {
                    portfolioItems.forEach((item, index) => {
                        const category = item.getAttribute('data-category');
                        const shouldShow = filterValue === 'all' || category === filterValue;
                        
                        if (shouldShow) {
                            item.style.display = 'block';
                            setTimeout(() => {
                                item.style.opacity = '1';
                                item.style.transform = 'translateY(0) scale(1)';
                            }, index * 50);
                        } else {
                            item.style.opacity = '0';
                            item.style.transform = 'translateY(20px) scale(0.95)';
                            setTimeout(() => {
                                item.style.display = 'none';
                            }, 200);
                        }
                    });
                    
                    if (portfolioGrid) {
                        portfolioGrid.style.opacity = '1';
                    }
                }, 100);
            });
        });
        
        // Portfolio item hover effects
        portfolioItems.forEach(item => {
            const image = item.querySelector('.portfolio-image img');
            
            if (image) {
                item.addEventListener('mouseenter', () => {
                    image.style.transform = 'scale(1.05)';
                });
                
                item.addEventListener('mouseleave', () => {
                    image.style.transform = 'scale(1)';
                });
            }
        });
    }
    
    // Lightbox with improved functionality
    function initLightbox() {
        const portfolioItems = document.querySelectorAll('.portfolio-item');
        const lightbox = document.getElementById('lightbox');
        const lightboxImage = document.querySelector('.lightbox-image');
        const lightboxTitle = document.querySelector('.lightbox-title');
        const lightboxDescription = document.querySelector('.lightbox-description');
        const lightboxClose = document.querySelector('.lightbox-close');
        const lightboxPrev = document.querySelector('.lightbox-prev');
        const lightboxNext = document.querySelector('.lightbox-next');
        
        if (!lightbox || !portfolioItems.length) return;
        
        let currentImageIndex = 0;
        const images = Array.from(portfolioItems);
        
        // Open lightbox
        portfolioItems.forEach((item, index) => {
            const viewBtn = item.querySelector('[data-action="view"]');
            
            if (viewBtn) {
                viewBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    openLightbox(index);
                });
            }
            
            // Also open on item click
            item.addEventListener('click', () => {
                openLightbox(index);
            });
        });
        
        function openLightbox(index) {
            currentImageIndex = index;
            updateLightboxContent();
            lightbox.classList.add('active');
            document.body.style.overflow = 'hidden';
            
            // Add entrance animation
            const lightboxContent = document.querySelector('.lightbox-content');
            if (lightboxContent) {
                lightboxContent.style.transform = 'scale(0.9)';
                lightboxContent.style.opacity = '0';
                
                setTimeout(() => {
                    lightboxContent.style.transform = 'scale(1)';
                    lightboxContent.style.opacity = '1';
                }, 50);
            }
        }
        
        function updateLightboxContent() {
            const currentItem = images[currentImageIndex];
            if (!currentItem) return;
            
            const img = currentItem.querySelector('img');
            const title = currentItem.querySelector('.portfolio-info h3');
            const description = currentItem.querySelector('.portfolio-info p');
            
            if (img && lightboxImage) {
                lightboxImage.src = img.src;
                lightboxImage.alt = img.alt;
            }
            
            if (title && lightboxTitle) {
                lightboxTitle.textContent = title.textContent;
            }
            
            if (description && lightboxDescription) {
                lightboxDescription.textContent = description.textContent;
            }
        }
        
        // Close lightbox
        function closeLightbox() {
            const lightboxContent = document.querySelector('.lightbox-content');
            if (lightboxContent) {
                lightboxContent.style.transform = 'scale(0.9)';
                lightboxContent.style.opacity = '0';
            }
            
            setTimeout(() => {
                lightbox.classList.remove('active');
                document.body.style.overflow = '';
            }, 200);
        }
        
        // Event listeners
        if (lightboxClose) {
            lightboxClose.addEventListener('click', closeLightbox);
        }
        
        lightbox.addEventListener('click', (e) => {
            if (e.target === lightbox) {
                closeLightbox();
            }
        });
        
        // Navigation
        if (lightboxPrev) {
            lightboxPrev.addEventListener('click', () => {
                currentImageIndex = currentImageIndex > 0 ? currentImageIndex - 1 : images.length - 1;
                updateLightboxContent();
            });
        }
        
        if (lightboxNext) {
            lightboxNext.addEventListener('click', () => {
                currentImageIndex = currentImageIndex < images.length - 1 ? currentImageIndex + 1 : 0;
                updateLightboxContent();
            });
        }
        
        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (!lightbox.classList.contains('active')) return;
            
            switch (e.key) {
                case 'Escape':
                    closeLightbox();
                    break;
                case 'ArrowLeft':
                    lightboxPrev?.click();
                    break;
                case 'ArrowRight':
                    lightboxNext?.click();
                    break;
            }
        });
        
        // Portfolio item interactions
        portfolioItems.forEach(item => {
            const likeBtn = item.querySelector('[data-action="like"]');
            
            if (likeBtn) {
                likeBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    likeBtn.classList.toggle('liked');
                    
                    const icon = likeBtn.querySelector('i');
                    if (icon) {
                        if (likeBtn.classList.contains('liked')) {
                            icon.style.color = '#e74c3c';
                            icon.classList.remove('far');
                            icon.classList.add('fas');
                        } else {
                            icon.style.color = '';
                            icon.classList.remove('fas');
                            icon.classList.add('far');
                        }
                    }
                    
                    // Add animation
                    likeBtn.style.transform = 'scale(1.2)';
                    setTimeout(() => {
                        likeBtn.style.transform = 'scale(1)';
                    }, 200);
                });
            }
        });
    }
    
    // Fixed Testimonial Slider with proper refresh
    function initTestimonialSlider() {
        const testimonialCards = document.querySelectorAll('.testimonial-card');
        const dots = document.querySelectorAll('.dot');
        const prevBtn = document.querySelector('.prev-btn');
        const nextBtn = document.querySelector('.next-btn');
        
        if (!testimonialCards.length) return;
        
        let currentSlide = 0;
        const totalSlides = testimonialCards.length;
        let autoPlayInterval;
        let isTransitioning = false;
        
        function showSlide(index, direction = 'next') {
            if (isTransitioning) return;
            
            // Ensure index is within bounds
            if (index >= totalSlides) index = 0;
            if (index < 0) index = totalSlides - 1;
            
            isTransitioning = true;
            
            // Remove active class from current slide
            const currentCard = document.querySelector('.testimonial-card.active');
            if (currentCard) {
                currentCard.classList.remove('active');
                if (direction === 'next') {
                    currentCard.classList.add('prev');
                } else {
                    currentCard.style.transform = 'translateX(100px)';
                }
            }
            
            // Show new slide after a brief delay
            setTimeout(() => {
                // Reset all cards
                testimonialCards.forEach((card, i) => {
                    card.classList.remove('active', 'prev');
                    if (i === index) {
                        card.style.transform = direction === 'next' ? 'translateX(100px)' : 'translateX(-100px)';
                        card.style.opacity = '0';
                        
                        // Animate in the new card
                        setTimeout(() => {
                            card.classList.add('active');
                            card.style.transform = 'translateX(0)';
                            card.style.opacity = '1';
                        }, 50);
                    } else {
                        card.style.transform = i < index ? 'translateX(-100px)' : 'translateX(100px)';
                        card.style.opacity = '0';
                    }
                });
                
                // Update dots
                dots.forEach((dot, i) => {
                    dot.classList.toggle('active', i === index);
                });
                
                currentSlide = index;
                
                // Reset transition flag
                setTimeout(() => {
                    isTransitioning = false;
                }, 500);
                
            }, 100);
        }
        
        function nextSlide() {
            showSlide(currentSlide + 1, 'next');
        }
        
        function prevSlide() {
            showSlide(currentSlide - 1, 'prev');
        }
        
        function startAutoPlay() {
            stopAutoPlay(); // Clear any existing interval
            autoPlayInterval = setInterval(nextSlide, 5000);
        }
        
        function stopAutoPlay() {
            if (autoPlayInterval) {
                clearInterval(autoPlayInterval);
                autoPlayInterval = null;
            }
        }
        
        // Event listeners
        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                nextSlide();
                stopAutoPlay();
                setTimeout(startAutoPlay, 1000); // Restart autoplay after 1 second
            });
        }
        
        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                prevSlide();
                stopAutoPlay();
                setTimeout(startAutoPlay, 1000); // Restart autoplay after 1 second
            });
        }
        
        dots.forEach((dot, index) => {
            dot.addEventListener('click', () => {
                if (index !== currentSlide) {
                    const direction = index > currentSlide ? 'next' : 'prev';
                    showSlide(index, direction);
                    stopAutoPlay();
                    setTimeout(startAutoPlay, 1000); // Restart autoplay after 1 second
                }
            });
        });
        
        // Pause on hover
        const testimonialSlider = document.querySelector('.testimonials-slider');
        if (testimonialSlider) {
            testimonialSlider.addEventListener('mouseenter', stopAutoPlay);
            testimonialSlider.addEventListener('mouseleave', startAutoPlay);
        }
        
        // Touch/swipe support
        let startX = 0;
        let endX = 0;
        let startY = 0;
        let endY = 0;
        
        if (testimonialSlider) {
            testimonialSlider.addEventListener('touchstart', (e) => {
                startX = e.touches[0].clientX;
                startY = e.touches[0].clientY;
                stopAutoPlay();
            }, { passive: true });
            
            testimonialSlider.addEventListener('touchend', (e) => {
                endX = e.changedTouches[0].clientX;
                endY = e.changedTouches[0].clientY;
                handleSwipe();
                setTimeout(startAutoPlay, 1000);
            }, { passive: true });
        }
        
        function handleSwipe() {
            const swipeThreshold = 50;
            const diffX = startX - endX;
            const diffY = Math.abs(startY - endY);
            
            // Only handle horizontal swipes
            if (Math.abs(diffX) > swipeThreshold && diffY < 100) {
                if (diffX > 0) {
                    nextSlide();
                } else {
                    prevSlide();
                }
            }
        }
        
        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (testimonialSlider && isElementInViewport(testimonialSlider)) {
                switch (e.key) {
                    case 'ArrowLeft':
                        e.preventDefault();
                        prevSlide();
                        stopAutoPlay();
                        setTimeout(startAutoPlay, 1000);
                        break;
                    case 'ArrowRight':
                        e.preventDefault();
                        nextSlide();
                        stopAutoPlay();
                        setTimeout(startAutoPlay, 1000);
                        break;
                }
            }
        });
        
        // Helper function to check if element is in viewport
        function isElementInViewport(el) {
            const rect = el.getBoundingClientRect();
            return (
                rect.top >= 0 &&
                rect.left >= 0 &&
                rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                rect.right <= (window.innerWidth || document.documentElement.clientWidth)
            );
        }
        
        // Initialize first slide and start autoplay
        showSlide(0, 'next');
        setTimeout(startAutoPlay, 1000); // Start autoplay after initial load
        
        // Pause autoplay when page is not visible
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                stopAutoPlay();
            } else {
                startAutoPlay();
            }
        });
    }
    
    // Contact Form with improved validation
    function initContactForm() {
        const contactForm = document.querySelector('.form');
        
        if (!contactForm) return;
        
        contactForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const submitBtn = contactForm.querySelector('button[type="submit"]');
            const formData = new FormData(contactForm);
            
            // Validate form before submission
            if (!validateForm(contactForm)) {
                showNotification('Please fill in all required fields correctly.', 'error');
                return;
            }
            
            // Add loading state
            if (submitBtn) {
                submitBtn.classList.add('loading');
                submitBtn.disabled = true;
            }
            
            // Simulate form submission (replace with actual endpoint)
            try {
                await simulateFormSubmission(formData);
                
                // Success
                showNotification('Message sent successfully! I\'ll get back to you soon.', 'success');
                contactForm.reset();
                
                // Add success animation
                contactForm.style.transform = 'scale(0.98)';
                setTimeout(() => {
                    contactForm.style.transform = 'scale(1)';
                }, 200);
                
            } catch (error) {
                showNotification('Sorry, there was an error sending your message. Please try again.', 'error');
            } finally {
                if (submitBtn) {
                    submitBtn.classList.remove('loading');
                    submitBtn.disabled = false;
                }
            }
        });
        
        // Real-time form validation
        const inputs = contactForm.querySelectorAll('input, textarea, select');
        
        inputs.forEach(input => {
            input.addEventListener('blur', validateField);
            input.addEventListener('input', clearFieldError);
        });
        
        function validateForm(form) {
            const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
            let isValid = true;
            
            inputs.forEach(input => {
                if (!validateField({ target: input })) {
                    isValid = false;
                }
            });
            
            return isValid;
        }
        
        function validateField(e) {
            const field = e.target;
            const value = field.value.trim();
            
            // Remove existing error
            clearFieldError(e);
            
            // Validation rules
            if (field.hasAttribute('required') && !value) {
                showFieldError(field, 'This field is required');
                return false;
            }
            
            if (field.type === 'email' && value) {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(value)) {
                    showFieldError(field, 'Please enter a valid email address');
                    return false;
                }
            }
            
            if (field.type === 'tel' && value) {
                const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
                if (!phoneRegex.test(value.replace(/[\s\-\(\)]/g, ''))) {
                    showFieldError(field, 'Please enter a valid phone number');
                    return false;
                }
            }
            
            return true;
        }
        
        function showFieldError(field, message) {
            const formGroup = field.closest('.form-group');
            if (!formGroup) return;
            
            // Remove existing error
            const existingError = formGroup.querySelector('.field-error');
            if (existingError) {
                existingError.remove();
            }
            
            // Add error message
            const errorElement = document.createElement('div');
            errorElement.className = 'field-error';
            errorElement.textContent = message;
            errorElement.style.cssText = 'color: #e74c3c; font-size: 0.8rem; margin-top: 0.3rem;';
            
            formGroup.appendChild(errorElement);
            field.style.borderColor = '#e74c3c';
        }
        
        function clearFieldError(e) {
            const field = e.target;
            const formGroup = field.closest('.form-group');
            if (!formGroup) return;
            
            const errorElement = formGroup.querySelector('.field-error');
            if (errorElement) {
                errorElement.remove();
            }
            
            field.style.borderColor = '';
        }
        
        async function simulateFormSubmission(formData) {
            // Simulate API call
            return new Promise((resolve, reject) => {
                setTimeout(() => {
                    // Simulate 95% success rate
                    if (Math.random() > 0.05) {
                        resolve();
                    } else {
                        reject(new Error('Network error'));
                    }
                }, 1500);
            });
        }
    }
    
    // Optimized Scroll Effects
    function initScrollEffects() {
        // Reveal animations with Intersection Observer
        const revealElements = document.querySelectorAll('.service-card, .portfolio-item, .feature-item');
        
        const revealObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                    revealObserver.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });
        
        revealElements.forEach(element => {
            element.style.opacity = '0';
            element.style.transform = 'translateY(30px)';
            element.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            revealObserver.observe(element);
        });
    }
    
    // Counter Animations
    function initCounterAnimations() {
        const counters = document.querySelectorAll('.stat-number[data-count]');
        
        const counterObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const counter = entry.target;
                    const finalValue = parseInt(counter.getAttribute('data-count'));
                    if (finalValue) {
                        animateCounter(counter, 0, finalValue, '+', 2000);
                    }
                    counterObserver.unobserve(counter);
                }
            });
        }, { threshold: 0.5 });
        
        counters.forEach(counter => {
            counterObserver.observe(counter);
        });
    }
    
    function animateCounter(element, start, end, suffix = '', duration = 2000, delay = 0) {
        setTimeout(() => {
            const range = end - start;
            const increment = range / (duration / 16);
            let current = start;
            
            const timer = setInterval(() => {
                current += increment;
                if (current >= end) {
                    current = end;
                    clearInterval(timer);
                }
                element.textContent = Math.floor(current) + suffix;
            }, 16);
        }, delay);
    }
    
    // Back to Top Button
    function initBackToTop() {
        const backToTopBtn = document.querySelector('.back-to-top');
        
        if (!backToTopBtn) return;
        
        let scrollTicking = false;
        
        function updateBackToTop() {
            if (window.scrollY > 300) {
                backToTopBtn.classList.add('visible');
            } else {
                backToTopBtn.classList.remove('visible');
            }
            scrollTicking = false;
        }
        
        window.addEventListener('scroll', () => {
            if (!scrollTicking) {
                requestAnimationFrame(updateBackToTop);
                scrollTicking = true;
            }
        });
        
        backToTopBtn.addEventListener('click', () => {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
    
    // Utility Functions
    function showNotification(message, type = 'info') {
        // Remove existing notifications
        const existingNotifications = document.querySelectorAll('.notification');
        existingNotifications.forEach(notification => {
            notification.remove();
        });
        
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
                <span>${message}</span>
            </div>
        `;
        
        // Style the notification
        const bgColor = type === 'success' ? '#27ae60' : type === 'error' ? '#e74c3c' : '#3498db';
        Object.assign(notification.style, {
            position: 'fixed',
            top: '2rem',
            right: '2rem',
            background: bgColor,
            color: 'white',
            padding: '1rem 1.5rem',
            borderRadius: '10px',
            boxShadow: '0 10px 30px rgba(0, 0, 0, 0.2)',
            zIndex: '10000',
            transform: 'translateX(100%)',
            transition: 'transform 0.3s ease',
            maxWidth: '400px',
            fontSize: '0.9rem'
        });
        
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);
        
        // Remove after delay
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 4000);
    }
    
    // Performance optimization - debounce function
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
    
    // Add smooth loading for images
    function initImageLoading() {
        const images = document.querySelectorAll('img');
        
        images.forEach(img => {
            img.addEventListener('load', () => {
                img.style.opacity = '1';
            });
            
            // Set initial opacity
            img.style.opacity = '0';
            img.style.transition = 'opacity 0.3s ease';
            
            // If image is already loaded
            if (img.complete) {
                img.style.opacity = '1';
            }
        });
    }
    
    // Initialize image loading
    initImageLoading();
    
    console.log('✅ All components initialized successfully!');
});