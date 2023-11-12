const API_URL = 'https://flask-hello-world-hazel-omega.vercel.app/';

document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const name = urlParams.get('name');
    const mins = urlParams.get('mins');
    const lastMood = urlParams.get('last_mood');
    setLastMoodInitially(lastMood)
    document.getElementsByClassName('head')[0].innerText = `Hello, ${name}`;
    document.getElementsByClassName('text-2')[0].innerText = `${mins} minutes`

    const adviceField = document.getElementsByClassName('text-advice')[0];
    const container = document.getElementsByClassName('typography-2')[0];
  
    fetch(`${API_URL}advice`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
    })
    .then(response => response.json())
    .then(data => {
      console.log(data);
      adviceField.innerText = data['data'];
      adviceField.style.height = 'auto';
      let res = adviceField.offsetHeight + 40 + 'px'
      container.style.height = res;
      console.log(res);
    })
    .catch(error => console.error(error));
  })

const handleIconClick = (event) => {
    const activeTab = document.body.querySelector(`.icon-3-selected`);
    const currentTab = event.currentTarget;
  
    console.log(currentTab)
    console.log(activeTab)

    const currentCirce = currentTab.parentNode;

    const spanElement = currentCirce.nextSibling.nextSibling;
    const tag = spanElement.innerText
    console.log(tag)

    if (activeTab) {
        const activeCircle = activeTab.parentNode;
        if (activeTab === currentTab) {
            activeCircle.classList.remove('circle-selected')
            currentTab.classList.remove('icon-3-selected');
            currentTab.classList.add('icon-3');
            sendRequest(0)
        } else {
            activeCircle.classList.remove('circle-selected')
            activeTab.classList.remove('icon-3-selected');
            currentTab.classList.remove('icon-3');
            currentTab.classList.add('icon-3-selected');
            currentCirce.classList.add('circle-selected')
            sendRequest(tag)
        }
    } else {
        currentTab.classList.remove('icon-3');
        currentTab.classList.add('icon-3-selected');
        currentCirce.classList.add('circle-selected');
        sendRequest(tag)
    }
  };

function sendRequest(mood) {
    const urlParams = new URLSearchParams(window.location.search);
    const user_id = urlParams.get('user_id');
    const body = JSON.stringify({
        user_id: user_id,
        mood: mood
      })
      fetch(`${API_URL}saveMood`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
          },
          body: body
        })
        .then(console.log(body))
        .then(response => response.json())
        .then(data => {
          console.log(data);
        })
        .catch(error => console.error(error));
}

function setLastMoodInitially(mood) {
    const spans = document.getElementsByClassName('integer');
    for (let i = 0; i < spans.length; i++) {
        if (spans[i].innerText == mood) {
            console.log(mood);
            const circle = spans[i].previousElementSibling
            circle.classList.add('circle-selected')
            circle.firstElementChild.classList.add('icon-3-selected');
        }
    }
}