 // Initialize WOW.js
        new WOW().init();

        document.addEventListener('DOMContentLoaded', () => {
            const faqQuestions = document.querySelectorAll('.faq-question');

            faqQuestions.forEach(question => {
                question.addEventListener('click', () => {
                    const faqItem = question.closest('.faq-item');
                    const answer = faqItem.querySelector('.faq-answer');
                    const isActive = question.classList.contains('active');

                    // Close all other open answers
                    document.querySelectorAll('.faq-question.active').forEach(activeQuestion => {
                        if (activeQuestion !== question) {
                            activeQuestion.classList.remove('active');
                            activeQuestion.closest('.faq-item').querySelector('.faq-answer').style.maxHeight = 0;
                            activeQuestion.closest('.faq-item').querySelector('.faq-answer').style.padding = '0 25px'; // Reset padding
                        }
                    });

                    // Toggle the clicked answer
                    if (isActive) {
                        question.classList.remove('active');
                        answer.style.maxHeight = 0;
                        answer.style.padding = '0 25px'; // Reset padding
                    } else {
                        question.classList.add('active');
                        // Use setTimeout to allow the class change to render before calculating scrollHeight
                        // This helps in some edge cases for smoother animation
                        setTimeout(() => {
                            answer.style.maxHeight = answer.scrollHeight + 'px';
                            answer.style.padding = '0 25px 20px'; // Apply padding when open
                        }, 10); // Small delay
                    }
                });
            });
        });