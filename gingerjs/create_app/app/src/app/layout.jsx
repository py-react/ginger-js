import React from 'react'
import { Outlet } from 'react-router-dom'

function Layout() {
  return (
    <div className='p-0'><Outlet /></div>
  )
}

export default Layout