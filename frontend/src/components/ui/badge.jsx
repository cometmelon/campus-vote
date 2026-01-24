import * as React from "react"
import { cn } from "@/lib/utils"

const badgeVariants = {
    default: "bg-primary text-white hover:bg-primary/90",
    secondary: "bg-gray-100 text-gray-800 hover:bg-gray-200",
    destructive: "bg-red-100 text-red-800 hover:bg-red-200",
    outline: "border border-gray-300 bg-white text-gray-700",
    planned: "bg-yellow-100 text-yellow-800 border-0",
    active: "bg-green-100 text-green-800 border-0",
    finished: "bg-gray-100 text-gray-800 border-0",
}

function Badge({
    className,
    variant = "default",
    ...props
}) {
    const variantClass = badgeVariants[variant] || badgeVariants.default;

    return (
        <div
            className={cn(
                "inline-flex items-center rounded-md px-2.5 py-0.5 text-xs font-medium transition-colors",
                variantClass,
                className
            )}
            {...props}
        />
    )
}

export { Badge, badgeVariants }
