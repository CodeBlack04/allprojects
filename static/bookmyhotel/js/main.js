console.log('it works!')
/* Variables */
let chatSocket = null
let chatWindowUrl = window.location.href
let chatRoomId = Math.random().toString(36).slice(2,12)

/* Getting User info from frontend */
const chatUserNameElement = document.querySelector('#user_name')
const chatUserIdElement = document.querySelector('#user_id')

let chatUserName = chatUserNameElement ? chatUserNameElement.textContent.replaceAll('"', '') : null
let chatUserId = chatUserIdElement ? chatUserIdElement.textContent.replaceAll('"', '') : null

console.log('UserName:', chatUserName)
console.log('UserId:', chatUserId)

/* Elements */
const chatIconElement = document.querySelector('#chat_icon')
const chatRoomElement = document.querySelector('#chat_room')
const chatLogElement = document.querySelector('#chat_log')

/* Inputs */
const chatMessageInput = document.querySelector('#chat_message_input')

/* Buttons */
const chatMessageSend = document.querySelector('#chat_message_submit')



/* Functions */
const scrollToBottom = () => {
    chatLogElement.scrollTop = chatLogElement.scrollHeight
}


const joinChatRoom = async () => {
    console.log('Creating chat room')

    if ( chatUserName && chatUserId ) {
        chatIconElement.classList.add('hidden')
        chatRoomElement.classList.remove('hidden')

        const data = new FormData()
        data.append('url', chatWindowUrl)

        await fetch(`/bookmyhotel/create-room/${chatRoomId}/`, {
            method: 'POST',
            body: data
        })
        .then((res) => {
            return res.json()
        })
        .then((data) => {
            console.log('data', data)
        })

        chatSocket = new WebSocket(`ws://${window.location.host}/ws/${chatRoomId}/`)

        chatSocket.onopen = (e) => {
            console.log('onOpen - Websocket was opened')
        }

        chatSocket.onclose = (e) => {
            console.log('onClode - Websocket was closed')
        }

        chatSocket.onmessage = (e) => {
            console.log('onMessage')

            onChatMessage(JSON.parse(e.data))
        }
    } else {
        window.location.href = '/login/'
    }

    scrollToBottom()
}


const sendMessage = async () => {

    chatSocket.send(JSON.stringify({
        'type': 'message',
        'message': chatMessageInput.value,
        'name': chatUserName,
        'client': chatUserId
    }))

    chatMessageInput.value = ''
}


const onChatMessage = async (data) => {
    console.log('onChatMessage', data)

    if (data.type == 'chat_message') {

        let tempLogElement = document.querySelector('.temp-log')
        
        if (tempLogElement) {
            tempLogElement.remove()
        }

        if (data.client) {
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
    } else if (data.type == 'inform_client') {

        chatLogElement.innerHTML += `<p class='mt-2 mb-2'>An agent has joined the chat</p>`

    } else if (data.type == 'add_writing_status') {

        if (data.agent) {
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
chatIconElement.onclick = (e) => {
    e.preventDefault()

    joinChatRoom()

    return false
}

chatMessageSend.onclick = (e) => {
    e.preventDefault()

    sendMessage()

    return false
}

chatMessageInput.onkeyup = (e) => {
    if (e.keyCode == 13) {
        sendMessage()
    }
}

chatMessageInput.onfocus = (e) => {
    chatSocket.send(JSON.stringify({    
        'type': 'writing_on',
        'message': 'typing...',
        'name': chatUserName,
        'client': chatUserId,
    }))
}

chatMessageInput.onblur = (e) => {
    chatSocket.send(JSON.stringify({
        'type': 'writing_off'
    }))
}
