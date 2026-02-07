import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { Button } from './button'

describe('Button', () => {
    it('renders with default props', () => {
        render(<Button>Click me</Button>)
        const button = screen.getByRole('button', { name: /click me/i })
        expect(button).toBeInTheDocument()
        // Check for default variant classes
        expect(button).toHaveClass('bg-primary')
        expect(button).toHaveClass('text-primary-foreground')
    })

    it('applies variant classes correctly', () => {
        const { rerender } = render(<Button variant="destructive">Destructive</Button>)
        expect(screen.getByRole('button')).toHaveClass('bg-destructive')

        rerender(<Button variant="outline">Outline</Button>)
        expect(screen.getByRole('button')).toHaveClass('border')
        expect(screen.getByRole('button')).toHaveClass('border-input')

        rerender(<Button variant="secondary">Secondary</Button>)
        expect(screen.getByRole('button')).toHaveClass('bg-secondary')

        rerender(<Button variant="ghost">Ghost</Button>)
        expect(screen.getByRole('button')).toHaveClass('hover:bg-accent')

        rerender(<Button variant="link">Link</Button>)
        expect(screen.getByRole('button')).toHaveClass('text-primary')
        expect(screen.getByRole('button')).toHaveClass('underline-offset-4')
    })

    it('applies size classes correctly', () => {
        const { rerender } = render(<Button size="sm">Small</Button>)
        expect(screen.getByRole('button')).toHaveClass('h-9')
        expect(screen.getByRole('button')).toHaveClass('px-3')

        rerender(<Button size="lg">Large</Button>)
        expect(screen.getByRole('button')).toHaveClass('h-11')
        expect(screen.getByRole('button')).toHaveClass('px-8')

        rerender(<Button size="icon">Icon</Button>)
        expect(screen.getByRole('button')).toHaveClass('h-10')
        expect(screen.getByRole('button')).toHaveClass('w-10')
    })

    it('handles onClick events', () => {
        const handleClick = vi.fn()
        render(<Button onClick={handleClick}>Click me</Button>)
        fireEvent.click(screen.getByRole('button'))
        expect(handleClick).toHaveBeenCalledTimes(1)
    })

    it('can be disabled', () => {
        render(<Button disabled>Disabled</Button>)
        expect(screen.getByRole('button')).toBeDisabled()
        expect(screen.getByRole('button')).toHaveClass('disabled:pointer-events-none')
        expect(screen.getByRole('button')).toHaveClass('disabled:opacity-50')
    })

    it('merges custom className', () => {
        render(<Button className="custom-class">Custom</Button>)
        expect(screen.getByRole('button')).toHaveClass('custom-class')
        expect(screen.getByRole('button')).toHaveClass('bg-primary') // Should preserve default classes
    })

    it('renders as child component when asChild is true', () => {
        render(
            <Button asChild>
                <a href="/link">Link Button</a>
            </Button>
        )
        const link = screen.getByRole('link', { name: /link button/i })
        expect(link).toBeInTheDocument()
        expect(link).toHaveAttribute('href', '/link')
        expect(link).toHaveClass('bg-primary') // Should still have button classes
    })
})
