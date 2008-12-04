// Copyright (c) 2008 Christopher Hall.  All rights reserved.
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions
// are met:
// 1. Redistributions of source code must retain the above copyright
//    notice, this list of conditions and the following disclaimer.
// 2. Redistributions in binary form must reproduce the above copyright
//    notice, this list of conditions and the following disclaimer in the
//    documentation and/or other materials provided with the distribution.
// 3. The name of the author may not be used to endorse or promote products
//    derived from this software without specific prior written permission.
//
// THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
// IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
// OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
// IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
// INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
// NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
// DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
// THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
// (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
// THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

#include <sys/cdefs.h>
#include <sys/types.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>


// A simple emulation of the FreeBSD libc routine fgetln
// that cn be compiled on systems that lack this routine

char *fgetln(FILE *stream, size_t *len)
{
  char c;
  size_t n = fread(&c, sizeof(c), 1, stream);
  if (1 != n)
  {
    *len = 0;
    return(NULL);
  }

  size_t BufferLength = 256;
  char *buffer = malloc(BufferLength);
  size_t l = 0;
  char *p = buffer;
  while (1 == n)
  {
    *p++ = c;
    ++l;
    if ('\n' == c)
    {
      break;
    }
    n = fread(&c, sizeof(c), 1, stream);
    if (0 != n && l >= BufferLength)
    {
      BufferLength *= 2;
      buffer = realloc(buffer, BufferLength);
      p = &buffer[l];
    }
  }

  *len = l;
  return(buffer);
}
