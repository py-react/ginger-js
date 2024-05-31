# A Truly Full-Stack Development Experience with Python and React

Unlike typical setups where Node.js serves as the backend for frontend applications, this project leverages Python to deliver a comprehensive full-stack solution.

### Install GingerJS

#### Python Environment and Requirements
Create a virtual environment to manage dependencies locally:
```shell
virtualenv env
```
Activate the virtual environment:
```shell
source env/bin/activate
```
Alternatively:

```shell
. env/bin/activate
```


Now, you need to install GingerJS using `pip`. Open your terminal or command prompt and run the following command:

```bash
pip install gingerjs
```

### Create your app

```bash
gingerjs create-app
```

### Run server

```bash
gingerjs runserver
```


The application will run on port 5001 by default. If port 5000 is already in use, you can change the port in main.py:
If 5000 is already in use, You can change the default port by adding port in main.py 
```python
app.run(debug=True, host="0.0.0.0", port=<PORT>)
```

## Main Features
Some of the main py-react features include:

Feature | Description
--- | --- 
Routing | A file-system based router built on top of Flask and Server Components that supports layouts, nested routing, loading states, and more. 
Rendering | Client-side and Server-side Rendering with Client and Server Components. Further optimized with Static and Dynamic Rendering on the server with py-react.
Styling | Support for your preferred styling methods, including CSS Modules, Tailwind CSS, and CSS-in-JS

## Pre-Requisite Knowledge
Although our docs are designed to be beginner-friendly, we need to establish a baseline so that the docs can stay focused on py-react functionality. We'll make sure to provide links to relevant documentation whenever we introduce a new concept.

To get the most out of our docs, it's recommended that you have a basic understanding of Flask,HTML, CSS, and React. If you need to brush up on your React skills, check out this [React Foundations Course](https://nextjs.org/learn/react-foundations) and [FLask](https://flask.palletsprojects.com/en/3.0.x/), which will introduce you to the fundamentals.


## Creating your First Page

### Layouts
A layout is UI that is shared between multiple routes. On navigation, layouts preserve state, remain interactive, and do not re-render. Layouts can also be nested.

You can define a layout by default exporting a React component from a layout.jsx file. The component will be populated with a child layout (if it exists) or a page during rendering.
```jsx
import React from "react";
import Header from "../components/header";
import { Outlet } from "react-router-dom";

const Layout = ({ children }) => {
  return (
    <div className="p-4">
      <Header />
      <Outlet />
    </div>
  );
};

export default Layout;

```

For example, the layout will be shared with the /dashboard and /dashboard/settings pages:
![NextJs layout example image](https://nextjs.org/_next/image?url=%2Fdocs%2Flight%2Fnested-layout.png&w=3840&q=75)

If you were to combine the two layouts above, the root layout (app/layout.jsx) would wrap the dashboard layout (app/dashboard/layout.jsx), which would wrap route segments inside app/dashboard/*.

The two layouts would be nested as such:
![NextJs Multi layout example image](https://nextjs.org/_next/image?url=%2Fdocs%2Flight%2Fnested-layouts-ui.png&w=3840&q=75)

## Linking and Navigating
There are Three ways to navigate between routes in py-react:

- Using the Link Component
- Using the useRouter hook
- Using the native History API

This page will go through how to use each of these options, and dive deeper into how navigation works.

## Dynamic Routes
When you don't know the exact segment names ahead of time and want to create routes from dynamic data, you can use Dynamic Segments that are filled in at request time.

### Convention
A Dynamic Segment can be created by wrapping a folder's name in square brackets: [folderName]. For example, [id] or [slug].

You can use useParam hook to get the values in component/pages
For ecample if your folder structure looks like src/app/products/[productId]/index.jsx
```jsx
import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

function Product() {
  const { productId } = useParams();
  return (
    <>
      {productId}
    </>
  );
}

export default Product;

```

## Server-Side Props

In a Python environment, you can fetch data, interact with the database, and pass the data to your page.

### Convention

The server logic is placed alongside `index.jsx` or `layout.jsx` within the same folder and is named `index.py`.

### Example
#### Server Example
Path Example : src/app/products/[productId]/index.py
```python
from gingerjs.SSR.ssr import ssr
import requests

def index(request,productId):
    api_url = f'https://dummyjson.com/products/{productId}'  # Replace this with the URL of the API you want to fetch data from
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()
        return {"product":data}
    return {"product":{"error":{"message":"Something went wrong! Please try again"}}}

```
#### Middleware Example
Path Example : src/app/products/[productId]/middleware.py
```python
def middleware(request,abort):
    token = request.headers.get('X-Auth-Token')
    if token != 'secret-token':
      return abort(401,{"error":"No Auth"})
    return

```

#### Component Example
Path Example : src/app/products/[productId]/index.jsx
```jsx
import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

function Products({serverProps:{product}}) {
  return (
    <>
      {JSON.stringify(product)}
    </>
  );
}

export default Products;

```
#### Api Example
Path Example : src/app/api/product/[id]index.py
```python

def index(request,id):
    data = {}
    for key,value in request.args.items():
        data[key] = value
    return {"query":data,"id":id}

```

Enjoy your full-stack development experience with Python and React!



<!-- Write a better build process -->
## Building this project locally

```bash
python setup.py sdist bdist_wheel
```

To install built package
```bash
pip install absolute/relative/path/to/dist/gingerjs-0.0.1-py3-none-any.whl
```
