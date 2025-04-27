import React from 'react'
import { Outlet } from 'react-router-dom'
import { ThemeProvider } from "src/libs/theme-provider"

function Layout() {
  return (
    <ThemeProvider attribute="class" defaultTheme="dark" enableSystem>
      <div className="dark:bg-gray-800 dark:text-white">
        <Outlet />
      </div>
    </ThemeProvider>
  );
}

export default Layout