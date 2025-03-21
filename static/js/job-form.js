// Job form functionality including URL extraction

document.addEventListener('DOMContentLoaded', function() {
    const extractBtn = document.getElementById('extract-btn');
    const jobUrlInput = document.getElementById('job-url');
    const extractionStatus = document.getElementById('extraction-status');
    const jobForm = document.getElementById('job-form');
    
    // Form fields that will be populated by extraction
    const formFields = {
        title: document.getElementById('title'),
        company: document.getElementById('company'),
        location: document.getElementById('location'),
        description: document.getElementById('description'),
        requirements: document.getElementById('requirements'),
        salary_range: document.getElementById('salary_range'),
        job_type: document.getElementById('job_type'),
        application_url: document.getElementById('application_url'),
        source_url: document.getElementById('source_url')
    };
    
    // Add event listener to extraction button
    if (extractBtn && jobUrlInput && extractionStatus) {
        extractBtn.addEventListener('click', function() {
            const url = jobUrlInput.value.trim();
            
            if (!url) {
                showExtractionStatus('error', 'Please enter a valid URL');
                return;
            }
            
            // Validate URL format
            if (!isValidURL(url)) {
                showExtractionStatus('error', 'Invalid URL format. Please enter a complete URL (e.g., https://example.com/job)');
                return;
            }
            
            // Show loading status
            showExtractionStatus('loading', 'Extracting job details...');
            
            // Disable extraction button during processing
            extractBtn.disabled = true;
            extractBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Extracting...';
            
            // Make API request to extract job details
            fetchJobDetails(url)
                .then(data => {
                    if (data.error) {
                        showExtractionStatus('error', data.error);
                    } else {
                        populateForm(data);
                        showExtractionStatus('success', 'Job details extracted successfully! Please review and edit if needed.');
                    }
                })
                .catch(error => {
                    console.error('Error extracting job details:', error);
                    showExtractionStatus('error', 'Failed to extract job details. Please try again or fill the form manually.');
                })
                .finally(() => {
                    // Re-enable extraction button
                    extractBtn.disabled = false;
                    extractBtn.innerHTML = '<i class="fas fa-magic"></i> Extract';
                });
        });
    }
    
    // Helper function to validate URL format
    function isValidURL(url) {
        try {
            new URL(url);
            return true;
        } catch (e) {
            return false;
        }
    }
    
    // Function to fetch job details from the server
    async function fetchJobDetails(url) {
        try {
            const response = await fetch('/api/extract-job', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: url })
            });
            
            return await response.json();
        } catch (error) {
            console.error('Error in API request:', error);
            throw error;
        }
    }
    
    // Function to populate the form with extracted data
    function populateForm(data) {
        // For each field in our form, populate with extracted data if available
        for (const field in formFields) {
            if (formFields[field] && data[field]) {
                if (field === 'job_type') {
                    // For select elements, find the matching option
                    const options = formFields[field].options;
                    const jobType = data[field].trim();
                    
                    let found = false;
                    for (let i = 0; i < options.length; i++) {
                        if (options[i].value.toLowerCase() === jobType.toLowerCase()) {
                            formFields[field].selectedIndex = i;
                            found = true;
                            break;
                        }
                    }
                    
                    // If no exact match, use the first option
                    if (!found) {
                        formFields[field].selectedIndex = 0;
                    }
                } else {
                    // For text inputs and textareas
                    formFields[field].value = data[field];
                }
            }
        }
        
        // Set the application URL if it was extracted or use the source URL
        if (data.application_url) {
            formFields.application_url.value = data.application_url;
        } else if (data.source_url) {
            formFields.application_url.value = data.source_url;
        }
        
        // Set the source URL hidden field
        formFields.source_url.value = data.source_url;
        
        // Add visual indication that fields were populated
        highlightPopulatedFields();
    }
    
    // Function to show extraction status messages
    function showExtractionStatus(type, message) {
        extractionStatus.innerHTML = '';
        extractionStatus.className = '';
        
        let icon, alertClass;
        
        switch (type) {
            case 'loading':
                icon = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>';
                alertClass = 'alert alert-info';
                break;
            case 'success':
                icon = '<i class="fas fa-check-circle me-2"></i>';
                alertClass = 'alert alert-success';
                break;
            case 'error':
                icon = '<i class="fas fa-exclamation-circle me-2"></i>';
                alertClass = 'alert alert-danger';
                break;
            default:
                icon = '<i class="fas fa-info-circle me-2"></i>';
                alertClass = 'alert alert-info';
        }
        
        extractionStatus.className = alertClass;
        extractionStatus.innerHTML = `${icon}${message}`;
    }
    
    // Function to highlight fields that were populated by extraction
    function highlightPopulatedFields() {
        for (const field in formFields) {
            if (formFields[field] && formFields[field].value) {
                formFields[field].classList.add('is-valid');
                
                // Add animation to show the field was populated
                formFields[field].classList.add('field-populated');
                
                // Remove the animation class after animation completes
                setTimeout(() => {
                    formFields[field].classList.remove('field-populated');
                }, 1000);
            }
        }
    }
    
    // Form validation on submit
    if (jobForm) {
        jobForm.addEventListener('submit', function(event) {
            const requiredFields = ['title', 'company', 'description', 'application_url'];
            let valid = true;
            
            requiredFields.forEach(field => {
                const input = document.getElementById(field);
                if (!input.value.trim()) {
                    input.classList.add('is-invalid');
                    valid = false;
                } else {
                    input.classList.remove('is-invalid');
                    input.classList.add('is-valid');
                }
            });
            
            if (!valid) {
                event.preventDefault();
                showExtractionStatus('error', 'Please fill in all required fields marked with *');
                
                // Scroll to the first invalid field
                const firstInvalid = document.querySelector('.is-invalid');
                if (firstInvalid) {
                    firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    firstInvalid.focus();
                }
            }
        });
        
        // Add event listeners to remove validation styling on input
        const inputs = jobForm.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('input', function() {
                this.classList.remove('is-invalid');
                if (this.value.trim()) {
                    this.classList.add('is-valid');
                } else {
                    this.classList.remove('is-valid');
                }
            });
        });
    }
    
    // Initialize URL input to capture paste events
    if (jobUrlInput) {
        jobUrlInput.addEventListener('paste', function(e) {
            // Short timeout to allow the paste to complete
            setTimeout(() => {
                if (this.value.trim()) {
                    // Auto-extract on paste if URL seems valid
                    if (isValidURL(this.value.trim())) {
                        extractBtn.click();
                    }
                }
            }, 100);
        });
    }
});

// Add CSS for form field animation
(function() {
    const style = document.createElement('style');
    style.textContent = `
        @keyframes fieldPopulatedAnimation {
            0% { background-color: rgba(108, 99, 255, 0.1); }
            50% { background-color: rgba(108, 99, 255, 0.2); }
            100% { background-color: transparent; }
        }
        
        .field-populated {
            animation: fieldPopulatedAnimation 1s ease;
        }
        
        .error-shake {
            animation: shake 0.5s cubic-bezier(.36,.07,.19,.97) both;
        }
        
        @keyframes shake {
            10%, 90% { transform: translate3d(-1px, 0, 0); }
            20%, 80% { transform: translate3d(2px, 0, 0); }
            30%, 50%, 70% { transform: translate3d(-4px, 0, 0); }
            40%, 60% { transform: translate3d(4px, 0, 0); }
        }
    `;
    document.head.appendChild(style);
})();
