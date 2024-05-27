let slides = document.querySelectorAll('.slide');
let dots = document.querySelectorAll('.dot');
let currentIndex = 0; // Starting index

function showSlides(index) {
    // First make all slides transparent and remove 'active' class from dots
    slides.forEach((slide, ind) => {
        slide.style.opacity = '0';
        dots[ind].classList.replace('bg-gray-800', 'bg-white');
    });

    // Make the current slide visible
    slides[index].style.opacity = '1';
    dots[index].classList.replace('bg-white', 'bg-gray-800');
}

    
function currentSlide(index) {
    showSlides(index);
    currentIndex = index;
    resetInterval();
}

function nextSlide() {
    currentIndex++;

    if (currentIndex >= slides.length) {
        currentIndex = 0
    };

    if (currentIndex < 0) currentIndex = slides.length - 1;
        
    showSlides(currentIndex);
    console.log(currentIndex);
}

// Reset the interval
function resetInterval() {
    clearInterval(slideInterval);
    slideInterval = setInterval(nextSlide, 5000);
}

// Automatic slideshow
let slideInterval = setInterval(nextSlide, 5000);


// Your existing window.onload code
dots.forEach((dot, index) => {
    dot.addEventListener('click', () => {
        currentSlide(index)
    });
});

showSlides(currentIndex); // Initialize the slider


// Optional: Preload images if you have a large set of images
window.onload = () => {
    for (let i = 0; i < slides.length; i++) {
        const img = new Image();
        img.src = slides[i].getElementsByTagName('img')[0].src;
    }
};