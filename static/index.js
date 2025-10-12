async function translateText() {
    const elProgress = document.getElementById('progress');
    const elResult = document.getElementById('text_result');
    const submit = document.getElementById('submit');
    const errorText = document.getElementById('errorText');
    submit.disabled = true;
    elProgress.style.display = 'inline';
    elResult.value = '';

    const text = document.getElementById('text').value;
    const fromLang = document.getElementById('from_lang_select').value;
    const toLang = document.getElementById('to_lang_select').value;
    const plugin = document.getElementById('plugin').value;

    errorText.innerHTML = ""

    try {
        const reqBody = JSON.stringify({
            text: text, from_lang: fromLang, to_lang: toLang,
            translator_plugin: plugin
        });
        const reqParam = {
            method: 'POST',
            body: reqBody,
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            }
        }
        const response = await fetch(`/translate`, reqParam);
        const data = await response.json();
        if (data.error) {
            errorText.innerHTML = data.error;
            return "";
        } else {
            const translation = data.result;
            elResult.value = translation;

            errorText.innerHTML = ""
            return translation;
        }
    } catch (error) {
        errorText.innerHTML = error.message;
        console.error(error.message);
    } finally {
        elProgress.style.display = 'none';
        submit.disabled = false;
    }
}


window.onload = () => {
    const submit = document.getElementById('submit');
    submit.onmouseup = () => {
        translateText();
    };

    fill_language_select_elements();
}