import React from "react";

function Loading() {
  return (
    <div className="w-full h-[90vh] flex items-center justify-center bg-opacity-50 z-50">
      <div className="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-gray-900"></div>
    </div>
  );
}

export default Loading;
