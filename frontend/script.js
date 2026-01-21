const sendBtn = document.getElementById('send-btn');
const userInput = document.getElementById('user-input');
const chatWindow = document.getElementById('chat-window');
const loader = document.getElementById('loading-container');
const deptSelect = document.getElementById('dept-select');

async function sendMessage() {
    const query = userInput.value.trim();
    const dept = deptSelect.value;
    const role = "admin"; // Change this to test your security logic

    if (!query) return;

    // Show User Message
    chatWindow.innerHTML += `<div class="user-msg bubble">${query}</div>`;
    userInput.value = '';
    
    // START THE SPINNING LINE
    loader.classList.remove('hidden');
    chatWindow.scrollTop = chatWindow.scrollHeight;

    try {
        // Fetch from your FastAPI Backend
        const response = await fetch(`http://127.0.0.1:8000/ask?role=${role}&dept=${dept}&query=${encodeURIComponent(query)}`);
        const data = await response.json();

        // HIDE THE SPINNING LINE
        loader.classList.add('hidden');

        // Show AI Response (Supporting Markdown style)
        const formattedAnswer = data.answer.replace(/\n/g, '<br>');
        chatWindow.innerHTML += `<div class="bot-msg bubble">${formattedAnswer}</div>`;
        
    } catch (error) {
        loader.classList.add('hidden');
        chatWindow.innerHTML += `<div class="bot-msg bubble" style="color: red;">⚠️ Connection Error: Is main.py running on port 8000?</div>`;
    }
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') sendMessage(); });