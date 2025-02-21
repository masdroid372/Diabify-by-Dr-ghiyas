document.addEventListener('DOMContentLoaded', function() {
    const bloodSugarForm = document.getElementById('bloodSugarForm');
    const readingResults = document.getElementById('readingResults');
    
    bloodSugarForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const reading = {
            blood_sugar: parseFloat(document.getElementById('bloodSugarValue').value),
            unit: document.getElementById('bloodSugarUnit').value,
            meal_status: document.querySelector('input[name="mealStatus"]:checked').value,
            symptoms: document.getElementById('symptoms').value
        };
        
        try {
            const response = await fetch('/api/reading', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(reading)
            });
            
            const result = await response.json();
            displayResults(result);
        } catch (error) {
            console.error('Error:', error);
            showError('Error submitting reading. Please try again.');
        }
    });
    
    function displayResults(result) {
        let alertClass = 'alert-info';
        
        if (result.alert_level === 'danger') {
            alertClass = 'alert-danger';
        } else if (result.alert_level === 'warning') {
            alertClass = 'alert-warning';
        }
        
        readingResults.innerHTML = `
            <div class="alert ${alertClass}">
                <h5>Analysis Results:</h5>
                <ul>
                    ${result.messages.map(msg => `<li>${msg}</li>`).join('')}
                </ul>
                ${result.recommendations.length > 0 ? `
                    <h5>Recommendations:</h5>
                    <ul>
                        ${result.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                    </ul>
                ` : ''}
            </div>
        `;
        
        // Scroll to results
        readingResults.scrollIntoView({ behavior: 'smooth' });
    }
    
    function showError(message) {
        readingResults.innerHTML = `
            <div class="alert alert-danger">
                <strong>Error:</strong> ${message}
            </div>
        `;
    }
    
    // Unit conversion helper
    document.getElementById('bloodSugarUnit').addEventListener('change', function(e) {
        const valueInput = document.getElementById('bloodSugarValue');
        const currentValue = parseFloat(valueInput.value);
        
        if (!isNaN(currentValue)) {
            if (e.target.value === 'mg/dL') {
                valueInput.value = (currentValue * 18.0182).toFixed(0);
            } else {
                valueInput.value = (currentValue / 18.0182).toFixed(1);
            }
        }
    });
    
    // Clear form after submission
    function clearForm() {
        document.getElementById('bloodSugarValue').value = '';
        document.getElementById('symptoms').value = '';
    }
});
