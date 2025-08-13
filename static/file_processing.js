async function load_file_list() {
    const recursiveSubDirs = document.getElementById('recursive_sub_dirs');
    const params = new URLSearchParams({recursive_sub_dirs: recursiveSubDirs.checked});

    const response = await fetch(`/process-files-list?${params}`);
    const data = await response.json();
    if (data.error) {
        const errorTextAdd = document.getElementById('errorText');
        errorTextAdd.innerHTML = data.error;
    } else {
        const processFilesTableIn = document.getElementById('process_files_table_in');
        const processFilesTableOut = document.getElementById('process_files_table_out');
        const directoryIn = document.getElementById('directory_in');
        const directoryOut = document.getElementById('directory_out');

        processFilesTableIn.innerHTML = "";
        processFilesTableOut.innerHTML = "";

        for (const fileItem of data.files_in) {
            let file_class;
            if (fileItem.file_error) {
                file_class = "text-error";
            } else if (fileItem.file_processor) {
                file_class = "text-primary text-bold";
            } else {
                file_class = "";
            }

            const file_processor = fileItem.file_processor ? fileItem.file_processor : "Not found";
            processFilesTableIn.innerHTML += "<tr><td><span class='" + file_class + "'>" + fileItem.file_with_path
                + "</span></td><td>" + file_processor + "</td></tr>"
        }
        for (const fileItem of data.files_out) {
            processFilesTableOut.innerHTML += "<tr><td><span>" + fileItem.file_with_path + "</span></td></tr>"
        }
        directoryIn.innerHTML = data.directory_in;
        directoryOut.innerHTML = data.directory_out;
    }

    return "";
}

async function process_files() {
    const elProgress = document.getElementById('progress');
    const submit = document.getElementById('submit');
    const errorText = document.getElementById('errorText');
    submit.disabled = true;
    elProgress.style.display = 'inline';

    const preserve_original_text = document.getElementById('preserve_original_text').checked;
    const overwrite_processed_files = document.getElementById('overwrite_processed_files').checked;
    const recursiveSubDirs = document.getElementById('recursive_sub_dirs').checked;
    const fromLang = document.getElementById('from_lang_select').value;
    const toLang = document.getElementById('to_lang_select').value;
    const plugin = document.getElementById('plugin').value;

    const reqBody = JSON.stringify({
        from_lang: fromLang, to_lang: toLang, translator_plugin: plugin,
        preserve_original_text: preserve_original_text, overwrite_processed_files: overwrite_processed_files,
        recursive_sub_dirs: recursiveSubDirs, file_processors: null
    });
    const reqParam = {
        method: 'POST',
        body: reqBody,
        signal: AbortSignal.timeout(600000),
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
    }
    try {
        const response = await fetch(`/process-files`, reqParam);
        const data = await response.json();
        if (data.error) {
            errorText.innerHTML = data.error;
            return "";
        } else {
            const processFilesTableResult = document.getElementById('process_files_table_result');
            processFilesTableResult.innerHTML = "";
            for (const fileItem of data.files) {
                let file_class = "";
                if (fileItem.status === 'ERROR') {
                    file_class = "text-error";
                } else if (fileItem.status === 'OK') {
                    file_class = "text-primary text-bold";
                } else {
                    file_class = "";
                }

                let status = fileItem.status;
                switch (fileItem.status) {
                    case "ERROR":
                        status = "Error";
                        break;
                    case "TYPE_NOT_SUPPORT":
                        status = "Type not support";
                        break;
                    case "TRANSLATE_ALREADY_EXISTS":
                        status = "Translate already exists"
                }

                const pathFileOut = fileItem.path_file_out ? fileItem.path_file_out : "";

                processFilesTableResult.innerHTML += "<tr><td><span class='" + file_class + "'>" + fileItem.path_file_in
                    + "</span></td><td>" + pathFileOut + "</td><td>" + status + "</td></tr>"
            }

            return "";
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
    const recursiveSubDirs = document.getElementById('recursive_sub_dirs');
    recursiveSubDirs.onchange = () => {
        load_file_list();
    }
    const submit = document.getElementById('submit');
    submit.onmouseup = () => {
        process_files();
        load_file_list();
    };

    fill_language_select_elements();

    load_file_list();
}

