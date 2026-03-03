// --- Government Login Logic ---
document.getElementById('gov-login-form').addEventListener('submit', function(e) {
    e.preventDefault();
    alert("Authentication Successful. Redirecting to Command Center...");
    window.location.href = 'index.html';
});


// --- SOS FORM ---
document.getElementById('sos-form').addEventListener('submit', async function(e) {

    e.preventDefault();

    console.log("🚨 SOS BUTTON CLICKED! Attempting to send...");

    const location = document.getElementById('sos-location').value;
    const message = document.getElementById('sos-message').value;
    const statusBox = document.getElementById('sos-status-box');
    const submitBtn = e.target.querySelector('button[type="submit"]');

    submitBtn.disabled = true;
    submitBtn.innerText = "TRANSMITTING...";

    statusBox.classList.remove('hidden');
    statusBox.style.background = "#1e293b";
    statusBox.style.color = "#cbd5e1";
    statusBox.innerText = "Connecting to Command Center...";

    try {

        const response = await fetch('http://localhost:8000/api/send-sos', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                location: location,
                message: message
            })
        });

        if (!response.ok) {
            throw new Error(`Server responded with status: ${response.status}`);
        }

        const data = await response.json();

        console.log("Server Response:", data);

        // ✅ SAFE CHECK
        if (data.status === "success" && data.analysis) {

            statusBox.style.background = "rgba(16, 185, 129, 0.2)";
            statusBox.style.color = "#10b981";

            statusBox.innerHTML =
                "<b>SOS RECEIVED</b><br><br>" +
                "Priority: " + (data.analysis.priority || "N/A") + "<br>" +
                "Action: " + (data.analysis.recommended_action || "Awaiting command...");

            submitBtn.innerText = "SIGNAL ACTIVE";

        } else {

            // Backend returned error safely
            statusBox.style.background = "rgba(239, 68, 68, 0.2)";
            statusBox.style.color = "#ef4444";

            statusBox.innerText =
                data.message || "Analysis failed. Try again.";

            submitBtn.disabled = false;
            submitBtn.innerText = "RETRY SOS";
        }

    } catch (error) {

        console.error("🔥 FETCH ERROR:", error);

        statusBox.style.background = "rgba(239, 68, 68, 0.2)";
        statusBox.style.color = "#ef4444";
        statusBox.innerText = "CONNECTION FAILED. Try SMS or Radio.";

        submitBtn.disabled = false;
        submitBtn.innerText = "RETRY SOS";
    }

});