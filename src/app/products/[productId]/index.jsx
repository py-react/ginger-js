"use client";
import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

function Products() {
  const { productId } = useParams();
  const [data, setData] = useState(null);

  useEffect(() => {
    fetch(`https://dummyjson.com/products/${productId}`)
      .then((response) => response.json())
      .then((data) => setData(data))
      .catch((error) => console.error("Error fetching data:", error));
  }, []);

  return (
    <>
      {data && (
        <>
          <h1>Prodcut</h1>
          <div className="flex flex-wrap" style={{ gap: "4px" }}>
            <div className="p-4 w-[400px] h-[200px] border rounded">
              <p>{data.id}</p>
              <p>{data.title}</p>
              <p>{data.price}</p>
              <p>{data.description}</p>
              <p>{data.discountPercentage}</p>
              <p>{data.rating}</p>
            </div>
          </div>
        </>
      )}
    </>
  );
}

export default Products;
