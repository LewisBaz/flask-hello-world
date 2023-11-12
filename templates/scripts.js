const API_URL = 'https://flask-hello-world-hazel-omega.vercel.app/';

document.addEventListener('DOMContentLoaded', function() {
    const buttons = document.getElementsByClassName('button-login');
    const loginField = document.getElementsByClassName('login')[0];
    const passwordField = document.getElementsByClassName('password')[0];

    passwordField.addEventListener('click', function() {
      passwordField.innerHTML = '';
    });

    loginField.addEventListener('click', function() {
      loginField.innerHTML = ''
    })

    if (buttons) {
        buttons[0].addEventListener('click', function() {
            const data = {
                login: loginField.innerText,
                password: passwordField.innerText
            };
            console.log(data.login, data.password)
            const body = JSON.stringify({
              login: data.login,
              password: data.password
            })
            fetch(`${API_URL}login`, {
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
                if (data.success) {
                  console.log('success routing');
                  window.location.href = `templates/main.html?name=${data['data']['name']}&mins=${data['data']['calm_mins']}&user_id=${data['data']['userId']}&last_mood=${data['data']['last_mood']}`;
                } else {
                  console.log('error routing');
                }
              })
              .catch(error => console.error(error));
        });
    }
});