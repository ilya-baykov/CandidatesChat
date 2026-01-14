document.addEventListener("DOMContentLoaded", () => {
    // скролл чата (оставляем)
    const messages = document.getElementById("messages");
    if (messages) {
        messages.scrollTop = messages.scrollHeight;
    }

    // ищем форму
    const form = document.querySelector(".chat-input");
    if (!form) {
        console.log("Форма .chat-input не найдена на странице");
        return;
    }

    const btn = form.querySelector('button[type="submit"]');
    const textarea = form.querySelector('textarea');

    if (!btn) {
        console.log("Кнопка внутри .chat-input не найдена");
        return;
    }

    console.log("Кнопка найдена, слушатель добавлен");

    form.addEventListener("submit", () => {
        console.log("Форма отправляется → отключаем кнопку");
        btn.disabled = true;
        btn.classList.add("sending");
//        if (textarea) textarea.disabled = true;
    });
});