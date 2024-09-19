function toggleLoading(id, show) {
    const element = document.getElementById(id);
    if (show) {
        element.classList.remove('hidden');
    } else {
        element.classList.add('hidden');
    }
}

// Login function
function login() {
    const registerNumber = document.getElementById('register_number_input').value;

    // Check if register number is not empty
    if (!registerNumber) {
        document.getElementById('error').textContent = 'Please enter your register number!';
        return;
    }

    toggleLoading('loading-login', true);

    fetch('http://localhost:5000/api/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ register_number: registerNumber }),
        credentials: 'include'
    })
    .then(response => response.json())
    .then(data => {
        toggleLoading('loading-login', false);

        if (data.message === "Login successful") {
            document.getElementById('login-form').style.display = 'none';
            document.getElementById('user-details').classList.remove('hidden');
            document.getElementById('interests-form').classList.remove('hidden');

            // Display user details
            document.getElementById('name').textContent = data.user.name;
            document.getElementById('register_number').textContent = data.user.register_number;
            document.getElementById('cgpa').textContent = data.user.cgpa;
            document.getElementById('dbms').textContent = data.user.dbms;
            document.getElementById('ai').textContent = data.user.ai;
            document.getElementById('os').textContent = data.user.os;
            document.getElementById('cc').textContent = data.user.cc;
            document.getElementById('fla').textContent = data.user.fla;
            document.getElementById('cn').textContent = data.user.cn;
            document.getElementById('sepm').textContent = data.user.sepm;

            document.getElementById('message').textContent = 'Login successful!';
            document.getElementById('error').textContent = ''; // Clear error message
        } else {
            document.getElementById('error').textContent = 'Invalid credentials!';
        }
    })
    .catch((error) => {
        toggleLoading('loading-login', false);
        console.error('Error:', error);
        document.getElementById('error').textContent = 'An error occurred!';
    });
}

// Add interests function
function addInterests() {
    const registerNumber = document.getElementById('register_number').textContent;

    // Get selected interests
    const selectedInterests = [];
    document.querySelectorAll('input[type="checkbox"]:checked').forEach(checkbox => {
        selectedInterests.push(checkbox.value);
    });

    if (selectedInterests.length === 0) {
        document.getElementById('message').textContent = 'Please select at least one interest!';
        return;
    }

    fetch('http://localhost:5000/api/add-interests', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ register_number: registerNumber, user_choice: selectedInterests.join(',') }),
        credentials: 'include',
        mode:'cors'
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('message').textContent = 'Interests updated successfully!';
    })
    .catch((error) => {
        console.error('Error:', error);
        document.getElementById('error').textContent = 'An error occurred while updating interests!';
    });
}

// Get recommendations function
// Get recommendations function
document.addEventListener('DOMContentLoaded', function () {
    // Get recommendations function
    function getRecommendations() {
        const registerNumber = document.getElementById('register_number').textContent;

        toggleLoading('loading-recommendations', true);

        fetch('http://localhost:5000/api/recommendations', {
            method: 'GET',
            credentials: 'include'  // Include credentials (cookies/sessions)
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                toggleLoading('loading-recommendations', false);

                const coursesList = document.getElementById('recommended-courses');
                coursesList.innerHTML = ''; // Clear the list

                if (!data || !data.recommended_courses || data.recommended_courses.length === 0) {
                    document.getElementById('message').textContent = 'No recommendations found based on your interests.';
                    document.getElementById('courses').classList.add('hidden'); // Hide the courses section if empty
                    return;
                }

                const courses = data.recommended_courses;  // Expecting an array of recommended courses

                courses.forEach(course => {
                    const li = document.createElement('li');
                    li.textContent = course; // Display each recommended course
                    coursesList.appendChild(li);
                });
                document.getElementById('courses').classList.remove('hidden'); // Show the courses section
                document.getElementById('message').textContent = ''; // Clear message
            })
            .catch((error) => {
                toggleLoading('loading-recommendations', false);
                console.error('Error fetching recommendations:', error);
                document.getElementById('error').textContent = 'An error occurred while fetching recommendations!';
            });
    }

    // Example function call or event listener attachment
    document.getElementById('getRecommendationsButton').addEventListener('click', getRecommendations);
});
