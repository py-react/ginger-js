import os
from flask import render_template,request
from gingerjs.SSR import ssr

not_found_template = """
{% extends "layout.html" %}

{% block title %}Not Found{% endblock %}

{% block content %}
<div style="height:100vh;" class="flex items-center justify-center bg-white dark:bg-gray-950 px-4 md:px-6">
    <div class="max-w-md text-center space-y-4">
        <h1 style="font-size: 8rem;line-height: 1;color: rgb(17 24 39);" class="font-bold text-gray-900 dark:text-gray-50">404</h1>
        <p style="font-size: 1.125rem;color: rgb(107 114 128)" class="dark:text-gray-400">
            Oops, the page you are looking for could not be found.
        </p>
    </div>
</div>
{% endblock %}

"""

def not_found(bridge):
    def view_func(*args,**kwargs):
        props = {}
        props["location"] = {}
        props['location']["path"] = request.path
        props['location']['query'] = str(request.query_string,"utf-8")
        toRender = ssr(bridge,props)
        return render_template("index.html",react_context=toRender,react_props=props),404
        # return render_template_string(not_found_template,error=True),404
    return view_func