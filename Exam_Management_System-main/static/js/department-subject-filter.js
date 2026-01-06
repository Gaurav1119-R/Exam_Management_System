/**
 * Department-Subject Filtering
 * Dynamically loads subjects based on selected department
 */

document.addEventListener('DOMContentLoaded', function() {
    // Handle department selection in student profile
    const departmentSelect = document.getElementById('id_department') || document.getElementById('department-select');
    const subjectSelectContainer = document.getElementById('subject-select-container');
    
    if (departmentSelect) {
        departmentSelect.addEventListener('change', function() {
            loadSubjectsByDepartment(this.value);
        });
    }

    // Handle subject selection in question paper form
    const adminSubjectSelect = document.getElementById('id_subject');
    if (adminSubjectSelect) {
        adminSubjectSelect.addEventListener('change', function() {
            loadQuestionsBySubject(this.value);
        });
    }
});

/**
 * Fetch subjects by department via AJAX
 * @param {string} departmentCode - The department code (e.g., 'BCA', 'IT')
 */
function loadSubjectsByDepartment(departmentCode) {
    if (!departmentCode) {
        clearSubjectSelect();
        return;
    }

    const url = `/exams/admin/api/subjects-by-department/?department=${encodeURIComponent(departmentCode)}`;

    fetch(url, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json',
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            populateSubjectSelect(data.subjects);
        } else {
            console.error('Error:', data.error);
            clearSubjectSelect();
        }
    })
    .catch(error => {
        console.error('Fetch error:', error);
        clearSubjectSelect();
    });
}

/**
 * Populate subject select dropdown with fetched subjects
 * @param {Array} subjects - Array of subject objects with id, code, and name
 */
function populateSubjectSelect(subjects) {
    const container = document.getElementById('subject-select-container');
    
    if (!container) {
        // Create a simple list if container doesn't exist
        const subjectList = document.getElementById('subject-list');
        if (subjectList) {
            subjectList.innerHTML = '';
            subjects.forEach(subject => {
                const li = document.createElement('li');
                li.className = 'list-group-item';
                li.textContent = `${subject.code} - ${subject.name}`;
                li.dataset.subjectId = subject.id;
                subjectList.appendChild(li);
            });
        }
        return;
    }

    // Update select dropdown if it exists
    const select = container.querySelector('select');
    if (select) {
        select.innerHTML = '<option value="">-- Select Subject --</option>';
        subjects.forEach(subject => {
            const option = document.createElement('option');
            option.value = subject.id;
            option.textContent = `${subject.code} - ${subject.name}`;
            select.appendChild(option);
        });
    }
}

/**
 * Clear the subject select dropdown
 */
function clearSubjectSelect() {
    const container = document.getElementById('subject-select-container');
    if (container) {
        const select = container.querySelector('select');
        if (select) {
            select.innerHTML = '<option value="">-- Select Subject --</option>';
        }
    }

    const subjectList = document.getElementById('subject-list');
    if (subjectList) {
        subjectList.innerHTML = '';
    }
}

/**
 * Load questions by subject (for admin paper creation)
 * @param {string} subjectId - The subject ID
 */
function loadQuestionsBySubject(subjectId) {
    if (!subjectId) {
        return;
    }

    // This would typically update a questions checkbox list
    // The form already handles this server-side through the form's __init__ method
}

/**
 * Initialize department-subject filtering on page load
 */
function initializeDepartmentFiltering() {
    const departmentSelect = document.getElementById('id_department') || document.getElementById('department-select');
    if (departmentSelect && departmentSelect.value) {
        loadSubjectsByDepartment(departmentSelect.value);
    }
}

// Call initialization on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeDepartmentFiltering);
} else {
    initializeDepartmentFiltering();
}
