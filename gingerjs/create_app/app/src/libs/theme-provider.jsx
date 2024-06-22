import * as React from "react"
import { ThemeProvider as GingerThemesProvider } from "next-themes"

export function ThemeProvider({ children, ...props }) {
  return <GingerThemesProvider {...props}>{children}</GingerThemesProvider>
}
