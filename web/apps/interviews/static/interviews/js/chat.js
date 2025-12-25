document.addEventListener("DOMContentLoaded", () => {
    const messages = document.getElementById("messages");
    if (messages) {
        messages.scrollTop = messages.scrollHeight;
    }
});
