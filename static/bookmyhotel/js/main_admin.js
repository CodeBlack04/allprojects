console.log('it works')

/* Variables */
const chatRoomId = document.querySelector('#room_id').textContent.replaceAll('"','')
const chatUserName = document.querySelector('#user_name').textContent.replaceAll('"','')
const chatUserId = document.querySelector('#user_id').textContent.replaceAll('"','')

console.log('UserName:', chatUserName)
console.log('UserId:', chatUserId)

let chatSocket = null


/* Elements */
const chatLogElement = document.querySelector('#chat_log')
const chatInputElement = document.querySelector('#chat_message_input')
const chatSubmitElement = document.querySelector('#chat_message_submit')


/* Websocket build */
chatSocket = new WebSocket(`ws://${window.location.host}/ws/${chatRoomId}/`)

chatSocket.onopen = (e) => {
    console.log('onOpen - websocket was opened')

    scrollToBottom()
}

chatSocket.onclose = (e) => {
    console.log('onClose - websocket was closed')
}

chatSocket.onmessage = (e) => {
    console.log('onMessage')

    onChatMessage(JSON.parse(e.data))
}


/* Functions */
const scrollToBottom = () => {
    chatLogElement.scrollTop = chatLogElement.scrollHeight
}


const sendMessage = () => {
    chatSocket.send(JSON.stringify({
        'type': 'message',
        'message': chatInputElement.value,
        'name': chatUserName,
        'agent': chatUserId
    }))

    chatInputElement.value = ''
}


const onChatMessage = (data) => {
    console.log('onChatMessage', data)

    if (data.type == 'chat_message') {
        
        let tempLogElement = document.querySelector('.temp-log')

        if (tempLogElement) {
            tempLogElement.remove()
        }

        if (!data.client) {
            chatLogElement.innerHTML += `
                <div class="flex w-full mt-2 space-x-3 max-w-md ml-auto justify-end">
                    <div>
                        <div class="bg-blue-700 p-3 rounded-l-lg rounded-br-2xl">
                            <p class="text-sm whitespace-normal break-words">${data.message}</p>
                        </div>
                
                        <span class="text-xs text-gray-200 leading-none">${data.created_at} ago</span>
                    </div>

                    <div class="flex-shrink-0 h-10 w-10 rounded-full bg-blue-700 text-center pt-2">${data.initials}</div>
                </div>
            `
        } else {
            chatLogElement.innerHTML += `
                <div class="flex w-full mt-2 space-x-3 max-w-md">

                    <div class="flex-shrink-0 h-10 w-10 rounded-full bg-gray-800 text-center pt-2">${data.initials}</div>

                    <div>
                        <div class="bg-gray-800 p-3 rounded-bl-2xl rounded-r-lg">
                            <p class="text-sm whitespace-normal break-words">${data.message}</p>
                        </div>
                        
                        <span class="text-xs text-gray-200 leading-none">${data.created_at} ago</span>
                    </div>
                </div>
            `
        }
    } else if (data.type == 'add_writing_status') {
        if (data.client) {
            chatLogElement.innerHTML += `
                <div class="temp-log flex w-full mt-2 space-x-3 max-w-md">

                    <div class="flex-shrink-0 h-10 w-10 rounded-full bg-gray-800 text-center pt-2">${data.initials}</div>

                    <div>
                        <div class="bg-gray-800 p-3 rounded-bl-2xl rounded-r-lg">
                            <p class="text-sm whitespace-normal break-words">${data.message}</p>
                        </div>
                    </div>

                </div>
            `
        }
    } else if (data.type == 'remove_writing_status') {
        
        let tempLogElement = document.querySelector('.temp-log')

        if (tempLogElement) {
            tempLogElement.remove()
        }
    }

    scrollToBottom()
}


/* Event listeners */
chatSubmitElement.onclick = (e) => {
    e.preventDefault()

    sendMessage()

    return false
}

chatInputElement.onkeyup = (e) => {
    if (e.keyCode == 13) {
        sendMessage()
    }
}

chatInputElement.onfocus = (e) => {
    chatSocket.send(JSON.stringify({
        'type': 'writing_on',
        'message': 'Typing...',
        'name': chatUserName,
        'agent': chatUserId,
    }))
}

chatInputElement.onblur = (e) => {
    chatSocket.send(JSON.stringify({
        'type': 'writing_off',
    }))
}