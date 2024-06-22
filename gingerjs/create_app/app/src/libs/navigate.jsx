import { useCallback } from "react";

const useNavigate = () => {

  const navigate = useCallback((path, { replace = false } = {}) => {
    if (!path) {
      console.error("Navigation path is required");
      return;
    }

    if (typeof path !== "string") {
      console.error("Navigation path must be a string");
      return;
    }

    try {
      // Function to make a GET request
      function getData(url, headers, callback) {
        var xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function () {
          if (xhr.readyState === 4 && xhr.status === 200) {
            callback(xhr.responseText,xhr.responseURL);
          }
        };
        xhr.open("GET", url, true);

        // Set headers
        for (var key in headers) {
          if (headers.hasOwnProperty(key)) {
            xhr.setRequestHeader(key, headers[key]);
          }
        }

        xhr.send();
      }

      // Function to replace HTML with response
      function replaceHTMLWithResponse(response,responseUrl) {
        let parser = new DOMParser();
        let doc = parser.parseFromString(response, "text/html");
        let scriptElement = doc.querySelector(".serverScript");
        if (scriptElement) {
          // Create a new script element
          let newScript = document.createElement("script");
          if (scriptElement.src) {
            // If the script has a src attribute, set it
            newScript.src = scriptElement.src;
            newScript.onload = () => console.log("");
            newScript.onerror = () => console.error("Error while changing route.");
          } else {
            // If the script is inline, copy its content
            newScript.textContent = scriptElement.textContent;
          }
          // Append the script to the current document to execute it
          document.body.appendChild(newScript);
        }
       
        if (replace) {
          window.history.replaceState(null, "", responseUrl);
        } else {
          window.history.pushState(null, "", responseUrl);
        }
        // Dispatch a popstate event to notify the app of the navigation
        window.dispatchEvent(new PopStateEvent("popstate"));
        window.scroll({
          top: 0, 
          left: 0, 
          behavior: 'instant' 
        })
      }

      // Make the GET request and replace HTML
      const headers = {
        // "X-Requested-With":"XMLHttpRequest"
      };
      getData(path, headers, replaceHTMLWithResponse);
    } catch (error) {
      console.error("Error loading content:", error);
    }
  }, []);

  return navigate;
};

export default useNavigate;
