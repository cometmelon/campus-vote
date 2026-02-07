import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import * as React from 'react';
import { Button } from './button';

describe('Button', () => {
    it('renders correctly with default props', () => {
        render(<Button>Click me</Button>);
        const button = screen.getByRole('button', { name: /click me/i });
        expect(button).toBeInTheDocument();
        expect(button).toHaveClass('bg-primary');
        expect(button).toHaveClass('text-primary-foreground');
    });

    it('renders with different variants', () => {
        const variants = [
            { name: 'destructive', class: 'bg-destructive' },
            { name: 'outline', class: 'border-input' },
            { name: 'secondary', class: 'bg-secondary' },
            { name: 'ghost', class: 'hover:bg-accent' },
            { name: 'link', class: 'text-primary' },
        ];

        variants.forEach(({ name, class: className }) => {
            const { unmount } = render(<Button variant={name}>{name}</Button>);
            const button = screen.getByRole('button', { name: new RegExp(name, 'i') });
            expect(button).toHaveClass(className);
            unmount();
        });
    });

    it('renders with different sizes', () => {
        const sizes = [
            { name: 'sm', class: 'h-9' },
            { name: 'lg', class: 'h-11' },
            { name: 'icon', class: 'h-10 w-10' },
        ];

        sizes.forEach(({ name, class: className }) => {
            const { unmount } = render(<Button size={name}>Size {name}</Button>);
            const button = screen.getByRole('button', { name: new RegExp(`size ${name}`, 'i') });
            expect(button).toHaveClass(className);
            unmount();
        });
    });

    it('renders as a child component when asChild is true', () => {
        render(
            <Button asChild>
                <a href="/link">Link Button</a>
            </Button>
        );
        const link = screen.getByRole('link', { name: /link button/i });
        expect(link).toBeInTheDocument();
        expect(link).toHaveAttribute('href', '/link');
        expect(link).toHaveClass('inline-flex'); // Should still have button classes
    });

    it('forwards ref correctly', () => {
        const ref = React.createRef();
        render(<Button ref={ref}>Button with Ref</Button>);
        expect(ref.current).toBeInstanceOf(HTMLButtonElement);
    });

    it('handles click events', async () => {
        const handleClick = vi.fn();
        const user = userEvent.setup();
        render(<Button onClick={handleClick}>Clickable</Button>);
        const button = screen.getByRole('button', { name: /clickable/i });

        await user.click(button);
        expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('merges custom classes', () => {
        render(<Button className="custom-class">Custom Class</Button>);
        const button = screen.getByRole('button', { name: /custom class/i });
        expect(button).toHaveClass('custom-class');
        expect(button).toHaveClass('inline-flex'); // Default classes should be preserved
    });

    it('can be disabled', () => {
        render(<Button disabled>Disabled</Button>);
        const button = screen.getByRole('button', { name: /disabled/i });
        expect(button).toBeDisabled();
        expect(button).toHaveClass('disabled:pointer-events-none');
    });
});
