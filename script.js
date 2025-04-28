document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.querySelector('.search-bar');
    const tagButtons = document.querySelectorAll('.tag-button');
    const tutorResults = document.querySelector('.tutor-results');

    // Search button functionality (if you add a search button)
    searchInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            const query = searchInput.value.trim();
            if (query) {
                performSearch(query);
            }
        }
    });

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

