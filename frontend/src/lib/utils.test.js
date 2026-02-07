import { describe, it, expect } from 'vitest'
import { cn } from './utils'

describe('cn', () => {
    it('should merge class names correctly', () => {
        expect(cn('class1', 'class2')).toBe('class1 class2')
    })

    it('should handle conditional classes', () => {
        expect(cn('class1', { class2: true, class3: false })).toBe('class1 class2')
    })

    it('should handle arrays of classes', () => {
        expect(cn(['class1', 'class2'])).toBe('class1 class2')
    })

    it('should handle mixed inputs', () => {
        expect(cn('class1', ['class2', { class3: true }])).toBe('class1 class2 class3')
    })

    it('should handle tailwind conflict resolution', () => {
        expect(cn('p-4', 'p-2')).toBe('p-2')
        expect(cn('text-red-500', 'text-blue-500')).toBe('text-blue-500')
    })

    it('should handle complex tailwind conflicts', () => {
        expect(cn('px-2 py-1', 'p-4')).toBe('p-4')
    })

    it('should handle falsy values', () => {
        expect(cn('class1', null, undefined, false, 'class2')).toBe('class1 class2')
    })
})
