async function copyText(site, email) {
    const baseUrl = "http://127.0.0.1:5000";
    const endpoint = "/send";
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
    // const response = await fetch(urlToFetch);
    // console.log("response");
}


