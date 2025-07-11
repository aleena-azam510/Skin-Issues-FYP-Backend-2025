let currentPage = 1;
const remediesPerPage = 3;

document.addEventListener('DOMContentLoaded', function () {
    const video = document.getElementById('herbal-camera-feed');
    const canvas = document.getElementById('canvas');
    const preview = document.getElementById('imagePreview');
    const startCameraBtn = document.getElementById('startCameraBtn');
    const captureBtn = document.getElementById('captureBtn');
    const predictBtn = document.getElementById('herbal-analyze-btn');
    const resultsSection = document.getElementById('results'); // This is the diagnosis summary card
    const diagnosisConditionNameEl = document.getElementById('diagnosisConditionName');
    const diagnosisConfidenceLevelEl = document.getElementById('diagnosisConfidenceLevel');
    const diagnosisConfidenceTextEl = document.getElementById('diagnosisConfidenceText');
    const herbalDetailedRemediesGrid = document.getElementById('herbalDetailedRemediesGrid');
    const spinner = document.getElementById('spinner');
    const fileInput = document.getElementById('fileInput');

    let stream = null;
    const ctx = canvas.getContext('2d');
    const remedyState = {}; // To keep track of current remedy index for each issue
    let latestData = null;

    // --- Event Listeners (Remain mostly the same) ---
    startCameraBtn.addEventListener('click', async () => {
        try {
            stream = await navigator.mediaDevices.getUserMedia({ video: true });
            video.srcObject = stream;
            video.play();
            video.style.display = 'block';
            captureBtn.disabled = false;
            preview.style.display = 'none';
            hideElement(canvas); // Ensure canvas is hidden when camera starts
        } catch (err) {
            console.error('Error accessing camera:', err);
            alert('Could not access the camera. Please check permissions.');
        }
    });

    captureBtn.addEventListener('click', () => {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

        preview.src = canvas.toDataURL('image/jpeg');
        preview.style.display = 'block';
        video.style.display = 'none';
        showElement(preview); // Explicitly show preview after capture
        hideElement(canvas); // Hide canvas immediately after drawing if it's for bounding boxes later

        predictBtn.disabled = false;

        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            stream = null;
        }
    });

    fileInput.addEventListener('change', () => {
        const file = fileInput.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (event) => {
            preview.src = event.target.result;
            showElement(preview);
            hideElement(video);
            hideElement(canvas); // Ensure canvas is hidden when image is loaded from file
            predictBtn.disabled = false;
        };
        reader.readAsDataURL(file);
    });

    predictBtn.addEventListener('click', async () => {
        // Clear previous results from both summary and detailed sections
        diagnosisConditionNameEl.textContent = 'Analyzing...';
        diagnosisConfidenceLevelEl.style.width = '0%';
        diagnosisConfidenceTextEl.textContent = 'Confidence: --%';
        herbalDetailedRemediesGrid.innerHTML = ''; // Clear the detailed remedies grid

        showSpinner();
        predictBtn.disabled = true;

        try {
            const formData = new FormData();

            if (preview.src.startsWith('data:image')) {
                const blob = await fetch(preview.src).then(res => res.blob());
                formData.append('file', blob, 'skin_image.jpg');
            } else if (fileInput.files.length > 0) {
                formData.append('file', fileInput.files[0]);
            } else {
                throw new Error('No image selected or captured.');
            }

            const response = await fetch('/api/predict/', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                // Try to parse error message from response body if available
                const errorData = await response.json().catch(() => ({ message: response.statusText }));
                throw new Error(errorData.message || 'Server responded with an unknown error');
            }

            const data = await response.json();
            latestData = data;
            currentPage = 1;

            displayResults(data);
        } catch (error) {
            console.error('Error:', error);
            // Display error in the summary section
            diagnosisConditionNameEl.textContent = 'Analysis Error';
            diagnosisConfidenceTextEl.textContent = `Error: ${error.message || 'Failed to process image'}`;
            // Optionally clear image and bounding boxes on error
            preview.style.display = 'none';
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            hideElement(canvas); // Ensure canvas is hidden on error
        } finally {
            hideSpinner();
            predictBtn.disabled = false;
        }
    });

    // --- Helper Functions ---
    function showElement(el) {
        el.style.display = 'block';
        el.classList.add('active');
    }

    function hideElement(el) {
        el.style.display = 'none';
        el.classList.remove('active');
    }

    function showSpinner() {
        spinner.style.display = 'block';
    }

    function hideSpinner() {
        spinner.style.display = 'none';
    }

    function resizeCanvas() {
        if (preview.style.display !== 'none' && preview.naturalWidth && preview.naturalHeight) {
            canvas.width = preview.clientWidth;
            canvas.height = preview.clientHeight;
            canvas.style.width = preview.clientWidth + 'px';
            canvas.style.height = preview.clientHeight + 'px';
        } else {
            hideElement(canvas);
        }
    }

    function drawBoundingBoxes(boxes) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        if (!boxes || boxes.length === 0) {
            hideElement(canvas);
            return;
        }
        showElement(canvas);
        resizeCanvas();

        ctx.strokeStyle = 'red';
        ctx.lineWidth = 3;

        const scaleX = preview.clientWidth / preview.naturalWidth;
        const scaleY = preview.clientHeight / preview.naturalHeight;

        boxes.forEach(box => {
            ctx.strokeRect(
                box.x * scaleX,
                box.y * scaleY,
                box.width * scaleX,
                box.height * scaleY
            );
        });
    }

    function formatConditionName(name) {
        return name.split('_').map(word =>
            word.charAt(0).toUpperCase() + word.slice(1)
        ).join(' ');
    }

    function renderRemedyCardHTML(issue, remedy, remedyIndex, totalRemedies) {
    const directions = Array.isArray(remedy.directions) ? remedy.directions : [remedy.directions];
    const isPrevDisabled = remedyIndex === 0 ? 'disabled' : '';
    const isNextDisabled = remedyIndex === totalRemedies - 1 ? 'disabled' : '';

    return `
        <div class="card herbal-remedy-card">
           
            <div class="card-content-padded">
                <h4 style="color:rgb(34, 116, 45) ; margin-bottom: 0.5rem;">Remedies</h4>
                <h4 style="color:rgb(209, 111, 0); margin-bottom: 0.5rem;">${remedy.title}</h4>
                ${remedy.amount ? `<p><strong>Amount:</strong> ${remedy.amount}</p>` : ''}
                ${directions.length > 0 && directions[0] !== "" ?
                `<div><strong>Directions:</strong></div>
                 <ul class="remedy-steps">
                     ${directions.map(step => `<li>${step}</li>`).join('')}
                 </ul>` : ''}
                
                <div class="remedy-navigation">
                    <button class="herbal-btn herbal-btn-secondary remedy-btn prev-btn" onclick="changeRemedy('${issue}', -1)" ${isPrevDisabled}>&#8592; Previous</button>
                    <span class="remedy-page-info">${remedyIndex + 1} / ${totalRemedies}</span>
                    <button class="herbal-btn herbal-btn-secondary remedy-btn next-btn" onclick="changeRemedy('${issue}', 1)" ${isNextDisabled}>Next &#8594;</button>
                </div>
                 ${remedy.image_url ?
            `<div class="remedy-image-wrapper">
                 <img src="${remedy.image_url}" alt="${remedy.title}" class="remedy-image">
             </div>`
            : '<div class="remedy-image-wrapper remedy-image-placeholder"><div class="remedy-image-placeholder-text">No image available</div></div>'}

            </div>
        </div>
    `;
}

    // --- NEW: Modified renderIssueCardHTML function to include buttons and collapsible content ---
    function renderIssueCardHTML(issue, issueData) {
        const formattedIssueName = formatConditionName(issue);
        const description = issueData.description || 'No description available.';
        const symptoms = issueData.symptoms || 'No symptoms listed.';
        const causes = issueData.causes || 'No causes listed.';

        return `
            <div class="card herbal-issue-card">
                <div class="herbal-card-body">
                    <h3 class="herbal-issue-name">
                        <i class="fas fa-exclamation-triangle"></i> ${formattedIssueName} Details
                    </h3>

                    <div class="herbal-issue-buttons">
                        <button class="herbal-btn herbal-btn-secondary toggle-causes-btn" data-target="causes-${issue}">View Causes</button>
                        <button class="herbal-btn herbal-btn-secondary toggle-symptoms-btn" data-target="symptoms-${issue}">View Symptoms</button>
                    </div>

                    <div id="causes-${issue}" class="herbal-collapsible-content">
                        <h4><i class="fas fa-lightbulb"></i> Causes:</h4>
                        <p>${causes}</p>
                    </div>

                    <div id="symptoms-${issue}" class="herbal-collapsible-content">
                        <h4><i class="fas fa-th-list"></i> Symptoms:</h4>
                        <p>${symptoms}</p>
                    </div>
                </div>
            </div>
        `;
    }

    window.changeRemedy = function (issue, direction) {
        const remedies = latestData.remedies_data[issue]?.remedies;
        if (!remedies || remedies.length === 0) return;

        let currentIndex = remedyState[issue] !== undefined ? remedyState[issue] : 0;
        let newIndex = currentIndex + direction;

        if (newIndex < 0) newIndex = 0;
        if (newIndex >= remedies.length) newIndex = remedies.length - 1;

        remedyState[issue] = newIndex;

        const remedyCardContainer = document.getElementById(`remedy-card-${issue}`);
        if (remedyCardContainer) {
            remedyCardContainer.innerHTML = renderRemedyCardHTML(issue, remedies[newIndex], newIndex, remedies.length);
        }
    };

    function displayResults(data) {
        herbalDetailedRemediesGrid.innerHTML = '';

        // 1. Update the main diagnosis summary card
        // MODIFIED: To show all detected issues WITH their confidence levels in the summary
        let mainPredictedIssueText = 'No specific condition detected';
        if (data.detected_issues && data.detected_issues.length > 0) {
            const issuesWithConfidence = data.detected_issues.map(issue => {
                const formattedName = formatConditionName(issue);
                // Try to get confidence from remedies_data for the specific issue
                const issueConfidence = data.remedies_data && data.remedies_data[issue] && data.remedies_data[issue].confidence
                                        ? (data.remedies_data[issue].confidence * 100).toFixed(0) // Rounded to whole number for summary
                                        : 'N/A';
                return `${formattedName} (${issueConfidence}%)`;
            });
            mainPredictedIssueText = issuesWithConfidence.join(', ');
        }
        diagnosisConditionNameEl.textContent = mainPredictedIssueText;

        // The overall confidence bar remains the same, assuming 'data.confidence' is overall model confidence
        const overallConfidence = data.confidence ? (data.confidence * 100).toFixed(2) : 0;
        diagnosisConfidenceLevelEl.style.width = `${overallConfidence}%`;
        diagnosisConfidenceTextEl.textContent = `Confidence: ${overallConfidence}%`;


        // Handle image and bounding boxes (this part remains the same)
        if (data.annotated_image) {
            preview.src = 'data:image/jpeg;base64,' + data.annotated_image;
            showElement(preview);
            preview.onload = () => {
                if (data.bounding_boxes) {
                    drawBoundingBoxes(data.bounding_boxes);
                } else {
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                    hideElement(canvas);
                }
            };
        } else {
            hideElement(preview);
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            hideElement(canvas);
        }

        // 2. Render detailed issue and remedy cards
        if (!data.detected_issues || data.detected_issues.length === 0) {
            const noResultsMessage = document.createElement('div');
            noResultsMessage.className = 'no-results-message';
            noResultsMessage.textContent = 'No detailed skin conditions or remedies were detected. Please try a clearer image or consult a professional.';
            herbalDetailedRemediesGrid.appendChild(noResultsMessage);
            return;
        }

        for (const issue of data.detected_issues) {
            const issueData = data.remedies_data[issue];

            if (!issueData) {
                console.warn(`No remedy data found for issue: ${issue}`);
                continue;
            }

            const remediesForIssue = issueData.remedies || [];

            const issueRemedyPairContainer = document.createElement('div');
            issueRemedyPairContainer.className = 'issue-remedy-pair'; // Keep this class for layout if needed

            // NEW: Use the updated renderIssueCardHTML
            const issueCardHtml = renderIssueCardHTML(issue, issueData);
            issueRemedyPairContainer.innerHTML += issueCardHtml;

            if (remediesForIssue.length > 0) {
                remedyState[issue] = 0;

                const remedyCardWrapper = document.createElement('div');
                remedyCardWrapper.id = `remedy-card-${issue}`;
                remedyCardWrapper.innerHTML = renderRemedyCardHTML(issue, remediesForIssue[0], 0, remediesForIssue.length);
                issueRemedyPairContainer.appendChild(remedyCardWrapper);
            } else {
                const noRemedyCard = document.createElement('div');
                noRemedyCard.className = 'card herbal-remedy-card';
                noRemedyCard.innerHTML = `
                    <div class="herbal-card-body">
                        <h4 style="color: var(--primary-color);">No Remedies Available</h4>
                        <p>Currently, no specific remedies are listed for ${formatConditionName(issue)}.</p>
                        <div class="remedy-image-placeholder">No image available</div>
                    </div>
                `;
                issueRemedyPairContainer.appendChild(noRemedyCard);
            }

            herbalDetailedRemediesGrid.appendChild(issueRemedyPairContainer);
        }

        // --- NEW: Call this function AFTER all dynamic content is added to the DOM ---
        attachToggleButtonListeners();
    }

    // --- NEW: Function to attach event listeners to dynamically created buttons ---
    function attachToggleButtonListeners() {
        // Remove existing listeners to prevent duplicates if displayResults is called multiple times
        document.querySelectorAll('.toggle-causes-btn, .toggle-symptoms-btn').forEach(button => {
            button.removeEventListener('click', handleToggleButtonClick);
        });

        // Add new listeners
        document.querySelectorAll('.toggle-causes-btn, .toggle-symptoms-btn').forEach(button => {
            button.addEventListener('click', handleToggleButtonClick);
        });
    }

    // --- NEW: Event handler for the toggle buttons ---
    function handleToggleButtonClick(event) {
        const button = event.target;
        const targetId = button.dataset.target;
        const targetContent = document.getElementById(targetId);

        if (targetContent) {
            // Check if the clicked content is currently active
            const isActive = targetContent.classList.contains('active');

            // Find all other active collapsible contents in the same issue card
            // and close them, unless it's the same button clicked again
            const parentIssueCard = button.closest('.herbal-issue-card');
            if (parentIssueCard) {
                parentIssueCard.querySelectorAll('.herbal-collapsible-content.active').forEach(openContent => {
                    if (openContent !== targetContent) {
                        openContent.classList.remove('active');
                        openContent.style.maxHeight = '0';
                        // Reset button text for other buttons
                        const otherButton = parentIssueCard.querySelector(`[data-target="${openContent.id}"]`);
                        if (otherButton) {
                            otherButton.textContent = otherButton.classList.contains('toggle-causes-btn') ? 'View Causes' : 'View Symptoms';
                        }
                    }
                });
            }

            // Now, toggle the clicked content
            if (isActive) {
                targetContent.classList.remove('active');
                targetContent.style.maxHeight = '0';
                button.textContent = button.classList.contains('toggle-causes-btn') ? 'View Causes' : 'View Symptoms';
            } else {
                targetContent.classList.add('active');
                // Set max-height to scrollHeight for proper animation
                targetContent.style.maxHeight = targetContent.scrollHeight + 'px';
                button.textContent = button.classList.contains('toggle-causes-btn') ? 'Hide Causes' : 'Hide Symptoms';
            }
        }
    }


    // Initial load/hide states
    hideElement(video);
    hideElement(canvas);
});