import os
import traceback
from flask import render_template_string
from werkzeug.exceptions import BadRequest,InternalServerError

exception_template = """
{% extends "layout.html" %}

{% block title %}Exception{% endblock %}

{% block content %}
<div style="display:flex;align-items:center;justify-content:center;min-height:100vh">
    <div style="max-width: 28rem; width: 100%; padding-left: 1.5rem; padding-right: 1.5rem; padding-top: 3rem; padding-bottom: 3rem; border-radius: 0.5rem;">
        <div style="text-align:center">
            <h1 style="font-size: 1.875rem; line-height: 2.25rem; font-weight: 700;">{{name|safe}}</h1>
            <p style="color: #4B5563; margin-top: 0.5rem; text-align: center;">
                {{msg|safe}}
            </p>
        </div>
    </div>
</div>
{% endblock %}

"""
exception_template_debug = """
{% extends "layout.html" %}

{% block title %}Exception{% endblock %}

{% block content %}
<div style="display:flex;align-items:center;justify-content:center;min-height:100vh;z-index:50;position:fixed;">
    <div class="bg-white rounded-md shadow-lg p-8 max-w-screen-2xl w-full">
        <h2 class="text-lg font-semibold mb-2 text-red-600">Exception: {{name|safe}}</h2>
        <p class="mb-4 text-gray-800">{{msg|safe}}</p>
        <pre class="bg-red-100 p-4 rounded overflow-x-auto text-red-700">{{stack|safe}}</pre>
    </div>
</div>
{% endblock %}

"""
bad_request_exception_template = """
{% extends "layout.html" %}

{% block title %}Bad Request{% endblock %}

{% block content %}
<div style="display:flex;align-items:center;justify-content:center;min-height:100vh">
    <div style="max-width: 28rem; width: 100%; padding-left: 1.5rem; padding-right: 1.5rem; padding-top: 3rem; padding-bottom: 3rem; border-radius: 0.5rem;">
    <div style="display:flex;align-items:center;justify-content:center;flex-direction:column">
        <h1 style="font-size: 8rem;line-height: 1;color: rgb(17 24 39);margin:0" class="font-bold text-gray-900 dark:text-gray-50">400</h1>
        <h1 style="font-size: 1.875rem; line-height: 2.25rem; font-weight: 700; margin-top: 1rem;">Bad Request</h1>
        <p style="color: #4B5563; margin-top: 0.5rem; text-align: center;">
            oops, it looks like you've encountered a 400 Bad Request error. This means the server couldn't understand the
          request you sent.
        </p>
    </div>
    </div>
</div>
{% endblock %}

"""

internal_server_exception_template = """
{% extends "layout.html" %}

{% block title %}Internal Server Error{% endblock %}

{% block content %}
<div style="display:flex;align-items:center;justify-content:center;min-height:100vh">
    <div style="max-width: 28rem; width: 100%; padding-left: 1.5rem; padding-right: 1.5rem; padding-top: 3rem; padding-bottom: 3rem; border-radius: 0.5rem; ">
        <div style="display:flex;align-items:center;justify-content:center;flex-direction:column">
            <div style="width:60px;">
                <svg fill="#7b7b7b" version="1.1" id="Capa_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 492.426 492.426" xml:space="preserve">
                    <g>
                        <g>
                        <g>
                            <path d="M485.013,383.313l-191.9-328.3c-9.8-16.8-27.4-26.8-46.9-26.8s-37,10-46.9,26.8l-191.9,328.3c-9.8,16.8-9.9,36.9-0.2,53.7c9.8,17,27.4,27.2,47.1,27.2h383.8c19.7,0,37.3-10.2,47.1-27.2C494.913,420.213,494.813,400.113,485.013,383.313z M441.413,411.913c-0.7,1.2-1.8,1.8-3.3,1.8h-383.8c-1.5,0-2.6-0.6-3.3-1.8c-0.9-1.5-0.3-2.6,0-3.1l191.9-328.3c0.7-1.2,1.8-1.8,3.3-1.8s2.6,0.6,3.3,1.8l191.9,328.3C441.713,409.313,442.313,410.413,441.413,411.913z"/>
                        </g>
                        <polygon points="264.013,330.213 228.413,330.213 223.413,165.613 269.013,165.613"/>
                        <rect x="228.513" y="350.113" width="35.4" height="35.4"/>
                        </g>
                    </g>
                </svg>
            </div>
            <h1 style="font-size: 1.875rem; line-height: 2.25rem; font-weight: 700; color: #1F2937; margin-top: 1rem;">Internal Server Error</h1>
            <p style="color: #4B5563; margin-top: 0.5rem; text-align: center;">
                Oops, something went wrong on our end. Please try again later or contact support if the issue persists.
            </p>
        </div>
    </div>
</div>
{% endblock %}

"""

def exception(bridge):
    def handle_exception(e):
        # handles all the exception except 404
        msg = "Unable to process your request"
        errorName = "Unknown Error"
        try:
            findString = f"{e.name}:"
            msgStartsOn = str(e).index(findString)
            msg = str(e)[len(findString)+msgStartsOn:]
            errorName = e.name
        except Exception as err:
            pass

        tb_str = ''.join(traceback.format_tb(e.__traceback__))
        response = {
            "error": errorName + ":" + msg,
            "exception_type": errorName,
            "traceback": tb_str
        }
        print(response["error"])
        print(f"Traceback: {response['traceback']}")
        if os.environ.get("DEBUG") == "True":
        # if False:
            return render_template_string(exception_template_debug,error=True,msg={response["error"]},stack=response['traceback'],name={response['exception_type']}),e.code
        else:
            if isinstance(e, BadRequest):
                return render_template_string(bad_request_exception_template,error=True),e.code
            if isinstance(e, InternalServerError):
                return render_template_string(internal_server_exception_template,error=True),e.code
            return render_template_string(exception_template,error=True,msg=msg,name=errorName),e.code
    return handle_exception