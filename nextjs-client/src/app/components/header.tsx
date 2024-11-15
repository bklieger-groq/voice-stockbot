import * as React from 'react'
import Link from 'next/link'
import Image from 'next/image'

import { cn } from '../utils/utils'
import { Button, buttonVariants } from './ui/button'
import {
  IconGitHub,
  IconSeparator
} from './ui/icons'

export function Header() {
  return (
    <header className="sticky top-0 z-50 flex items-center justify-between w-full h-16 px-4 border-b shrink-0 bg-gradient-to-b from-background/10 via-background/50 to-background/80 backdrop-blur-xl">
      <div className="flex items-center">
        <Link href="https://wow.groq.com/groq-labs/" rel="nofollow">
        <Image
          src="/groqlabs-logo-black.png"
          alt="GroqLabs Logo"
          width={100}
          height={30}
        />
      </Link>

      <div className="flex items-center font-semibold">
        <IconSeparator className="size-6 text-muted-foreground/50" />
        <a href="/">StockBot</a>
        <span className="ml-2 px-2 py-0.5 text-xs font-medium rounded-md border border-orange-600 bg-orange-100 text-orange-700">
          BETA
        </span>
        <IconSeparator className="size-6 text-muted-foreground/50" />
        <a
          href="/new"
          rel="noopener noreferrer"
          className={cn(buttonVariants({ variant: 'ghost' }))}
          style={{ borderRadius: 0, color: '#F55036', padding: '4px' }}
        >
          <span className="flex">Start New Chat</span>
        </a>
      </div>
      </div>
      <div className="flex items-center justify-end space-x-2">
        <a
          target="_blank"
          href="https://github.com/bklieger-groq/voice-stockbot/"
          rel="noopener noreferrer"
          className={cn(buttonVariants({ variant: 'outline' }))}
          style={{ borderRadius: 0 }}
        >
          <IconGitHub />
          <span className="hidden ml-2 md:flex">GitHub</span>
        </a>
      </div>
    </header>
  )
}