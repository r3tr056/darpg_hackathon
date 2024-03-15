class Chatbox {
    constructor() {
        this.args = {
            openButton: document.querySelector('.chatbox__button'),
            chatBox: document.querySelector('.chat__interface'),
            sendButton: document.querySelector('.send__button')
        }
        this.state = false;
        this.conversation_id = "";
        this.messages = [];
    }

    startConversation() {
        fetch('/chatapi/start-chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        }).then(response => response.json()).then(data => {
            this.conversation_id = data.conversation_id;
        }).catch(error => {
            console.error('Error creating conversation:', error);
        });
    }

    display() {
        const { openButton, chatBox, sendButton } = this.args;
        openButton.addEventListener('click', () => this.toggleState(chatBox))
        sendButton.addEventListener('click', () => this.onSendButton(chatBox))

        const node = chatBox.querySelector('input');
        node.addEventListener('keyup', ({ key }) => {
            if (key === 'Enter') {
                this.onSendButton(chatBox);
            }
        })
    }

    toggleState(chatbox) {
        this.state = !this.state;
        if (this.state) {
            chatbox.classList.add('chatbox--active')
        } else {
            chatbox.classList.remove('chatbox--active')
        }
    }

    onSendButton(chatbox) {
        var textField = chatbox.querySelector('input');
        let text1 = textField.value
        if (text1 === "") {
            return;
        }

        let msg1 = { name: "User", message: text1 }
        this.messages.push(msg1);

        fetch('/chatapi/send-msg', {
            method: 'POST',
            body: JSON.stringify({ content: text1 }),
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json'
            },
        })
            .then(r => r.json())
            .then(r => {
                let msg2 = { name: r.sender, message: r.content };
                this.messages.push(msg2);
                this.updateChatText(chatbox)
                textField.value = ''

            }).catch((error) => {
                console.error('Error:', error);
                this.updateChatText(chatbox)
                textField.value = ''
            });
    }

    updateChatText(chatbox) {
        var html = '';
        this.messages.slice().reverse().forEach(function (item, index) {
            if (item.name === "Bot") {
                html += '<div class="flex items-start justify-start"><img class="w-8 h-8 rounded-full" src="https://img.icons8.com/color/48/000000/circled-user-female-skin-type-5--v1.png" alt="Bot image"><div class="bg-gray-300 text-sm px-3 py-2 rounded-lg mb-2"></div><p>' + item.message + '</p></div></div>'
            }
            else {
                html += '<div class="flex items-end justify-end"><div class="bg-blue-500 text-white text-sm px-3 py-2 rounded-lg mb-2"><p>' + item.message + '</p></div></div>'
            }
        });

        const chatmessage = chatbox.querySelector('.chatbox__messages');
        chatmessage.innerHTML = html;
    }
}

const chatbox = new Chatbox();
chatbox.display();