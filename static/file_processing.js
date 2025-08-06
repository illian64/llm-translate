async function load_file_list() {
    const processFilesTableIn = document.getElementById('process_files_table_in');
    const processFilesTableOut = document.getElementById('process_files_table_out');
    const response = await fetch(`/process-files-list`);
    const data = await response.json();
    if (data.error) {
        const errorTextAdd = document.getElementById('errorText');
        errorTextAdd.innerHTML = data.error;
    } else {
        for (const fileItem of data.files_in) {
            let file_class;
            if (fileItem.file_error) {
                file_class = "text-error";
            } else if (fileItem.file_processor) {
                file_class = "text-primary";
            } else {
                file_class = "";
            }

            const file_processor = fileItem.file_processor ? fileItem.file_processor : "Not found";
            processFilesTableIn.innerHTML += "<tr><td><span class='" + file_class + "'>" + fileItem.file
                + "</span></td><td>" + file_processor + "</td></tr>"
        }
        for (const fileItem of data.files_out) {
            processFilesTableOut.innerHTML += "<tr><td>" + fileItem.file + "</td></tr>"
        }
    }

    return "";
}

window.onload = () => {
    // const translate = document.getElementById('translate');
    // translate.onmouseup = () => {
    //     translateText();
    // };

    fill_language_select_elements();

    fetch_data(load_file_list);
}

