document.addEventListener('DOMContentLoaded', () => {
    const doilookupElement = document.getElementById('doilookup');

    if (doilookupElement) {
        doilookupElement.addEventListener('click', () => {
            lookupFunction();
        });
    console.info("DOI Lookup loaded");
    }
});

function lookupFunction() {
    // Your function code here
    console.log("The lookup function was invoked.");

    // Get the DOI field
    const doiURLField = document.getElementById('id_doi');

    if(doiURLField.value){
            fetchDOI(doiURLField.value);
    }else {
        console.warn("No DOI value");
    }

}

// Function to log successful data to the console
function handleSuccess(data) {



    if(data.works.message.title.length < 0){
        // No titles
        console.warn("No title found");
    }else{
        if(data.works.message.title.length === 1){
            // Exactly one title
            console.info("One title found");
        }
        if(data.works.message.title.length > 1){
            // More than one title
            console.warn("Multiple titles found, only using the first one");
        }
            console.info("The title is: ", data.works.message.title[0]);

    }

    /*
    title[0]
    author[0]
    container-title[0]
    published.date-parts[0=y]
    published.date-parts[1=m]
    published.date-parts[2=d]
    abstract




     */

        payload = {

        // "author":  data.works.message.author[0]['given'] + " " + data.works.message.author[0]['family'],
        "title":  data.works.message.title[0],
                    "journal":  data.works.message['container-title'][0],
        "year":  data.works.message.published['date-parts'][0][0],
        "month":  data.works.message.published['date-parts'][0][1],
        "day":  data.works.message.published['date-parts'][0][2],


        "abstract": data.works.message.abstract,

    }
    console.debug("Success:", data, payload);
    populate(payload)



}


function populate(payload) {

    const titleInput = document.getElementById('id_title');
    // const authorInput = document.getElementById('id_author');
    const yearInput = document.getElementById('id_year');
    const monthInput = document.getElementById('id_month');
    const dayInput = document.getElementById('id_day');
    const journalInput = document.getElementById('id_journal');
    const abstractInput = document.getElementById('id_abstract');

    if(confirm("Populate the following fields?" + JSON.stringify(payload))){
        //do it
        titleInput.value = payload.title;
        // authorInput.value = payload.author;
        yearInput.value = payload.year;
        monthInput.value = payload.month;
        dayInput.value = payload.day;
        journalInput.value = payload.journal;
        abstractInput.innerHTML = payload.abstract;



        alert("Done");
    }

}

// Function to log errors to the console with a warning
function handleError(error) {
    console.warn("Error:", error);
}

// Function to fetch DOI data from the Django view
async function fetchDOI(doi) {
    try {
        // Construct the URL to call the Django view
        const response = await fetch(`/doi/${encodeURIComponent(doi)}`);

        // Check if the response was successful (HTTP status 200-299)
        if (response.ok) {
            const data = await response.json();
            handleSuccess(data);
        } else {
            // If the response was not successful, throw an error with the status text
            const errorData = await response.json();
            throw new Error(errorData.error || response.statusText);
        }
    } catch (error) {
        handleError(error.message);
    }
}
