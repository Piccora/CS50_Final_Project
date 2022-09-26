async function copyText(site, email) {
    const baseUrl = "http://127.0.0.1:5000";
    const endpoint = "/get-password";
    const urlToFetch = `${baseUrl}${endpoint}`;
    const data = JSON.stringify({ site: site, email: email })
    try {
        const response = await fetch(urlToFetch, {
            method: "POST", body: data, headers: {
                'Content-type': 'application/json',
            }
        });
        if (response.ok) {
            const jsonResponse = await response.json();
            console.log(jsonResponse)
            navigator.clipboard.writeText(jsonResponse["password"])
            console.log("success")
        }
    } catch (error) {
        console.log(error);
    }
}

async function getEmail() {
    var select = document.getElementById("list_sites");
    var option = select.options[select.selectedIndex];
    var length = document.getElementById("list_emails").length - 1;
    for (let i = length; i >= 0; i--) {
        document.getElementById("list_emails").remove(i)
    }
    if (option.value === "initial_value") {
        document.getElementById("list_emails").disabled = true
    } else {
        const urlToFetch = "http://127.0.0.1:5000/get-email"
        const data = JSON.stringify({ site: option.value })
        try {
            const response = await fetch(urlToFetch, {
                method: "POST", body: data, headers: {
                    'Content-type': 'application/json',
                }
            });
            if (response.ok) {
                const jsonResponse = await response.json();
                console.log(jsonResponse)
                for (let i = 0; i < jsonResponse["email"].length; i++) {
                    var opt = document.createElement("option");
                    opt.value = jsonResponse["email"][i];
                    opt.innerHTML = jsonResponse["email"][i];
                    document.getElementById("list_emails").add(opt);

                }
                document.getElementById("list_emails").disabled = false;
            }

        } catch (error) {
            console.log(error)
        }
    }
}

async function delete_password() {
    var select_site = document.getElementById("list_sites");
    var option_site = select_site.options[select_site.selectedIndex];
    var select_email = document.getElementById("list_emails");
    var option_email = select_email.options[select_email.selectedIndex];
    const baseUrl = "http://127.0.0.1:5000";
    const endpoint = "/delete-password";
    const urlToFetch = `${baseUrl}${endpoint}`;
    const data = JSON.stringify({ site: option_site.value, email: option_email.value })
    try {
        const response = await fetch(urlToFetch, {
            method: "POST", body: data, headers: {
                'Content-type': 'application/json',
            }
        });
        if (response.ok) {
            window.location.replace(`${baseUrl}/`);
        }
    } catch (error) {
        console.log(error)
    }
}

async function change_password() {
    var select_site = document.getElementById("list_sites");
    var option_site = select_site.options[select_site.selectedIndex];
    var select_email = document.getElementById("list_emails");
    var option_email = select_email.options[select_email.selectedIndex];
    var new_password = document.getElementById("new_password")
    const baseUrl = "http://127.0.0.1:5000";
    const endpoint = "/change-password";
    const urlToFetch = `${baseUrl}${endpoint}`;
    const data = JSON.stringify({ site: option_site.value, email: option_email.value, password: new_password.value })
    try {
        const response = await fetch(urlToFetch, {
            method: "POST", body: data, headers: {
                'Content-type': 'application/json',
            }
        });
        if (response.ok) {
            window.location.replace(`${baseUrl}/`)
        }
    } catch (error) {
        console.log(error)
    }
}

function button_check_delete() {
    var select_site = document.getElementById("list_sites");
    var option_site = select_site.options[select_site.selectedIndex];
    if (option_site.value !== "initial_value") {
        document.getElementById("delete_password_btn_delete").disabled = false;
    } else {
        document.getElementById("delete_password_btn_delete").disabled = true;
    }
}

function button_check_change() {
    var select_site = document.getElementById("list_sites");
    var option_site = select_site.options[select_site.selectedIndex];
    var new_password = document.getElementById("new_password").value.trim();
    var confirm_password = document.getElementById("confirm_password").value.trim();
    if (option_site.value !== "initial_value" && new_password === confirm_password) {
        document.getElementById("delete_password_btn_change").disabled = false;
    } else {
        document.getElementById("delete_password_btn_change").disabled = true;
    }

}
