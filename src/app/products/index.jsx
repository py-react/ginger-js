import React from "react";

function Products({ serverProps: { products } }) {
  return (
    <>
      <h1>Prodcuts</h1>
      <div className="flex flex-wrap" style={{ gap: "4px" }}>
        {products?.map((product) => (
          <div
            key={product.title + "_" + product.id}
            className="p-4 w-[200px] h-[150px] border rounded"
          >
            <p>{product.id}</p>
            <p>{product.title}</p>
          </div>
        ))}
      </div>
    </>
  );
}

export default Products;
