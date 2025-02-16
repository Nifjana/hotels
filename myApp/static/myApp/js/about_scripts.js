document.addEventListener("DOMContentLoaded", function () {
    const divs = document.querySelectorAll('.gif-container > div');

    divs.forEach(div => {
        div.addEventListener('mouseenter', () => {
            div.style.transform = 'scale(1.2)';
            div.style.transition = 'transform 0.3s ease';

            // Hide other divs
            divs.forEach(otherDiv => {
                if (otherDiv !== div) {
                    otherDiv.style.opacity = '0';
                    otherDiv.style.transition = 'opacity 0.3s ease';
                }
            });
        });

        div.addEventListener('mouseleave', () => {
            div.style.transform = 'scale(1)';

            // Show all divs again
            divs.forEach(otherDiv => {
                otherDiv.style.opacity = '1';
            });
        });
    });
});
