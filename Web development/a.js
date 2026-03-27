const button = document.getElementById("magicBtn");
const message = document.getElementById("message");

button.addEventListener("click", () => {
    const colors = ["#ff6b6b", "#ff9f1a", "#2ec4b6", "#e71d36", "#9b5de5"];
    const randomColor = colors[Math.floor(Math.random()* colors.length)];
   
    message.textContent = "Сіз кнопканы бастыңыз! 🎉";
    message.style.color = randomColor;
    message.style.fontSize = "2rem";
    message.style.transition = "all 0.5s ease";
});
 registerForm.addEventListener("submit", (e) => {
            e.preventDefault();
            const name = document.getElementById("name").value;
            const email = document.getElementById("emailReg").value;
            const password = document.getElementById("passwordReg").value;

            if(localStorage.getItem(email)){
                message.textContent = "Бұл email бұрын тіркелген ❌";
                message.style.color = "#ff6b6b";
                return;
            }

            const user = { name, email, password };
            localStorage.setItem(email, JSON.stringify(user));

            message.textContent = "Сіз сәтті тіркелдіңіз! 🎉";
            message.style.color = "#2ec4b6";

            registerForm.reset();
        });


        loginForm.addEventListener("submit", (e) => {
            e.preventDefault();
            const email = document.getElementById("email").value;
            const password = document.getElementById("password").value;

            const storedUser = localStorage.getItem(email);

            if(storedUser){
                const user = JSON.parse(storedUser);
                if(user.password === password){
                    message.textContent = `Кіру сәтті өтті! Қош келдіңіз, ${user.name} 🎉`;
                    message.style.color = "#2ec4b6";
                } else {
                    message.textContent = "Пароль дұрыс емес ❌";
                    message.style.color = "#ff6b6b";
                }
            } else {
                message.textContent = "Email табылмады ❌";
                message.style.color = "#ff6b6b";
            }
        });