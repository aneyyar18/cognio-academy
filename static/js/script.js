document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.querySelector('.search-bar');
    const tagButtons = document.querySelectorAll('.tag-button');
    const tutorResults = document.querySelector('.tutor-results');

    // Theme switching functionality
    const themeToggle = document.getElementById('theme-toggle');
    const themeToggleMobile = document.getElementById('theme-toggle-mobile');
    const themeToggleSetting = document.getElementById('theme-toggle-setting');
    const themeStylesheet = document.getElementById('theme-stylesheet');
    
    // Load saved theme preference or default to dark
    const savedTheme = localStorage.getItem('theme') || 'dark';
    setTheme(savedTheme);
    
    // Theme toggle event listeners for navbar (if they exist)
    function handleThemeToggle() {
        const currentTheme = getCurrentTheme();
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        setTheme(newTheme);
        localStorage.setItem('theme', newTheme);
    }
    
    if (themeToggle) {
        themeToggle.addEventListener('click', handleThemeToggle);
    }
    
    if (themeToggleMobile) {
        themeToggleMobile.addEventListener('click', handleThemeToggle);
    }
    
    // Settings page theme toggle
    if (themeToggleSetting) {
        // Set initial state based on current theme
        themeToggleSetting.checked = getCurrentTheme() === 'light';
        
        themeToggleSetting.addEventListener('change', function() {
            const newTheme = this.checked ? 'light' : 'dark';
            setTheme(newTheme);
            localStorage.setItem('theme', newTheme);
        });
    }
    
    function getCurrentTheme() {
        if (themeStylesheet) {
            return themeStylesheet.href.includes('style-light.css') ? 'light' : 'dark';
        }
        return 'dark';
    }
    
    function setTheme(theme) {
        if (themeStylesheet) {
            const basePath = themeStylesheet.href.replace(/\/[^\/]*$/, '/');
            if (theme === 'light') {
                themeStylesheet.href = basePath + 'style-light.css';
                document.body.className = document.body.className.replace('bg-slate-900', 'bg-slate-50');
                document.body.className = document.body.className.replace('text-gray-200', 'text-gray-800');
                if (!document.body.className.includes('bg-slate-50')) {
                    document.body.className += ' bg-slate-50';
                }
                if (!document.body.className.includes('text-gray-800')) {
                    document.body.className += ' text-gray-800';
                }
            } else {
                themeStylesheet.href = basePath + 'style.css';
                document.body.className = document.body.className.replace('bg-slate-50', 'bg-slate-900');
                document.body.className = document.body.className.replace('text-gray-800', 'text-gray-200');
                if (!document.body.className.includes('bg-slate-900')) {
                    document.body.className += ' bg-slate-900';
                }
                if (!document.body.className.includes('text-gray-200')) {
                    document.body.className += ' text-gray-200';
                }
            }
        }
        
        // Update theme toggle button text/icon for both desktop and mobile
        const toggleButtons = [themeToggle, themeToggleMobile];
        toggleButtons.forEach(button => {
            if (button) {
                const icon = button.querySelector('i');
                const text = button.querySelector('.theme-text');
                if (theme === 'light') {
                    if (icon) {
                        icon.className = 'fas fa-moon';
                    }
                    if (text) {
                        text.textContent = button === themeToggleMobile ? 'Dark Theme' : 'Dark';
                    }
                } else {
                    if (icon) {
                        icon.className = 'fas fa-sun';
                    }
                    if (text) {
                        text.textContent = button === themeToggleMobile ? 'Light Theme' : 'Light';
                    }
                }
            }
        });
    }

    // Search button functionality (if you add a search button)
    if (searchInput) {
        searchInput.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                const query = searchInput.value.trim();
                if (query) {
                    performSearch(query);
                }
            }
        });
    }

    // Tag button functionality
    tagButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tag = this.textContent.trim();
            performSearch(tag);
        });
    });

    // Function to perform search and update tutor results
    function performSearch(query) {
        alert('Searching for: ' + query); // Example action

        // Here, you would typically make an API call or search your database
        // and update the tutorResults section with the new tutor profiles.
        // For now, we'll just simulate this by clearing and adding a sample result.

        tutorResults.innerHTML = ''; // Clear previous results

        // Example of adding a new tutor card dynamically
        const tutorCard = document.createElement('div');
        tutorCard.classList.add('tutor-card');
        tutorCard.innerHTML = `
            <img src="tutor-sample.jpg" alt="Sample Tutor">
            <div>
                <h3>${query} Tutor - Sample Subject</h3>
                <p>Sample description for ${query} tutor. Customize this with real data.</p>
            </div>
        `;
        tutorResults.appendChild(tutorCard);
    }

    // Example fade-in effect for tutor results (if needed)
    const tutorObserver = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, { threshold: 0.1 });

    const tutorItems = document.querySelectorAll('.tutor-card');
    tutorItems.forEach(item => {
        tutorObserver.observe(item);
    });

    // Function to animate tagline text (if you still use it)
    const taglineElement = document.getElementById('animated-text');
    if (taglineElement) {
        function animateTagline() {
            const text = taglineElement.textContent;
            taglineElement.textContent = ''; // Clear original text

            // Split text into spans and append to the element
            text.split('').forEach((char, index) => {
                const span = document.createElement('span');
                span.textContent = char;
                taglineElement.appendChild(span);

                // Set delay for each letter to create typing effect
                setTimeout(() => {
                    span.style.opacity = 1;
                }, 50 * index); // Adjust timing here if needed
            });
        }

        // Call the function to animate tagline text
        animateTagline();
    }
});

