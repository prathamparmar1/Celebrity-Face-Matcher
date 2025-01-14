document.getElementById('uploadButton').addEventListener('click', function () {
    var fileInput = document.getElementById('fileInput');
    var loadingSpinner = document.getElementById('loadingSpinner');
    var resultContainer = document.getElementById('resultContainer');
    var imagesContainer = document.getElementById('imagesContainer');

    if (fileInput.files.length === 0) {
        alert('Please select an image file first.');
        return;
    }

    var formData = new FormData();
    formData.append('file', fileInput.files[0]);

    // Show loading spinner
    loadingSpinner.style.display = 'block';
    resultContainer.style.display = 'none';
    imagesContainer.innerHTML = '';  // Clear previous images

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            loadingSpinner.style.display = 'none';  // Hide loading spinner
            resultContainer.style.display = 'block';

            if (data.error) {
                document.getElementById('result').innerText = data.error;
            } else {
                // Display the matched celebrity name
                document.getElementById('result').innerText = "You match with: " + data.match;

                // Display the additional images
                if (data.additional_images.length > 0) {
                    data.additional_images.forEach(function (imageName) {
                        var img = document.createElement('img');
                        img.src = '/celebrity_dataset/' + imageName;
                        img.alt = data.match;
                        img.style.width = '150px';  // Adjust image size as needed
                        imagesContainer.appendChild(img);
                    });
                } else {
                    document.getElementById('result').innerText += " No additional images found.";
                }
            }
        })
        .catch(error => {
            loadingSpinner.style.display = 'none';  // Hide loading spinner
            console.error('Error:', error);
        });
});
