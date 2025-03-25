// Job categories and subcategories
const JOB_CATEGORIES = {
    "technology": ["Software Development", "IT & Networking", "Data Science", "DevOps", "Cybersecurity", "Product Management"],
    "creative": ["Design", "Writing", "Marketing", "Video Production", "Animation", "Social Media"],
    "professional": ["Accounting", "Legal", "HR", "Customer Service", "Sales", "Consulting"],
    "healthcare": ["Telemedicine", "Medical Coding", "Health Coaching", "Mental Health", "Medical Writing"],
    "education": ["Online Teaching", "Curriculum Development", "Educational Consulting", "Tutoring", "Course Creation"],
    "skilled-trades": ["Remote Technician", "Project Management", "Quality Assurance", "Virtual Installation Support"]
};

function updateSubcategories() {
    const categorySelect = document.getElementById('category');
    const subcategorySelect = document.getElementById('subcategory');
    
    if (!categorySelect || !subcategorySelect) return;
    
    const selectedCategory = categorySelect.value;
    
    // Clear current options
    subcategorySelect.innerHTML = '';
    
    // Add default option
    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.textContent = selectedCategory ? 'Select Subcategory' : 'Select a category first';
    subcategorySelect.appendChild(defaultOption);
    
    // If a category is selected, add its subcategories
    if (selectedCategory && JOB_CATEGORIES[selectedCategory]) {
        JOB_CATEGORIES[selectedCategory].forEach(subcategory => {
            const option = document.createElement('option');
            option.value = subcategory;
            option.textContent = subcategory;
            subcategorySelect.appendChild(option);
        });
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    const categorySelect = document.getElementById('category');
    if (categorySelect) {
        categorySelect.addEventListener('change', updateSubcategories);
        // Initialize subcategories based on current category selection
        updateSubcategories();
    }
});